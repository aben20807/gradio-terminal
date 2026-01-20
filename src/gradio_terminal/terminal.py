"""
Gradio Terminal Component using xterm.js and PTY.

This component provides a fully functional terminal in Gradio applications.
Based on pyxtermjs (https://github.com/cs01/pyxtermjs).

IMPORTANT: If using SSH tunneling, you need to tunnel BOTH ports:
- The Gradio port (default 7860)
- The terminal server port (default 5000)

Example SSH command:
  ssh -L 7860:localhost:7860 -L 5000:localhost:5000 user@remote
"""

"""
Include pyxtermjs's MIT license:

MIT License

Copyright (c) 2018 Chad Smith

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import atexit
import fcntl
import logging
import os
import pty
import select
import shlex
import signal
import struct
import subprocess
import termios
import threading
import time

import gradio as gr

logging.getLogger("werkzeug").setLevel(logging.ERROR)

# Global registry to track terminal servers
_terminal_servers: dict[int, "TerminalServer"] = {}


def _cleanup_servers():
    """Clean up all terminal servers on exit."""
    for server in list(_terminal_servers.values()):
        try:
            server.stop()
        except Exception:
            pass


atexit.register(_cleanup_servers)


class TerminalServer:
    """
    A server that manages PTY sessions for terminal access.
    Runs Flask-SocketIO in a background thread.
    """

    def __init__(self, port: int = 5000, host: str = "127.0.0.1", command: str = "bash"):
        self.port = port
        self.host = host
        self.command = command
        self.allow_sudo = True
        self.blacklist_commands = []
        self._running = False
        self._thread = None
        self._app = None
        self._socketio = None

        # Register in global registry
        _terminal_servers[port] = self

    def _create_app(self):
        """Create and configure the Flask app with SocketIO."""
        from flask import Flask, render_template_string
        from flask_socketio import SocketIO

        app = Flask(__name__)
        app.config["SECRET_KEY"] = "gradio-terminal-secret"
        app.config["fd"] = None
        app.config["child_pid"] = None
        app.config["cmd"] = shlex.split(self.command)
        app.config["input_buffer"] = ""
        app.config["allow_sudo"] = self.allow_sudo
        app.config["blacklist_commands"] = self.blacklist_commands

        socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

        def set_winsize(fd, row, col, xpix=0, ypix=0):
            winsize = struct.pack("HHHH", row, col, xpix, ypix)
            fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)

        def read_and_forward_pty_output():
            max_read_bytes = 1024 * 20
            while True:
                socketio.sleep(0.01)
                if app.config["fd"]:
                    timeout_sec = 0
                    try:
                        data_ready, _, _ = select.select([app.config["fd"]], [], [], timeout_sec)
                        if data_ready:
                            output = os.read(app.config["fd"], max_read_bytes).decode(
                                errors="ignore"
                            )
                            socketio.emit("pty-output", {"output": output}, namespace="/pty")
                    except (OSError, ValueError):
                        break

        @app.route("/")
        def index():
            return render_template_string(self._get_terminal_html())

        @socketio.on("pty-input", namespace="/pty")
        def pty_input(data):
            if app.config["fd"]:
                app.config["input_buffer"] += data["input"]

                # Check for command completion (Enter pressed)
                if "\r" in data["input"] or "\n" in data["input"]:
                    line = app.config["input_buffer"].strip()

                    # Check if sudo is used and not allowed
                    if "sudo" in line.split() and not app.config["allow_sudo"]:
                        # Deny the sudo command
                        error_msg = "\r\n\033[31mError: sudo commands are not allowed.\033[0m\r\n"
                        socketio.emit("pty-output", {"output": error_msg}, namespace="/pty")
                        # Clear the buffer and send newline to get a fresh prompt
                        app.config["input_buffer"] = ""
                        os.write(app.config["fd"], b"\x03")  # Send Ctrl+C to cancel
                        return

                    # Check for blacklisted commands
                    words = line.split()
                    for cmd in app.config["blacklist_commands"]:
                        if cmd in words:
                            error_msg = (
                                f"\r\n\033[31mError: '{cmd}' command is not allowed.\033[0m\r\n"
                            )
                            socketio.emit("pty-output", {"output": error_msg}, namespace="/pty")
                            app.config["input_buffer"] = ""
                            os.write(app.config["fd"], b"\x03")  # Send Ctrl+C to cancel
                            return

                    # Reset buffer for next command
                    app.config["input_buffer"] = ""

                # Write input to PTY
                os.write(app.config["fd"], data["input"].encode())

        @socketio.on("resize", namespace="/pty")
        def resize(data):
            if app.config["fd"]:
                set_winsize(app.config["fd"], data["rows"], data["cols"])

        @socketio.on("connect", namespace="/pty")
        def connect():
            if app.config["child_pid"]:
                return

            child_pid, fd = pty.fork()
            if child_pid == 0:
                subprocess.run(app.config["cmd"])
            else:
                app.config["fd"] = fd
                app.config["child_pid"] = child_pid
                set_winsize(fd, 24, 80)
                socketio.start_background_task(target=read_and_forward_pty_output)

        @socketio.on("disconnect", namespace="/pty")
        def disconnect():
            pass

        return app, socketio

    def _get_terminal_html(self) -> str:
        """Return the HTML template for the terminal."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <title>Gradio Terminal</title>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            height: 100%;
            overflow: hidden;
            background-color: #1e1e1e;
        }
        #terminal {
            width: 100%;
            height: 100%;
        }
        #status {
            position: absolute;
            top: 5px;
            right: 10px;
            font-size: 12px;
            font-family: Arial, sans-serif;
            z-index: 1000;
        }
        .connected {
            background-color: #4CAF50;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
        }
        .disconnected {
            background-color: #f44336;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
        }
        .connecting {
            background-color: #ff9800;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
        }
    </style>
    <link rel="stylesheet" href="https://unpkg.com/xterm@4.11.0/css/xterm.css" />
</head>
<body>
    <div id="status"><span class="connecting">connecting...</span></div>
    <div id="terminal"></div>

    <script src="https://unpkg.com/xterm@4.11.0/lib/xterm.js"></script>
    <script src="https://unpkg.com/xterm-addon-fit@0.5.0/lib/xterm-addon-fit.js"></script>
    <script src="https://unpkg.com/xterm-addon-web-links@0.4.0/lib/xterm-addon-web-links.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.min.js"></script>

    <script>
        const term = new Terminal({
            cursorBlink: true,
            macOptionIsMeta: true,
            scrollback: 5000,
            fontSize: 14,
            fontFamily: 'Consolas, Monaco, monospace',
            theme: {
                background: '#1e1e1e',
                foreground: '#d4d4d4',
                cursor: '#d4d4d4',
                cursorAccent: '#1e1e1e',
                selectionBackground: 'rgba(255, 255, 255, 0.3)',
            }
        });

        const fit = new FitAddon.FitAddon();
        term.loadAddon(fit);
        term.loadAddon(new WebLinksAddon.WebLinksAddon());

        term.open(document.getElementById("terminal"));
        fit.fit();

        term.attachCustomKeyEventHandler((e) => {
            if (e.type !== "keydown") return true;
            if (e.ctrlKey && e.shiftKey) {
                const key = e.key.toLowerCase();
                if (key === "v") {
                    navigator.clipboard.readText().then((text) => {
                        term.writeText(text);
                    });
                    return false;
                } else if (key === "c" || key === "x") {
                    const selection = term.getSelection();
                    if (selection) {
                        navigator.clipboard.writeText(selection);
                    }
                    return false;
                }
            }
            return true;
        });

        const socket = io.connect("/pty");
        const status = document.getElementById("status");

        term.onData((data) => {
            socket.emit("pty-input", { input: data });
        });

        socket.on("pty-output", (data) => {
            term.write(data.output);
        });

        socket.on("connect", () => {
            status.innerHTML = '<span class="connected">connected</span>';
            fitToScreen();
        });

        socket.on("disconnect", () => {
            status.innerHTML = '<span class="disconnected">disconnected</span>';
        });

        socket.on("connect_error", (error) => {
            status.innerHTML = '<span class="disconnected">error</span>';
        });

        function fitToScreen() {
            fit.fit();
            const dims = { cols: term.cols, rows: term.rows };
            socket.emit("resize", dims);
        }

        function debounce(func, wait) {
            let timeout;
            return function(...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), wait);
            };
        }

        window.onresize = debounce(fitToScreen, 50);
        setTimeout(fitToScreen, 100);
    </script>
</body>
</html>
"""

    def start(self):
        """Start the terminal server in a background thread."""
        if self._running:
            return self.get_url()

        self._app, self._socketio = self._create_app()

        def run_server():
            self._socketio.run(
                self._app,
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False,
                log_output=False,
            )

        self._thread = threading.Thread(target=run_server, daemon=True)
        self._thread.start()
        self._running = True

        # Wait for server to start
        time.sleep(1.0)

        print(f"Terminal server started at http://{self.host}:{self.port}")
        return self.get_url()

    def get_url(self) -> str:
        """Get the URL of the terminal server."""
        return f"http://{self.host}:{self.port}"

    def stop(self):
        """Stop the terminal server."""
        if self._app and self._app.config.get("child_pid"):
            try:
                os.kill(self._app.config["child_pid"], signal.SIGTERM)
                time.sleep(0.1)
                os.kill(self._app.config["child_pid"], signal.SIGKILL)
            except (ProcessLookupError, OSError):
                pass
            self._app.config["child_pid"] = None
            self._app.config["fd"] = None
        self._running = False

        if self.port in _terminal_servers:
            del _terminal_servers[self.port]


class Terminal:
    """
    A Terminal component that can be embedded in Gradio Blocks.

    This component provides an interactive terminal using xterm.js
    that communicates with a PTY backend through Flask-SocketIO.

    IMPORTANT: If using SSH tunneling, tunnel both Gradio port and terminal port:
        ssh -L 7860:localhost:7860 -L 5000:localhost:5000 user@remote

    Example:
        import gradio as gr
        from gradio_terminal import Terminal

        with gr.Blocks() as demo:
            gr.Markdown("# My App with Terminal")
            terminal = Terminal()

        demo.launch()
    """

    def __init__(
        self,
        port: int = 5000,
        host: str = "127.0.0.1",
        command: str = "bash",
        height: int = 400,
        label: str | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        allow_sudo: bool = True,
        blacklist_commands: list[str] | None = None,
    ):
        """
        Create a Terminal component.

        Args:
            port: Port for the terminal WebSocket server (must be tunneled if using SSH).
            host: Host for the terminal server.
            command: Shell command to run (default: bash).
            height: Height of the terminal in pixels.
            label: Label for the component.
            visible: Whether the terminal is visible.
            elem_id: HTML element ID.
            elem_classes: CSS classes.
            allow_sudo: Whether to allow sudo commands (default: True).
            blacklist_commands: List of commands to block (default: None).
        """
        self.port = port
        self.host = host
        self.command = command
        self.height = height
        self.label = label
        self.visible = visible
        self.elem_id = elem_id
        self.elem_classes = elem_classes
        self.allow_sudo = allow_sudo
        self.blacklist_commands = blacklist_commands or []

        # Start the terminal server
        self._server = TerminalServer(port=port, host=host, command=command)
        self._server.allow_sudo = allow_sudo
        self._server.blacklist_commands = self.blacklist_commands
        terminal_url = self._server.start()

        # Build the HTML with iframe
        label_html = ""
        if label:
            label_html = (
                f'<div style="font-weight: bold; margin-bottom: 5px; color: #d4d4d4;">{label}</div>'
            )

        # Use localhost for iframe src (browser connects to tunneled port)
        iframe_url = f"http://localhost:{port}"

        self._component = gr.HTML(
            value=f"""
            {label_html}
            <div style="border: 1px solid #444; border-radius: 5px; overflow: hidden;">
                <iframe
                    src="{iframe_url}"
                    style="border: none; width: 100%; height: {height}px;"
                    allow="clipboard-read; clipboard-write"
                ></iframe>
            </div>
            """,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
        )

    def stop(self):
        """Stop the terminal server."""
        self._server.stop()


def create_terminal(
    port: int = 5000,
    host: str = "127.0.0.1",
    command: str = "bash",
    height: int = 400,
    label: str | None = None,
    allow_sudo: bool = True,
    blacklist_commands: list[str] | None = None,
) -> Terminal:
    """
    Create a terminal component that can be used in Gradio Blocks.

    Args:
        port: Port for the terminal WebSocket server.
        host: Host for the terminal server.
        command: Shell command to run (default: bash).
        height: Height of the terminal in pixels.
        label: Optional label for the terminal.
        allow_sudo: Whether to allow sudo commands (default: True).
        blacklist_commands: List of commands to block (default: None).

    Returns:
        A Terminal instance.
    """
    return Terminal(
        port=port,
        host=host,
        command=command,
        height=height,
        label=label,
        allow_sudo=allow_sudo,
        blacklist_commands=blacklist_commands,
    )


def create_terminal_demo(
    port: int = 5000,
    host: str = "127.0.0.1",
    command: str = "bash",
    height: int = 400,
    allow_sudo: bool = True,
    blacklist_commands: list[str] | None = None,
) -> gr.Blocks:
    """
    Create a Gradio Blocks demo with an embedded terminal.

    Args:
        port: Port for the terminal server.
        host: Host for the terminal server.
        command: Shell command to run.
        height: Height of the terminal in pixels.
        allow_sudo: Whether to allow sudo commands (default: True).
        blacklist_commands: List of commands to block (default: None).

    Returns:
        A Gradio Blocks instance with the terminal.
    """
    with gr.Blocks(title="Gradio Terminal") as demo:
        gr.Markdown("## Interactive Terminal")
        gr.Markdown(f"Terminal server running on port {port}")

        Terminal(
            port=port,
            host=host,
            command=command,
            height=height,
            allow_sudo=allow_sudo,
            blacklist_commands=blacklist_commands,
        )

        gr.Markdown(f"""
            **Tips:**
            - If using SSH tunneling, also tunnel port {port}:
              `ssh -L 7860:localhost:7860 -L {port}:localhost:{port} user@remote`
            """)

    return demo


def launch_terminal(
    port: int = 5000,
    host: str = "127.0.0.1",
    command: str = "bash",
    share: bool = False,
    allow_sudo: bool = True,
    blacklist_commands: list[str] | None = None,
    **launch_kwargs,
):
    """
    Launch a standalone Gradio app with a terminal.

    Args:
        port: Port for the terminal WebSocket server.
        host: Host for the terminal server.
        command: Shell command to run (default: bash).
        share: Whether to create a public link.
        allow_sudo: Whether to allow sudo commands (default: True).
        blacklist_commands: List of commands to block (default: None).
        **launch_kwargs: Additional arguments passed to demo.launch()
    """
    demo = create_terminal_demo(
        port=port,
        host=host,
        command=command,
        allow_sudo=allow_sudo,
        blacklist_commands=blacklist_commands,
    )
    demo.launch(share=share, **launch_kwargs)
