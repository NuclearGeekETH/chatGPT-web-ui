import gradio as gr

def edit_image(im):
    return [im["background"].size, im["background"], im["layers"][0], im["composite"]]

with gr.Blocks() as demo:
    # Image Editor
    with gr.Tab("ImageEditor"):
        im = gr.ImageEditor(
            type="pil"
        )

        with gr.Group():
            with gr.Row():
                text_out = gr.Textbox(label="Edited Size")
            with gr.Row():
                im_out_1 = gr.Image(type="pil", label="Background")
                im_out_2 = gr.Image(type="pil", label="Layer 0")
                im_out_3 = gr.Image(type="pil", label="Composite")

        im.change(edit_image, outputs=[text_out, im_out_1, im_out_2, im_out_3], inputs=im)

demo.launch()
