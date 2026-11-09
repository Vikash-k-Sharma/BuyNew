import json
from pathlib import Path


def get_context(context):

    manifest_path = (
        Path(__file__).resolve().parents[1]
        / "public"
        / "frontend"
        / ".vite"
        / "manifest.json"
    )

    manifest = json.loads(manifest_path.read_text())

    entry = manifest["index.html"]

    context.js_files = [entry["file"]]
    context.css_files = entry.get("css", [])
    context.title = "BuyNew"
