import threading
import time
import socket
import uvicorn
import webview

from app.main import app


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def run_server(port):
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


def wait_for_server(port, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.2)
    return False


if __name__ == "__main__":
    port = find_free_port()

    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    if not wait_for_server(port):
        raise RuntimeError("Server failed to start")

    webview.create_window(
        "Clothing Shop POS",
        f"http://127.0.0.1:{port}",
        width=1200,
        height=800,
        min_size=(900, 600),
    )
    webview.start()
