import threading
import time
import socket
import uvicorn
import webview

from app.main import app


class Api:
    """This class exposes Python methods to the JavaScript frontend."""
    def save_csv(self, filename, content):
        window = webview.windows[0]
        # Open a native OS "Save As" dialog
        result = window.create_file_dialog(
            webview.SAVE_DIALOG, 
            directory='', 
            save_filename=filename
        )
        if result:
            filepath = result[0]
            # Write the CSV content directly to the selected file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def run_server(port):
    config = uvicorn.Config(
        app="app.main:app", 
        host="127.0.0.1", 
        port=port, 
        log_level="warning"
    )
    server = uvicorn.Server(config)
    
    # Disable signal handling so it doesn't crash the background thread
    server.install_signal_handlers = lambda: None 
    
    server.run()


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

    # Instantiate the API bridge
    api = Api()

    webview.create_window(
        "Clothing Shop POS",
        f"http://127.0.0.1:{port}",
        width=1200,
        height=800,
        min_size=(900, 600),
        js_api=api  # Connect the API to the frontend here
    )
    webview.start(gui='qt')