import requests
import pytest
from gradio_terminal import TerminalServer, Terminal


def test_server_start_and_stop():
    port = 5001
    server = TerminalServer(port=port, allow_unsafe_werkzeug=True)
    url = server.start()

    assert url == f"http://127.0.0.1:{port}"

    try:
        response = requests.get(f"http://127.0.0.1:{port}")
        assert response.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.fail("TerminalServer failed to start or is not reachable")
    finally:
        server.stop()


def test_terminal_component_lifecycle():
    port = 5002
    terminal = Terminal(port=port, allow_unsafe_werkzeug=True)

    try:
        response = requests.get(f"http://127.0.0.1:{port}")
        assert response.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.fail("Terminal component failed to start internal server")
    finally:
        terminal.stop()
