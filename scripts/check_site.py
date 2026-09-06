#!/usr/bin/env python3
"""Offline public-site checks. Image content still needs human visual inspection."""
import hashlib
import json
import re
import struct
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

SITE = Path(__file__).resolve().parents[1] / "site"
errors = []


def require(condition, message):
    if not condition:
        errors.append(message)


class Document(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids = set()
        self.elements = []
        self.source = path.read_text(encoding="utf-8")
        self.feed(self.source)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        self.elements.append((tag, attrs))
        if "id" in attrs:
            require(attrs["id"] not in self.ids, f"{self.path.name}: duplicate ID {attrs['id']}")
            self.ids.add(attrs["id"])

    handle_startendtag = handle_starttag


def target_path(document, url):
    parts = urlsplit(url)
    if parts.scheme or parts.netloc:
        return None
    # Root-relative URLs break at the GitHub project Pages subpath.
    require(not parts.path.startswith("/"), f"{document.name}: root-relative URL {url}")
    target = (document.parent / unquote(parts.path)).resolve() if parts.path else document
    require(target.is_relative_to(SITE), f"{document.name}: URL leaves site: {url}")
    if target.is_dir():
        target /= "index.html"
    require(target.is_file(), f"{document.name}: missing local target: {url}")
    return target


def png_size(path):
    header = path.read_bytes()[:24]
    require(header[:8] == b"\x89PNG\r\n\x1a\n", f"{path.name}: invalid PNG")
    return struct.unpack(">II", header[16:24]) if len(header) == 24 else (0, 0)


require((SITE / "index.html").is_file(), "Missing index.html")
require((SITE / ".nojekyll").is_file(), "Missing .nojekyll")
files = list(SITE.rglob("*"))
links = [path for path in files if path.is_symlink()]
if links:
    sys.exit("FAIL: symbolic links are not allowed in site/")

secret = re.compile(r"xox[baprs]-|gh[pousr]_[A-Za-z0-9_]+|glsa_[A-Za-z0-9_]+|/Users/[^/]+/")
for path in files:
    if not path.is_file():
        continue
    text = path.read_bytes().decode("utf-8", errors="ignore")
    require(not secret.search(text), f"{path.name}: potential secret or local path")
    repos = re.findall(r"(?:musinsa|29CM-Developers)/[A-Za-z0-9_.-]+", text)
    require(all(repo == "musinsa/cs-claude-marketplace" for repo in repos),
            f"{path.name}: unexpected internal repository")

documents = {path.resolve(): Document(path) for path in SITE.rglob("*.html")}
image_refs = set()
bundle_revisions = set()
for path, doc in documents.items():
    for tag, attrs in doc.elements:
        for key in ("href", "src"):
            url = attrs.get(key)
            if url is None:
                continue
            target = target_path(path, url)
            if target is None:
                continue
            fragment = unquote(urlsplit(url).fragment)
            if fragment and target in documents:
                require(fragment in documents[target].ids, f"{path.name}: missing anchor {url}")
            if target.name in ("app.js", "styles.css"):
                revision = urlsplit(url).query
                require(revision.startswith("v="), f"{path.name}: missing bundle revision")
                bundle_revisions.add(revision)
            if tag == "img" and key == "src":
                require(bool(attrs.get("alt")), f"{path.name}: image has no description")
                image_refs.add(target)
                if target.suffix == ".png" and target.is_file():
                    require((attrs.get("width"), attrs.get("height")) == tuple(map(str, png_size(target))),
                            f"{path.name}: dimensions differ from {target.name}")
        if attrs.get("role") == "tab":
            require(attrs.get("aria-controls") in doc.ids, f"{path.name}: tab has no panel")
        for key in ("aria-controls", "aria-labelledby"):
            for identifier in attrs.get(key, "").split():
                require(identifier in doc.ids, f"{path.name}: missing {key} target {identifier}")
    for tag, attrs in doc.elements:
        if tag == "script":
            require(bool(attrs.get("src")), f"{path.name}: inline script violates site CSP")
require(len(bundle_revisions) == 1, "Product and guide bundle revisions differ")

screens = SITE / "assets/screens"
manifest = json.loads((screens / "manifest.json").read_text(encoding="utf-8"))
require(manifest["exampleData"] is True, "Image provenance must identify example data")
listed = set()
for entry in manifest["images"]:
    path = screens / entry["file"]
    require(path.parent == screens and path.suffix == ".png", "Invalid image manifest path")
    require(path not in listed, "Duplicate image manifest entry")
    listed.add(path)
    require(path.is_file(), f"{path.name}: missing manifest image")
    if not path.is_file():
        continue
    require(hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], f"{path.name}: hash mismatch")
    require(png_size(path) == (entry["width"], entry["height"]), f"{path.name}: manifest size mismatch")
    require(path in image_refs, f"{path.name}: unused UI image")
require(listed == set(screens.glob("*.png")), "Unlisted UI images in public artifact")
for relative in ("index.html", "guide/index.html"):
    source = documents[SITE / relative].source
    require(f"문서 기준 {manifest['appVersion']}" in source, f"{relative}: stale document version")
    require(manifest["updatedAt"].replace("-", ".") in source, f"{relative}: stale document date")
required_sections = {"connections", "usage", "warning", "deep", "recurrence", "work", "safety", "images"}
require(required_sections <= documents[SITE / "guide/index.html"].ids, "Missing current guide section")

if errors:
    sys.exit("FAIL\n" + "\n".join(errors))
print(f"PASS: {len(documents)} pages, local links/anchors, tabs, bundle revisions, {len(listed)} UI images and public-artifact guards")
