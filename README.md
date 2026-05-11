# GEO Whitepaper

Markdown export of a Feishu docx page:

- Source: `https://yaojingang.feishu.cn/docx/Jv85dXAeZoKJ7exJi4Yc4Edrnhf`
- Pages source directory: `docs/`
- Raw pulled block JSON: `raw/`

## Rebuild

```bash
python3 tools/pull_feishu_docx.py --out raw
python3 tools/feishu_to_markdown.py --raw raw/merged_blocks.json --docs docs
```

## GitHub Pages

This repository is configured to publish from the `docs/` directory on the default branch.
