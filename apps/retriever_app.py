from pathlib import Path

import gradio as gr
import open_clip
from sentence_transformers import SentenceTransformer
import pyrender
import trimesh
import numpy as np
from PIL import Image
import os

from ai2holodeck.generation.objaverse_retriever import ObjathorRetriever
from apps.objaverse_downloader import download_assets


def render_glb_to_jpg(glb_path, jpg_path):
    """
    Renders a .glb file to a .jpg image.
    """
    if not os.path.exists(os.path.dirname(jpg_path)):
        os.makedirs(os.path.dirname(jpg_path))

    # Load the scene from the .glb file
    try:
        trimesh_mesh = trimesh.load_mesh(glb_path)
    except Exception as e:
        print(f"Error loading {glb_path}: {e}")
        return None

    # Create a pyrender scene
    mesh = pyrender.Mesh.from_trimesh(trimesh_mesh)
    scene = pyrender.Scene()
    scene.add(mesh)

    # Add a camera
    camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.0)

    if scene.bounds is None or not np.all(np.isfinite(scene.bounds)):
        print(f"Invalid scene bounds for {glb_path}")
        return None

    # camera_pose = scene.camera_transform
    s = np.sqrt(2)/2
    camera_pose = np.array([
        [0.0, -s,   s,   0.3],
        [1.0,  0.0, 0.0, 0.0],
        [0.0,  s,   s,   0.35],
        [0.0,  0.0, 0.0, 1.0],
    ])
    scene.add(camera, pose=camera_pose)

    # Add a light
    light = pyrender.DirectionalLight(color=np.ones(3), intensity=2.0)
    scene.add(light, pose=camera_pose)

    # Render the scene
    r = pyrender.OffscreenRenderer(400, 400)
    color, _ = r.render(scene)
    r.delete()

    # Save the image
    img = Image.fromarray(color)
    img.save(jpg_path)
    return jpg_path


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
        retrieval_threshold=28,
    )

    retriever = ObjathorRetriever(
        clip_model=clip_model,
        clip_preprocess=clip_preprocess,
        clip_tokenizer=clip_tokenizer,
        sbert_model=sbert_model,
        retrieval_threshold=28,
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

        image_paths = []
        for id, path in assets.items():
            image_path = path.replace(".glb", ".jpg")
            render_glb_to_jpg(path, image_path)
            image_paths.append(image_path)

        return image_paths

    def select(select_data: gr.SelectData):
        return select_data.value

    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                query_input = gr.Textbox(label="Query")
                threshold_input = gr.Slider(
                    minimum=20, maximum=35, value=28, label="Threshold"
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
                model_output = gr.Model3D(label="3D Model")
                download_status = gr.Textbox(label="Download Status")
                select_output = gr.Textbox(label="Select Data")

        output_gallery.select(select, None, select_output)

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

        # download_button.click(
        #     fn=download_and_display,
        #     inputs=output_gallery,
        #     outputs=[model_output, download_status],
        # )

    gr.set_static_paths(paths=[str(Path.home() / ".objaverse"), str(Path.cwd())])
    # demo.launch(allowed_paths=[str(Path.home() / ".objaverse"), str(Path.cwd())])
    demo.launch()


if __name__ == "__main__":
    main()
