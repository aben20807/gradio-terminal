# Gradio Terminal

[![PyPI](https://img.shields.io/pypi/v/gradio-terminal?color=blue&style=flat&logo=pypi)](https://pypi.org/project/gradio-terminal/) [![PyPI Downloads](https://static.pepy.tech/badge/gradio-terminal)](https://pepy.tech/projects/gradio-terminal) [![GitHub license](https://img.shields.io/github/license/aben20807/gradio-terminal?color=blue)](LICENSE) [![Coding style](https://img.shields.io/badge/code%20style-black-1183C3.svg)](https://github.com/psf/black)

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

### Secure Terminal (No Sudo)

```python
import gradio as gr
from gradio_terminal import Terminal
demo = gr.Blocks()
with demo:
    terminal = Terminal(allow_sudo=False)  # Block sudo commands
demo.launch()
```

## API Reference

| Function | Parameters | Description |
|----------|------------|-------------|
| `launch_terminal()` | `port=5000`, `host="127.0.0.1"`, `command="bash"`, `share=False`, `allow_sudo=True`, `**launch_kwargs` | Launch a standalone Gradio app with a terminal. |
| `create_terminal_demo()` | `port=5000`, `host="127.0.0.1"`, `command="bash"`, `height=400`, `allow_sudo=True` | Create a Gradio Blocks demo with an embedded terminal. |
| `Terminal()` | `port=5000`, `host="127.0.0.1"`, `command="bash"`, `height=400`, `label=None`, `visible=True`, `elem_id=None`, `elem_classes=None`, `allow_sudo=True` | Create a terminal component for Gradio Blocks. |
| `TerminalServer()` | `port=5000`, `host="127.0.0.1"`, `command="bash"` | Low-level terminal server for custom integrations. |

### TerminalServer Methods

| Method | Description |
|--------|-------------|
| `start()` | Start the server and return the URL |
| `get_url()` | Get the terminal server URL |
| `stop()` | Stop the terminal server |

### Notes

- `allow_sudo`: Whether to allow sudo commands (default: True). When False, sudo commands are blocked with an error message.

## Security

This component provides shell access to your server. Use the `allow_sudo=False` parameter to block sudo commands for enhanced security:

```python
terminal = Terminal(allow_sudo=False)
```

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