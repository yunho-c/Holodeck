"""
NOTE: for this script to work, monkey-patch lines 479-481 of gradio.processing_utils.py
      by commenting the raise Error(...) part, replacing it with pass, in _in_cache() function defn.

why the hell does gradio force using caches. fuck gradio.
"""

import os
import glob
import subprocess
from pathlib import Path

import gradio as gr
import open_clip
from sentence_transformers import SentenceTransformer

from ai2holodeck.generation.objaverse_retriever import ObjathorRetriever
from objaverse_downloader import download_assets


def main():
    # clip_model, _, clip_preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
    (
        clip_model,
        _,
        clip_preprocess,
    ) = open_clip.create_model_and_transforms(
        "ViT-L-14",
        pretrained="laion2b_s32b_b82k",
    )  # match
    # clip_tokenizer = open_clip.get_tokenizer('ViT-B-32')
    clip_tokenizer = open_clip.get_tokenizer("ViT-L-14")  # match
    # sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
    sbert_model = SentenceTransformer("all-mpnet-base-v2")  # match
    retriever = ObjathorRetriever(
        clip_model=clip_model,
        clip_preprocess=clip_preprocess,
        clip_tokenizer=clip_tokenizer,
        sbert_model=sbert_model,
        retrieval_threshold=30,
    )

    retriever = ObjathorRetriever(
        clip_model=clip_model,
        clip_preprocess=clip_preprocess,
        clip_tokenizer=clip_tokenizer,
        sbert_model=sbert_model,
        retrieval_threshold=30,
    )

    def search(query, threshold, use_text, size_x, size_y, size_z):
        retriever.use_text = use_text
        results = retriever.retrieve([query], threshold=threshold)
        if size_x > 0 and size_y > 0 and size_z > 0:
            results = retriever.compute_size_difference(
                (size_x, size_y, size_z), results
            )
        asset_ids = [result[0] for result in results]
        assets = download_assets(asset_ids)  # downloads

        # HACK: this is actually unfathomably hacky but whatever... it freaking works.
        subprocess.run(
            [
                "py",
                Path(
                    "~/Documents/GitHub/scripts/generate_thumbnails_for_glb.py"
                ).expanduser(),
                Path("~/.objaverse").expanduser(),
            ]
        )
        image_paths = []
        for i, (id, path) in enumerate(assets.items()):
            image_path = Path(path.replace(".glb", ".png")).expanduser()
            image_paths.append(image_path)

        return image_paths

    def select(select_data: gr.SelectData):
        # return select_data.value
        path = select_data.value["image"]["path"].replace(".png", ".glb")
        return path

    def png_to_glb(fn):  # NOTE: doesn't seem to ever get called
        if fn is None:
            return
        else:
            return fn.replace(".png", ".glb")

    # NOTE: gr.set_static_paths() just doesn't seem to work.
    # gr.set_static_paths(paths=[str(Path.home() / ".objaverse")])
    # gr.set_static_paths(os.walk(str(Path.home() / ".objaverse")))
    # paths = glob.glob(str(Path.home() / ".objaverse/**/"), recursive=True)
    paths = [d for d in (Path.home() / ".objaverse").glob("**/") if d.is_dir()]
    # print(paths)  # HACK
    gr.set_static_paths(paths)
    # NOTE: bruh... the fucking order mattered. fuck me and my stupid ass.
    #       wait what the fuck, that wasn't it. what the actual fuck...
    #       or maybe it has to be added to both static_paths and allowed_paths at the same time?

    # it's working. it's been working the entire time. kms

    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                query_input = gr.Textbox(label="Query")
                threshold_input = gr.Slider(
                    minimum=20, maximum=35, value=30, label="Threshold"
                )
                use_text_input = gr.Checkbox(value=True, label="Use Text")
                with gr.Row():
                    size_x_input = gr.Number(label="Size X (cm)", value=0)
                    size_y_input = gr.Number(label="Size Y (cm)", value=0)
                    size_z_input = gr.Number(label="Size Z (cm)", value=0)
                search_button = gr.Button("Search")
                download_button = gr.Button("Download Top Result")
            with gr.Column():
                output_gallery = gr.Gallery(label="Results")
                model_output = gr.Model3D(
                    value=png_to_glb,
                    label="3D Model",
                    inputs=output_gallery,
                    interactive=False,
                )
                select_output = gr.Textbox(
                    value=png_to_glb, inputs=output_gallery, label="Select Data"
                )

        # output_gallery.select(select, None, select_output)
        output_gallery.select(select, None, model_output)

        search_button.click(
            fn=search,
            inputs=[
                query_input,
                threshold_input,
                use_text_input,
                size_x_input,
                size_y_input,
                size_z_input,
            ],
            outputs=output_gallery,
        )

    demo.launch(allowed_paths=[str(Path.home() / ".objaverse")] + paths)
    demo.launch()
    # demo.launch(max_threads=1)


if __name__ == "__main__":
    main()
