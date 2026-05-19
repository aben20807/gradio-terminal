from gradio_terminal import TerminalServer


def test_custom_theme_colors():
    custom_colors = {"background": "#FF0000", "foreground": "#00FF00"}
    server = TerminalServer(theme="dark", xterm_options={"theme": custom_colors})
    theme_json = server._get_xterm_theme_json()

    assert '"background": "#FF0000"' in theme_json
    assert '"foreground": "#00FF00"' in theme_json
    # Ensure non-overridden colors are still there (from dark theme preset)
    assert '"black": "#2E3436"' in theme_json
