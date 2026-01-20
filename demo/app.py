"""
Demo application for gradio_terminal.

This demonstrates how to use the Terminal component in a Gradio Blocks app.
The Terminal component can be used just like any other Gradio component
within Blocks, Rows, Columns, Tabs, etc.

IMPORTANT: If accessing remotely via SSH tunneling, you need to tunnel BOTH ports:
    ssh -L 7860:localhost:7860 -L 5000:localhost:5000 user@remote
"""

import gradio as gr

from gradio_terminal import Terminal

# Configuration
TERMINAL_PORT = 5000  # Port for the terminal WebSocket server
GRADIO_PORT = 7860  # Port for the Gradio web server


def build_demo():
    """
    Launch the demo showing how to use Terminal as a component.

    This example shows the Terminal component used within:
    - gr.Blocks context
    - gr.Row and gr.Column for layout
    - Alongside other Gradio components
    """
    with gr.Blocks(title="Gradio Terminal Demo") as demo:
        gr.Markdown(f"""
            # Gradio Terminal Demo

            This demo shows how to use the `Terminal` component within a Gradio Blocks app.
            The terminal is a fully functional shell that you can use to run commands.

            **Remote Access:** If using SSH tunneling, tunnel both ports:
            ```
            ssh -L {GRADIO_PORT}:localhost:{GRADIO_PORT} -L {TERMINAL_PORT}:localhost:{TERMINAL_PORT} user@remote
            ```
            """)

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("""
                    ## About This Component

                    The `Terminal` component embeds a fully interactive terminal
                    in your Gradio application.

                    **Features:**
                    - Full PTY support (pseudo-terminal)
                    - ANSI colors and cursor control
                    - Resizable terminal window
                    - Works with any shell (bash, zsh, etc.)

                    **Usage:**
                    ```python
                    import gradio as gr
                    from gradio_terminal import Terminal

                    with gr.Blocks() as demo:
                        terminal = Terminal()

                    demo.launch()
                    ```
                    """)

            with gr.Column(scale=2):
                gr.Markdown("### Interactive Terminal")
                # This is how you add a Terminal component!
                Terminal(
                    port=TERMINAL_PORT,
                    host="0.0.0.0",  # Allow connections from any host
                    command="bash",
                    height=400,
                    allow_sudo=False,
                    blacklist_commands=["passwd", "su"],
                )

        gr.Markdown(f"""
            ---
            **Tips:**
            - Try running `htop`, `vim`, or any other terminal application!
            - Terminal server is running on port **{TERMINAL_PORT}**
            - Secure version: Disable `sudo` and blacklist sensitive commands, e.g., `passwd`, `su`.
            """)

    return demo


demo = build_demo()


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=GRADIO_PORT,
        share=False,
        theme=gr.themes.Soft(),
    )
