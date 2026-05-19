from gradio_terminal import TerminalServer


def test_dark_theme_html():
    server = TerminalServer(theme="dark")
    config = server._get_xterm_theme_json()
    assert '"background": "#1E1E1E"' in config
    assert '"black": "#2E3436"' in config


def test_light_theme_html():
    server = TerminalServer(theme="light", xterm_options={"fontSize": 20})
    config = server._get_xterm_theme_json()
    assert '"fontSize": 20' in config
    assert '"background": "#EAECDD"' in config
    assert '"black": "#2F3126"' in config


def test_default_theme_html():
    server = TerminalServer()  # defaults to dark, 14
    config = server._get_xterm_theme_json()
    assert '"background": "#1E1E1E"' in config
    assert '"black": "#2E3436"' in config
