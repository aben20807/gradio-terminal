"""
Gradio Terminal - A terminal component for Gradio.

This package provides a fully functional terminal that can be embedded
in Gradio applications. It uses xterm.js on the frontend and a PTY
(pseudo-terminal) on the backend to provide a real shell experience.

Example usage in Blocks:
    import gradio as gr
    from gradio_terminal import Terminal

    with gr.Blocks() as demo:
        gr.Markdown("# My App with Terminal")
        with gr.Row():
            with gr.Column():
                gr.Markdown("Some content here")
            with gr.Column():
                terminal = Terminal()

    demo.launch()

Or for quick usage:
    from gradio_terminal import launch_terminal

    launch_terminal()
"""

from .terminal import (
    Terminal,
    TerminalServer,
    create_terminal,
    create_terminal_demo,
    launch_terminal,
)

__version__ = "0.1.0"
__all__ = [
    "Terminal",
    "TerminalServer",
    "create_terminal",
    "create_terminal_demo",
    "launch_terminal",
]
