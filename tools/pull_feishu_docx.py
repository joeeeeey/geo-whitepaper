#!/usr/bin/env python3
import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from http.cookiejar import MozillaCookieJar
from typing import Optional


DEFAULT_DOC_ID = "Jv85dXAeZoKJ7exJi4Yc4Edrnhf"
BASE_URL = "https://yaojingang.feishu.cn"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
)


def extract_object_after(html: str, marker: str) -> dict:
    start = html.find(marker)
    if start == -1:
        raise RuntimeError(f"marker not found: {marker}")

    i = start + len(marker)
    while i < len(html) and html[i].isspace():
        i += 1
    if i >= len(html) or html[i] != "{":
        raise RuntimeError(f"object start not found after marker: {marker}")

    depth = 0
    in_string = False
    escaped = False
    for j in range(i, len(html)):
        ch = html[j]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(html[i : j + 1])

    raise RuntimeError(f"object end not found after marker: {marker}")


def request_json(opener, url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json, text/plain, */*",
            "Referer": f"{BASE_URL}/docx/{DEFAULT_DOC_ID}",
            "User-Agent": USER_AGENT,
        },
    )
    with opener.open(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def request_text(opener, url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": USER_AGENT,
        },
    )
    with opener.open(req, timeout=60) as response:
        return response.read().decode("utf-8", errors="replace")


def client_vars_url(doc_id: str, cursor: Optional[str], limit: int) -> str:
    params = {"id": doc_id, "mode": "7", "limit": str(limit)}
    if cursor:
        params["cursor"] = cursor
    return f"{BASE_URL}/space/api/docx/pages/client_vars?{urllib.parse.urlencode(params)}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Pull a public Feishu docx page into raw JSON pages.")
    parser.add_argument("--doc-id", default=DEFAULT_DOC_ID)
    parser.add_argument("--out", default="raw")
    parser.add_argument("--limit", type=int, default=239)
    parser.add_argument("--sleep", type=float, default=0.2)
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    cookie_path = out_dir / "cookies.txt"
    cookies = MozillaCookieJar(str(cookie_path))
    if cookie_path.exists():
        cookies.load(ignore_discard=True, ignore_expires=True)

    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))

    html = request_text(opener, f"{BASE_URL}/docx/{args.doc_id}")
    (out_dir / "doc_page.html").write_text(html)
    cookies.save(ignore_discard=True, ignore_expires=True)

    marker = "window.DATA = Object.assign({}, window.DATA, { clientVars: Object("
    first = extract_object_after(html, marker)
    pages = [first]
    (out_dir / "page_000.json").write_text(json.dumps(first, ensure_ascii=False, indent=2))

    seen_cursors = set()
    cursor = first.get("data", {}).get("cursor")
    page_index = 1
    while cursor:
        if cursor in seen_cursors:
            break
        seen_cursors.add(cursor)

        payload = request_json(opener, client_vars_url(args.doc_id, cursor, args.limit))
        if payload.get("code") != 0:
            print(f"stop: page {page_index} returned code={payload.get('code')} message={payload.get('message')}", file=sys.stderr)
            break

        pages.append(payload)
        (out_dir / f"page_{page_index:03d}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2)
        )
        cookies.save(ignore_discard=True, ignore_expires=True)

        data = payload.get("data", {})
        cursor = data.get("cursor") if data.get("has_more") else None
        page_index += 1
        time.sleep(args.sleep)

    merged = {
        "doc_id": args.doc_id,
        "page_count": len(pages),
        "block_map": {},
        "block_sequence": [],
        "meta": first.get("data", {}).get("meta_map", {}),
    }
    for page in pages:
        data = page.get("data", {})
        merged["block_map"].update(data.get("block_map", {}))
        for block_id in data.get("block_sequence", []):
            if block_id not in merged["block_sequence"]:
                merged["block_sequence"].append(block_id)

    (out_dir / "merged_blocks.json").write_text(json.dumps(merged, ensure_ascii=False, indent=2))
    print(f"pulled {len(pages)} pages, {len(merged['block_map'])} blocks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
