#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


DOC_ID = "Jv85dXAeZoKJ7exJi4Yc4Edrnhf"


def text_from_block(block: dict) -> str:
    data = block.get("data", {})
    text = data.get("text", {})
    initial = text.get("initialAttributedTexts", {}).get("text", {})
    if isinstance(initial, dict):
        return "".join(str(initial[key]) for key in sorted(initial.keys(), key=lambda x: int(x) if str(x).isdigit() else str(x))).strip()
    if isinstance(initial, str):
        return initial.strip()
    return ""


def slugify(value: str, fallback: str) -> str:
    value = re.sub(r"[\\s/\\\\:：*?\"<>|]+", "-", value.strip())
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:90] or fallback


def collect_order(block_map: dict, root_id: str) -> list[str]:
    root = block_map.get(root_id)
    if not root:
        return [key for key in block_map.keys() if key != root_id]

    ordered = []

    def visit(block_id: str):
        if block_id != root_id:
            ordered.append(block_id)
        for child_id in block_map.get(block_id, {}).get("data", {}).get("children", []) or []:
            visit(child_id)

    for child_id in root.get("data", {}).get("children", []) or []:
        visit(child_id)
    return ordered


def block_to_markdown(block: dict, block_map: dict) -> str:
    data = block.get("data", {})
    typ = data.get("type")
    text = text_from_block(block)

    if typ == "heading1":
        return f"# {text}" if text else ""
    if typ == "heading2":
        return f"## {text}" if text else ""
    if typ == "heading3":
        return f"### {text}" if text else ""
    if typ == "heading4":
        return f"#### {text}" if text else ""
    if typ == "heading5":
        return f"##### {text}" if text else ""
    if typ == "heading6":
        return f"###### {text}" if text else ""
    if typ == "bullet":
        return f"- {text}" if text else ""
    if typ == "ordered":
        return f"1. {text}" if text else ""
    if typ == "divider":
        return "---"
    if typ == "callout":
        return f"> {text}" if text else "> [callout]"
    if typ == "table":
        rows = []
        for child_id in data.get("children", []) or []:
            child = block_map.get(child_id, {})
            cell_text = text_from_block(child)
            if cell_text:
                rows.append(cell_text)
        if rows:
            return "\n".join(f"| {row} |" for row in rows)
        return ""
    if typ == "table_cell":
        return text
    if typ == "image":
        return "![image]()"
    if typ in {"isv"}:
        return f"> [{typ} block omitted]"
    if typ == "text":
        return text
    return text


def normalize_lines(lines: list[str]) -> str:
    output = []
    previous_blank = False
    for line in lines:
        line = line.rstrip()
        blank = not line
        if blank and previous_blank:
            continue
        output.append(line)
        previous_blank = blank
    return "\n".join(output).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert merged Feishu blocks to Markdown.")
    parser.add_argument("--raw", default="raw/merged_blocks.json")
    parser.add_argument("--docs", default="docs")
    args = parser.parse_args()

    raw = json.loads(Path(args.raw).read_text())
    block_map = raw["block_map"]
    root_id = raw.get("doc_id", DOC_ID)
    out_dir = Path(args.docs)
    chapters_dir = out_dir / "chapters"
    out_dir.mkdir(parents=True, exist_ok=True)
    chapters_dir.mkdir(parents=True, exist_ok=True)

    title = "《GEO白皮书：AI搜索时代的品牌增长新范式》"
    order = collect_order(block_map, root_id)
    lines = [f"# {title}", ""]
    chapters = []
    current = None

    for block_id in order:
        block = block_map.get(block_id)
        if not block:
            continue
        typ = block.get("data", {}).get("type")
        md = block_to_markdown(block, block_map)
        if not md:
            continue

        if typ == "heading1":
            heading = text_from_block(block)
            filename = f"{len(chapters) + 1:02d}-{slugify(heading, block_id)}.md"
            current = {"title": heading, "filename": filename, "lines": [f"# {heading}", ""]}
            chapters.append(current)
            lines.extend(["", md, ""])
            continue

        lines.extend([md, ""])
        if current:
            current["lines"].extend([md, ""])

    index_md = normalize_lines(lines)
    (out_dir / "index.md").write_text(index_md)

    summary_lines = [
        "# 文档目录",
        "",
        f"- 来源文档：{root_id}",
        f"- Block 数量：{len(block_map)}",
        f"- 章节数量：{len(chapters)}",
        "",
        "## 章节",
        "",
    ]
    for chapter in chapters:
        summary_lines.append(f"- [{chapter['title']}](chapters/{chapter['filename']})")
    (out_dir / "README.md").write_text(normalize_lines(summary_lines))

    for chapter in chapters:
        (chapters_dir / chapter["filename"]).write_text(normalize_lines(chapter["lines"]))

    print(f"wrote {out_dir / 'index.md'} and {len(chapters)} chapter files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
