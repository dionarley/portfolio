#!/usr/bin/env python3
"""Servidor de desenvolvimento com recarga automática.

Sem dependências externas: serve o site, injeta um cliente de recarga no
HTML e recarrega a página quando index.html, styles.css ou script.js mudam.

Uso:
    python3 scripts/dev.py                 # http://localhost:8000
    python3 scripts/dev.py --port 3000
    python3 scripts/dev.py --host 0.0.0.0  # testar no celular na mesma rede
    python3 scripts/dev.py --open          # abre o navegador
"""

from __future__ import annotations

import argparse
import mimetypes
import threading
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WATCHED = ("index.html", "styles.css", "script.js")

CONTENT_TYPES = {
    ".css": "text/css; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
}

CLIENT_SCRIPT = """(() => {
    if (!('EventSource' in window)) return;

    const source = new EventSource('/__dev/events');
    source.addEventListener('reload', () => window.location.reload());
})();
"""


class Reloader:
    """Observa os arquivos e avisa as conexões abertas quando algo muda."""

    def __init__(self, files: list[Path]) -> None:
        self.files = files
        self.version = 0
        self._condition = threading.Condition()
        self._mtimes = self._snapshot()
        threading.Thread(target=self._watch, daemon=True).start()

    def _snapshot(self) -> dict[Path, int]:
        return {path: path.stat().st_mtime_ns for path in self.files if path.exists()}

    def _watch(self) -> None:
        while True:
            time.sleep(0.4)
            snapshot = self._snapshot()
            if snapshot == self._mtimes:
                continue
            self._mtimes = snapshot
            with self._condition:
                self.version += 1
                self._condition.notify_all()

    def wait(self, version: int, timeout: float = 15.0) -> int:
        with self._condition:
            self._condition.wait_for(lambda: self.version != version, timeout=timeout)
            return self.version


class DevHandler(SimpleHTTPRequestHandler):
    server_version = "PortfolioDev/1.0"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/__dev/events":
            self._events()
        elif self.path == "/__dev/client.js":
            self._send(CLIENT_SCRIPT.encode("utf-8"), CONTENT_TYPES[".js"])
        else:
            self._file()

    def _file(self) -> None:
        path = Path(self.translate_path(self.path))
        if path.is_dir():
            path = path / "index.html"
        if not path.is_file():
            self.send_error(404, "Arquivo não encontrado")
            return

        if path.suffix == ".html":
            html = path.read_text(encoding="utf-8")
            html = html.replace(
                "</body>",
                '<script src="/__dev/client.js" defer></script>\n</body>',
            )
            self._send(html.encode("utf-8"), CONTENT_TYPES[".html"])
            return

        content_type = CONTENT_TYPES.get(path.suffix)
        if content_type is None:
            guessed, _ = mimetypes.guess_type(path.name)
            content_type = guessed or "application/octet-stream"
        self._send(path.read_bytes(), content_type)

    def _send(self, body: bytes, content_type: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _events(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        version = self.server.reloader.version
        try:
            self.wfile.write(f"event: ready\ndata: {version}\n\n".encode("utf-8"))
            self.wfile.flush()

            while True:
                updated = self.server.reloader.wait(version)
                if updated == version:
                    continue
                version = updated
                self.wfile.write(f"event: reload\ndata: {version}\n\n".encode("utf-8"))
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            return

    def log_message(self, format: str, *args) -> None:
        print(f"  {self.address_string()} — {format % args}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Servidor de desenvolvimento do portfólio")
    parser.add_argument("-p", "--port", type=int, default=8000, help="porta (padrão: 8000)")
    parser.add_argument("--host", default="127.0.0.1", help="endereço de escuta (padrão: 127.0.0.1)")
    parser.add_argument("--open", action="store_true", help="abre o navegador ao iniciar")
    args = parser.parse_args()

    try:
        server = ThreadingHTTPServer((args.host, args.port), DevHandler)
    except OSError as error:
        print(f"Não foi possível abrir {args.host}:{args.port} — {error}")
        return 1

    server.daemon_threads = True
    server.reloader = Reloader([ROOT / name for name in WATCHED])

    url = f"http://localhost:{args.port}/"
    print(f"Servidor de desenvolvimento: {url}", flush=True)
    print(f"Recarga automática: {', '.join(WATCHED)}", flush=True)
    print("Ctrl+C para parar.\n", flush=True)

    if args.open:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.server_close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
