import gradio as gr
from gradio_terminal import Terminal

with gr.Blocks() as demo:
    gr.Markdown("# Terminal Theme and Font Size Demo")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Dark Theme (Default)")
            Terminal(port=5000, theme="dark")

        with gr.Column():
            gr.Markdown("### Light Theme, Large Font")
            Terminal(port=5001, theme="light", xterm_options={"fontSize": 16})

demo.launch()
