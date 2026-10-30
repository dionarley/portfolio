#!/usr/bin/env python3
"""Verificações de sanidade do site antes de commitar.

Roda só com a biblioteca padrão do Python e cobre os erros que já
quebraram o projeto: HTML inválido, assets ausentes, variáveis CSS
indefinidas, JavaScript desbalanceado e arquivos que o Docker não copia
para a imagem (caso do LICENSE excluído pelo .dockerignore).

Uso:
    python3 tests/check.py

Erros impedem o commit (exit 1); avisos apenas informam.
"""

from __future__ import annotations

import fnmatch
import re
import shlex
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML_FILE = ROOT / "index.html"
CSS_FILE = ROOT / "styles.css"
JS_FILE = ROOT / "script.js"
DOCKERFILE = ROOT / "Dockerfile"
DOCKERIGNORE = ROOT / ".dockerignore"
COMPOSE_FILE = ROOT / "docker-compose.yml"

VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

EXTERNAL_PREFIXES = (
    "http://", "https://", "mailto:", "tel:", "data:", "//", "javascript:",
)


class Report:
    def __init__(self) -> None:
        self.errors: list[tuple[str, int | None, str]] = []
        self.warnings: list[tuple[str, int | None, str]] = []

    def error(self, where: str, message: str, line: int | None = None) -> None:
        self.errors.append((where, line, message))

    def warn(self, where: str, message: str, line: int | None = None) -> None:
        self.warnings.append((where, line, message))

    def render(self) -> str:
        lines = []
        for level, items in (("ERRO", self.errors), ("AVISO", self.warnings)):
            for where, line, message in items:
                location = f"{where}:{line}" if line else where
                lines.append(f"{level:<5} {location:<24} {message}")
        total = len(self.errors) + len(self.warnings)
        if total:
            lines.append("")
        lines.append(f"{len(self.errors)} erro(s), {len(self.warnings)} aviso(s)")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------
class Document(HTMLParser):
    """Coleta estrutura e referências do index.html."""

    def __init__(self, report: Report) -> None:
        super().__init__(convert_charrefs=True)
        self.report = report
        self.stack: list[tuple[str, int]] = []
        self.ids: dict[str, int] = {}
        self.classes: set[str] = set()
        self.links: list[tuple[str, int]] = []
        self.labels: list[tuple[str, int]] = []
        self.controls: list[tuple[str, str | None, int, bool]] = []
        self.meta: dict[str, str] = {}
        self.inline_vars: set[str] = set()
        self.lang: str | None = None
        self.has_main = False
        self.h1_count = 0
        self.has_title = False
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name: value for name, value in attrs}
        line = self.getpos()[0]

        if tag == "html":
            self.lang = attributes.get("lang")
        if tag == "main":
            self.has_main = True
        if tag == "title":
            self._in_title = True
        if tag == "h1":
            self.h1_count += 1
        if tag == "meta" and attributes.get("name"):
            self.meta[attributes["name"].lower()] = attributes.get("content") or ""

        if attributes.get("id"):
            ident = attributes["id"]
            if ident in self.ids:
                self.report.error("index.html", f"id duplicado: {ident}", line)
            self.ids[ident] = line

        if attributes.get("class"):
            self.classes.update(attributes["class"].split())

        if attributes.get("style"):
            self.inline_vars.update(re.findall(r"(--[\w-]+)\s*:", attributes["style"]))

        for attribute in ("href", "src"):
            value = attributes.get(attribute)
            if value is not None:
                self.links.append((value, line))

        if tag == "label" and attributes.get("for"):
            self.labels.append((attributes["for"], line))

        if tag in ("input", "textarea", "select"):
            has_aria = bool(attributes.get("aria-label") or attributes.get("aria-labelledby"))
            self.controls.append((tag, attributes.get("id"), line, has_aria))

        if tag not in VOID_ELEMENTS:
            self.stack.append((tag, line))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag in VOID_ELEMENTS:
            return
        if not self.stack:
            self.report.error("index.html", f"</{tag}> sem abertura", self.getpos()[0])
            return
        open_tag, line = self.stack.pop()
        if open_tag != tag:
            self.report.error(
                "index.html",
                f"</{tag}> fecha <{open_tag}> aberto na linha {line}",
                self.getpos()[0],
            )

    def handle_data(self, data: str) -> None:
        if self._in_title and data.strip():
            self.has_title = True


def local_assets(links: list[tuple[str, int]]) -> set[str]:
    assets = set()
    for value, _ in links:
        if not value or value.startswith("#") or value.startswith(EXTERNAL_PREFIXES):
            continue
        path = value.split("?")[0].split("#")[0]
        if path:
            assets.add(path)
    return assets


def check_html(report: Report) -> tuple[set[str], set[str]]:
    if not HTML_FILE.exists():
        report.error("index.html", "arquivo não encontrado")
        return set(), set()

    document = Document(report)
    document.feed(HTML_FILE.read_text(encoding="utf-8"))
    document.close()

    for tag, line in document.stack:
        report.error("index.html", f"<{tag}> não foi fechado", line)

    if not document.lang:
        report.error("index.html", "<html> sem atributo lang")
    elif document.lang.lower() != "pt-br":
        report.warn("index.html", f"lang inesperado: {document.lang}")

    if not document.has_title:
        report.error("index.html", "<title> vazio ou ausente")
    if not document.has_main:
        report.error("index.html", "falta o elemento <main>")
    if document.h1_count != 1:
        report.error("index.html", f"esperado 1 <h1>, encontrado {document.h1_count}")

    for name in ("viewport", "description"):
        if name not in document.meta:
            report.warn("index.html", f'falta <meta name="{name}">')

    for value, line in document.links:
        if value.startswith("#") and len(value) > 1:
            target = value[1:]
            if target not in document.ids:
                report.error("index.html", f'âncora "{value}" sem destino', line)

    assets = local_assets(document.links)
    for asset in sorted(assets):
        if not (ROOT / asset).exists():
            report.error("index.html", f"arquivo referenciado não existe: {asset}")

    for target, line in document.labels:
        if target not in document.ids:
            report.error("index.html", f'label for="{target}" sem campo correspondente', line)

    for tag, ident, line, has_aria in document.controls:
        if not ident:
            report.error("index.html", f"<{tag}> sem id para o label", line)
        elif not has_aria and not any(target == ident for target, _ in document.labels):
            report.error("index.html", f"<{tag} id={ident}> sem label acessível", line)

    return assets, document.inline_vars


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
def strip_css_literals(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"\"[^\"]*\"|'[^']*'", "", text)


def check_css(report: Report, inline_vars: set[str]) -> None:
    if not CSS_FILE.exists():
        report.error("styles.css", "arquivo não encontrado")
        return

    clean = strip_css_literals(CSS_FILE.read_text(encoding="utf-8"))

    if clean.count("{") != clean.count("}"):
        report.error("styles.css", "chaves { } desbalanceadas")
    if clean.count("(") != clean.count(")"):
        report.error("styles.css", "parênteses ( ) desbalanceados")

    defined = set(re.findall(r"(--[\w-]+)\s*:", clean)) | inline_vars
    used = set(re.findall(r"var\(\s*(--[\w-]+)", clean))
    for name in sorted(used - defined):
        report.error("styles.css", f"variável CSS não definida: {name}")

    for url in re.findall(r"url\(\s*['\"]?([^'\")]+)", clean):
        url = url.strip()
        if url.startswith(("data:", "http:", "https:", "#")):
            continue
        if not (ROOT / url).exists():
            report.error("styles.css", f"url() aponta para arquivo inexistente: {url}")


# ---------------------------------------------------------------------------
# JavaScript
# ---------------------------------------------------------------------------
def strip_js_literals(source: str) -> str:
    """Remove comentários e strings para contar delimitadores."""
    output: list[str] = []
    index = 0
    length = len(source)

    while index < length:
        char = source[index]
        next_char = source[index + 1] if index + 1 < length else ""

        if char == "/" and next_char == "/":
            newline = source.find("\n", index)
            if newline == -1:
                break
            index = newline
        elif char == "/" and next_char == "*":
            end = source.find("*/", index + 2)
            index = length if end == -1 else end + 2
        elif char in "\"'`":
            quote = char
            index += 1
            while index < length:
                if source[index] == "\\":
                    index += 2
                    continue
                if source[index] == quote:
                    index += 1
                    break
                index += 1
        else:
            output.append(char)
            index += 1

    return "".join(output)


def check_js(report: Report) -> None:
    if not JS_FILE.exists():
        report.error("script.js", "arquivo não encontrado")
        return

    source = JS_FILE.read_text(encoding="utf-8")

    node = shutil.which("node")
    if node:
        result = subprocess.run(
            [node, "--check", str(JS_FILE)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or "").strip().splitlines()
            report.error("script.js", detail[0] if detail else "erro de sintaxe")
        return

    clean = strip_js_literals(source)
    for opening, closing in (("{", "}"), ("(", ")"), ("[", "]")):
        if clean.count(opening) != clean.count(closing):
            report.error("script.js", f"delimitadores {opening}{closing} desbalanceados")


# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------
def read_ignore_patterns() -> list[str]:
    if not DOCKERIGNORE.exists():
        return []
    patterns = []
    for line in DOCKERIGNORE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            patterns.append(line)
    return patterns


def is_ignored(path: str, patterns: list[str]) -> bool:
    """Aproxima a semântica do .dockerignore (inclui diretórios e !negacao)."""
    parts = path.split("/")
    candidates = ["/".join(parts[: index + 1]) for index in range(len(parts))]
    ignored = False

    for raw in patterns:
        negate = raw.startswith("!")
        pattern = raw[1:] if negate else raw
        pattern = pattern.rstrip("/")

        matched = any(fnmatch.fnmatchcase(candidate, pattern) for candidate in candidates)
        if not matched and "/" not in pattern:
            matched = any(
                fnmatch.fnmatchcase(Path(candidate).name, pattern) for candidate in candidates
            )
        if matched:
            ignored = not negate

    return ignored


def dockerfile_copies() -> list[tuple[list[str], int]]:
    if not DOCKERFILE.exists():
        return []

    lines: list[tuple[str, int]] = []
    buffer = ""
    start_line = 0

    for number, raw in enumerate(DOCKERFILE.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not buffer:
            start_line = number
        if stripped.endswith("\\"):
            buffer += stripped[:-1] + " "
            continue
        lines.append((buffer + stripped, start_line))
        buffer = ""

    copies = []
    for line, number in lines:
        try:
            parts = shlex.split(line)
        except ValueError:
            continue
        if not parts or parts[0].upper() not in ("COPY", "ADD"):
            continue
        args = [part for part in parts[1:] if not part.startswith("--")]
        if len(args) < 2:
            continue
        copies.append((args[:-1], number))

    return copies


def expand_source(source: str) -> set[str]:
    path = ROOT / source
    if any(char in source for char in "*?["):
        return {str(match.relative_to(ROOT)) for match in ROOT.glob(source)}
    if path.is_dir():
        return {str(item.relative_to(ROOT)) for item in path.rglob("*") if item.is_file()}
    return {source} if path.exists() else set()


def check_docker(report: Report, assets: set[str]) -> None:
    patterns = read_ignore_patterns()
    shipped: set[str] = set()

    for sources, line in dockerfile_copies():
        for source in sources:
            if source.startswith(("http://", "https://")):
                continue

            expanded = expand_source(source)
            if not expanded:
                report.error("Dockerfile", f"COPY: {source} não existe no contexto", line)
                continue

            for item in expanded:
                if is_ignored(item, patterns):
                    report.error(
                        "Dockerfile",
                        f"COPY: {item} está excluído pelo .dockerignore",
                        line,
                    )
                else:
                    shipped.add(item)

    for asset in sorted(assets):
        if asset not in shipped:
            report.error("Dockerfile", f"{asset} é usado pelo site mas não entra na imagem")

    if COMPOSE_FILE.exists() and re.search(
        r"^version:", COMPOSE_FILE.read_text(encoding="utf-8"), flags=re.M
    ):
        report.warn("docker-compose.yml", "atributo `version` é obsoleto e pode ser removido")


# ---------------------------------------------------------------------------
def main() -> int:
    report = Report()

    assets, inline_vars = check_html(report)
    check_css(report, inline_vars)
    check_js(report)
    check_docker(report, assets)

    print(report.render())
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
