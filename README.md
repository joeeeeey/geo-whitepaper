# GEO 白皮书 · Cyber Atlas

A redesigned, long-form-friendly Jekyll site for the GEO whitepaper. Published live at:

- <https://joeeeeey.github.io/geo-whitepaper/>

## Source

Content is exported from a Feishu doc:

- Source: `https://yaojingang.feishu.cn/docx/Jv85dXAeZoKJ7exJi4Yc4Edrnhf`
- Generated pages: `docs/pages/` (84 chapters, grouped into 6 sections)
- Raw pulled block JSON: `raw/`

## Design

The visual system is **Cyber Atlas** — a dark, knowledge-graph aesthetic with:

- IBM Plex Sans / Plex Mono for UI, Noto Serif SC for long-form Chinese reading
- Cyan (`#6ef3ff`) primary accent over an ink ramp, six section colors for the graph TOC
- Sticky outline + reading progress bar + previous/next pager on every article
- ⌘K / `/` command palette over all 84 chapters
- Animated radial graph TOC + hero particle field; everything honors `prefers-reduced-motion`

Layouts under `docs/_layouts/`, shared partials under `docs/_includes/`, tokens in
`docs/assets/css/styles.css`, behavior in `docs/assets/js/app.js`.

## Rebuild

```bash
# 1. Pull the latest doc (skip if raw/ is fresh).
python3 tools/pull_feishu_docx.py --out raw

# 2. Re-export Markdown chapters.
python3 tools/feishu_to_markdown.py --raw raw/merged_blocks.json --docs docs

# 3. Apply the Cyber Atlas frontmatter, section landings, and structure data.
python3 tools/build_cyber_atlas.py --docs docs
```

Step 3 is idempotent — re-running on already-processed pages refreshes only the
frontmatter block. After running the three steps, `cd docs && jekyll build` will
produce the static site under `docs/_site/`.

## GitHub Pages

The repository publishes the `docs/` directory on `main`. GitHub Pages auto-builds
the Jekyll site (`baseurl: /geo-whitepaper`) — no Actions workflow required.

## Local preview

```bash
cd docs
jekyll serve --baseurl /geo-whitepaper
# open http://127.0.0.1:4000/geo-whitepaper/
```
