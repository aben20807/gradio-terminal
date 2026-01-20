# Gradio Terminal

A Gradio component that provides a fully functional terminal in your browser. This package uses xterm.js on the frontend and a PTY on the backend to provide a real shell experience.

![Gradio Terminal](https://github.com/user-attachments/assets/8a4cc81a-07a4-4c56-a008-bd438eae50de)

## Installation

```bash
pip install gradio-terminal
```

## Quick Start

### Simple Usage

```python
import gradio as gr
from gradio_terminal import Terminal
demo = gr.Blocks()
with demo:
    terminal = Terminal()
demo.launch()
```

## API Reference

`launch_terminal(port=5000, host="127.0.0.1", command="bash", share=False, **launch_kwargs)`

Launch a standalone Gradio app with a terminal.

`create_terminal_demo(port=5000, host="127.0.0.1", command="bash", height=400)`

Create a Gradio Blocks demo with an embedded terminal.

`TerminalServer(port=5000, host="127.0.0.1", command="bash")`

Low-level terminal server for custom integrations.

- `start()`: Start the server and return the URL
- `get_url()`: Get the terminal server URL
- `stop()`: Stop the terminal server

## Requirements

- Python 3.8+
- Linux
- Dependencies: gradio, flask, flask-socketio

## Security Notice

This component provides shell access to your server. Use only in trusted environments.

## License

This project is licensed under the Apache-2.0 License.

## Acknowledgments

- [pyxtermjs](https://github.com/cs01/pyxtermjs) - Inspiration for the terminal implementation
- [xterm.js](https://xtermjs.org/) - Terminal emulator for the browser
- [Gradio](https://gradio.app/) - The awesome ML demo framework