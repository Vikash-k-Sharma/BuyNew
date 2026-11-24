import json
from pathlib import Path
from urllib.parse import quote, urlparse

import frappe


AD_IMAGE_HOST = "rukminim2.flixcart.com"


def get_context(context):

    ads = frappe.get_all(
        "Ad Img",
        fields=["name", "ad_img"],
        order_by="creation asc",
        page_length=100,
    )
    visible_ads = [ad for ad in ads if ad.ad_img]
    if len(visible_ads) > 1:
        visible_ads = visible_ads[:-1]

    if visible_ads:
        first_ad = visible_ads[0]
        if urlparse(first_ad.ad_img).hostname == AD_IMAGE_HOST:
            context.preload_image = (
                "/api/method/buy_new.api.get_ad_image?name="
                f"{quote(first_ad.name, safe='')}"
            )

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
