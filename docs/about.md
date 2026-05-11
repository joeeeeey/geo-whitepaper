---
layout: default
title: "关于本图谱"
permalink: /about/
---

<div class="page">
  <header class="section-head" style="margin-top: var(--s-6);">
    <div class="kicker">
      <span class="ord">/ INFO</span>
      <span>关于</span>
      <span style="color:var(--text-faint);">v2.4 · 2025</span>
    </div>
    <div>
      <h2>关于《GEO 白皮书》</h2>
      <p class="blurb">本图谱是从原始飞书文档导出并重排版的开源版本，旨在提供长文友好的阅读体验。</p>
    </div>
  </header>

  <article class="body" style="max-width: var(--read-max); margin-top: var(--s-7);">
    <p class="lede">《GEO 白皮书：AI 搜索时代的品牌增长新范式》系统梳理了在大模型对话式搜索成为主入口后，品牌如何从“争取点击”转向“成为答案”的方法论与实战路径。</p>

    <h2 id="origin">来源</h2>
    <p>原文为<a href="https://yaojingang.feishu.cn/docx/Jv85dXAeZoKJ7exJi4Yc4Edrnhf" target="_blank" rel="noreferrer">向阳乔木在飞书上的公开文档</a>，社区持续更新。本仓库通过脚本将飞书 Block JSON 拆分成 84 篇可独立阅读的章节并按主题归类。</p>

    <h2 id="design">设计</h2>
    <p>视觉语言基于 <strong>Cyber Atlas</strong>（Direction B）——一个为深色长文优化的知识图谱风格：等宽元数据、衬线正文、cyan/violet 主题色、网格背景、低频粒子动画与圆周分支图谱。所有动画均尊重 <code>prefers-reduced-motion</code>。</p>

    <h2 id="pipeline">导出管线</h2>
    <p>原始管线保留并继续可用：</p>
    <pre><code>python3 tools/pull_feishu_docx.py --out raw
python3 tools/feishu_to_markdown.py --raw raw/merged_blocks.json --docs docs
python3 tools/build_cyber_atlas.py --docs docs</code></pre>
    <p>第三步会为每篇文章注入 frontmatter、生成结构数据与章节落地页。</p>

    <h2 id="keys">快捷键</h2>
    <ul>
      <li><kbd>⌘K</kbd> / <kbd>/</kbd>：打开搜索面板</li>
      <li><kbd>↑</kbd>/<kbd>↓</kbd>：在结果中切换</li>
      <li><kbd>↵</kbd>：进入选中章节</li>
      <li><kbd>esc</kbd>：关闭</li>
    </ul>

    <h2 id="license">许可</h2>
    <p>内容版权归原作者所有；本仓库的代码与样式以 MIT 协议开源。</p>
  </article>
</div>
