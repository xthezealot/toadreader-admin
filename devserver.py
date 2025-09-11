#!/usr/bin/env python

import argparse
import json
import os
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

LIVERE_LOAD_SCRIPT = """<script>
    setInterval(() => {
        fetch("/reload-status")
            .then(r => r.json())
            .then(d => d.reload && location.reload())
            .catch(() => {})
    }, 1000)
</script>"""


def make_handler(root_dir):
    class LiveReloadHandler(SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=root_dir, **kw)

        def do_GET(self):
            request_path = self.path.split("?", 1)[0]
            if request_path == "/reload-status":
                reload_event = self.server.reload_event
                should_reload = reload_event.is_set()
                if should_reload:
                    reload_event.clear()
                body_bytes = json.dumps({"reload": should_reload}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body_bytes)
                return
            target_path = "/index.html" if request_path == "/" else request_path
            fs_path = self.translate_path(target_path)
            if os.path.isfile(fs_path) and fs_path.endswith(".html"):
                try:
                    content = open(fs_path, encoding="utf-8", errors="replace").read()
                except OSError:
                    self.send_error(404, "File not found")
                    return
                if "</body>" in content:
                    content = content.replace(
                        "</body>", LIVERE_LOAD_SCRIPT + "</body>", 1
                    )
                data = content.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(data)
                return
            super().do_GET()

        def log_message(self, format, *args):
            # Silence only the reload polling endpoint
            request_path = getattr(self, "path", "").split("?", 1)[0]
            if request_path == "/reload-status":
                return
            return super().log_message(format, *args)

    return LiveReloadHandler


def watch(root_dir, reload_event, stop_event):
    watched_exts = (".html", ".css", ".js")
    previous_signature = None
    while not stop_event.is_set():
        time.sleep(1.0)
        signature = 0
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.lower().endswith(watched_exts):
                    filepath = os.path.join(dirpath, filename)
                    try:
                        mtime_ns = os.stat(filepath).st_mtime_ns
                        signature ^= hash((filepath, mtime_ns))
                    except OSError:
                        pass
        if signature != previous_signature:
            if previous_signature is not None:
                reload_event.set()
                print("Files changed - reload needed")
            previous_signature = signature


def run(port):
    root_dir = os.path.abspath("src")
    reload_event = threading.Event()
    stop_event = threading.Event()
    server = ThreadingHTTPServer(("localhost", port), make_handler(root_dir))
    server.reload_event = reload_event
    print(f"Server running on http://localhost:{port}")
    threading.Thread(
        target=watch, args=(root_dir, reload_event, stop_event), daemon=True
    ).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        stop_event.set()
        server.shutdown()
        server.server_close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", nargs="?", type=int, default=8002)
    args = parser.parse_args()
    run(args.port)


if __name__ == "__main__":
    main()
