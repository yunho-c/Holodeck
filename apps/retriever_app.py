import gradio as gr
from ai2holodeck.generation.objaverse_retriever import ObjathorRetriever
import open_clip
from sentence_transformers import SentenceTransformer


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

    def search(query, threshold, use_text, size_x, size_y, size_z):
        retriever.use_text = use_text
        results = retriever.retrieve([query], threshold=threshold)
        if size_x > 0 and size_y > 0 and size_z > 0:
            results = retriever.compute_size_difference(
                (size_x, size_y, size_z), results
            )
        return [result[0] for result in results]

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
            with gr.Column():
                output_gallery = gr.Gallery(label="Results")

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

    demo.launch()


if __name__ == "__main__":
    main()
