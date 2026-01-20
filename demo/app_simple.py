import gradio as gr

from gradio_terminal import Terminal

demo = gr.Blocks()
with demo:
    terminal = Terminal()
demo.launch()
