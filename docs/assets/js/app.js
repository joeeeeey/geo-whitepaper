/* Cyber Atlas — shared behavior for the GEO whitepaper.
   Mobile drawer, ⌘K search palette, reading progress, outline scrollspy,
   hero particles, animated graph TOC. No framework.
   Loads chapter index from window.GEO_INDEX (rendered by the layout). */
(function () {
  "use strict";

  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const BASE = (document.documentElement.dataset.baseurl || "").replace(/\/$/, "");
  const url = (p) => BASE + (p.startsWith("/") ? p : "/" + p);

  /* Read CSS custom properties so canvas drawings track the theme. */
  function themeColors() {
    const css = getComputedStyle(document.documentElement);
    const rgb = (css.getPropertyValue("--particle-rgb") || "110,243,255").trim();
    return {
      particleRGB: rgb,
      // Map directly to rgba() strings the canvases consume.
      particleLine: `rgba(${rgb},.16)`,
      particleDot: `rgba(${rgb},.7)`,
      graphRingStroke: `rgba(${rgb},0.08)`,
      graphLinkStroke: `rgba(${rgb},0.10)`,
      graphSubStroke: `rgba(${rgb},0.07)`,
      graphCenterFill: `rgb(${rgb})`,
      graphCenterShadow: `rgba(${rgb},.7)`,
      graphLabel: (css.getPropertyValue("--text-secondary") || "#aab2c0").trim() || "#aab2c0",
      graphCenterLabel: (css.getPropertyValue("--text-muted") || "#8a93a3").trim(),
    };
  }

  /* -------- Theme toggle -------- */
  function mountThemeToggle() {
    const btn = document.querySelector("[data-theme-toggle]");
    if (!btn) return;
    btn.addEventListener("click", () => {
      const cur = document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
      const next = cur === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem("geo-theme", next); } catch (e) {}
      document.dispatchEvent(new CustomEvent("geo:theme", { detail: { theme: next } }));
    });
  }

  /* -------- Mobile drawer -------- */
  function mountDrawer() {
    const btn = $(".menu-btn");
    if (!btn) return;
    btn.addEventListener("click", () => {
      const veil = document.createElement("div");
      veil.className = "drawer-veil";
      const draw = document.createElement("aside");
      draw.className = "drawer";
      const here = location.pathname;
      const items = [
        [url("/"), "图谱首页"],
        [url("/sections/"), "章节索引"],
        [url("/about/"), "关于"],
      ];
      draw.innerHTML = `
        <div class="head">
          <div class="brand"><span class="dot"></span> Cyber Atlas</div>
          <button class="close" aria-label="关闭">✕</button>
        </div>
        <ol>${items
          .map(
            ([h, l]) =>
              `<li><a href="${h}"${here === h ? ' aria-current="page"' : ""}>${l}</a></li>`
          )
          .join("")}</ol>
        <div class="lbl">PRESS ⌘K TO SEARCH</div>
      `;
      const close = () => {
        veil.remove();
        draw.remove();
      };
      veil.addEventListener("click", close);
      draw.querySelector(".close").addEventListener("click", close);
      document.body.append(veil, draw);
    });
  }

  /* -------- Command palette (⌘K) -------- */
  function mountPalette() {
    const INDEX = (window.GEO_INDEX || []).slice();
    let open = false,
      idx = 0;
    const openIt = () => {
      if (open) return;
      open = true;
      const veil = document.createElement("div");
      veil.className = "palette-veil";
      veil.id = "pal";
      veil.innerHTML = `
        <div class="palette" role="dialog" aria-label="搜索章节">
          <input type="text" placeholder="搜索 ${INDEX.length} 个章节…" autofocus />
          <div class="list"></div>
          <div class="foot-keys"><span>↑↓ 选择</span><span>↵ 打开</span><span>esc 关闭</span></div>
        </div>`;
      document.body.append(veil);
      const input = veil.querySelector("input");
      const list = veil.querySelector(".list");
      const render = (q = "") => {
        idx = 0;
        const qq = q.trim().toLowerCase();
        const rows = INDEX.filter(
          (r) => !qq || (r.t + r.s + r.n).toLowerCase().includes(qq)
        ).slice(0, 12);
        list.innerHTML =
          rows
            .map(
              (r, i) => `
            <a class="item ${i === 0 ? "active" : ""}" data-i="${i}" href="${r.href}">
              <span class="n">${r.n}</span>
              <span class="t">${r.t}</span>
              <span class="s">${r.s}</span>
            </a>`
            )
            .join("") ||
          `<div class="item"><span></span><span class="t" style="color:var(--text-muted);font-weight:400;">无匹配结果</span><span></span></div>`;
      };
      const move = (d) => {
        const items = list.querySelectorAll(".item[href]");
        if (!items.length) return;
        items[idx]?.classList.remove("active");
        idx = (idx + d + items.length) % items.length;
        items[idx].classList.add("active");
        items[idx].scrollIntoView({ block: "nearest" });
      };
      input.addEventListener("input", (e) => render(e.target.value));
      input.addEventListener("keydown", (e) => {
        if (e.key === "ArrowDown") {
          e.preventDefault();
          move(1);
        } else if (e.key === "ArrowUp") {
          e.preventDefault();
          move(-1);
        } else if (e.key === "Enter") {
          const a = list.querySelectorAll(".item[href]")[idx];
          if (a) location.href = a.getAttribute("href");
        } else if (e.key === "Escape") close();
      });
      veil.addEventListener("click", (e) => {
        if (e.target === veil) close();
      });
      render("");
    };
    const close = () => {
      open = false;
      document.getElementById("pal")?.remove();
    };
    document.addEventListener("keydown", (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        open ? close() : openIt();
      } else if (
        e.key === "/" &&
        !/INPUT|TEXTAREA/.test(document.activeElement?.tagName || "")
      ) {
        e.preventDefault();
        openIt();
      }
    });
    $$(".search,[data-search]").forEach((el) =>
      el.addEventListener("click", openIt)
    );
  }

  /* -------- Reading progress -------- */
  function mountProgress() {
    const bar = $(".progress-bar .fill");
    if (!bar) return;
    const target = $(".body") || document.body;
    const update = () => {
      const r = target.getBoundingClientRect();
      const total = r.height - window.innerHeight;
      const done = Math.min(1, Math.max(0, -r.top / Math.max(1, total)));
      bar.style.width = (done * 100).toFixed(2) + "%";
    };
    update();
    document.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
  }

  /* -------- Outline scrollspy -------- */
  function mountOutline() {
    const list = $(".outline ol");
    if (!list) return;
    // Auto-id any h2 that lacks one
    $$(".body h2").forEach((h, i) => {
      if (!h.id) h.id = "h-" + (i + 1);
    });
    const heads = $$(".body h2[id]");
    if (!heads.length) {
      const empty = $(".outline");
      if (empty) empty.style.display = "none";
      return;
    }
    list.innerHTML = heads
      .map(
        (h, i) => `
        <li data-id="${h.id}">
          <span><span style="color:var(--text-faint);margin-right:8px;">${String(
            i + 1
          ).padStart(2, "0")}</span>${h.textContent}</span>
          <span class="min">${h.dataset.min || ""}</span>
        </li>`
      )
      .join("");
    list.addEventListener("click", (e) => {
      const li = e.target.closest("li");
      if (!li) return;
      document.getElementById(li.dataset.id)?.scrollIntoView({
        behavior: reduced ? "auto" : "smooth",
        block: "start",
      });
    });
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((en) => {
          if (en.isIntersecting) {
            list.querySelectorAll("li").forEach((li) =>
              li.classList.toggle("active", li.dataset.id === en.target.id)
            );
          }
        });
      },
      { rootMargin: "-20% 0px -70% 0px" }
    );
    heads.forEach((h) => io.observe(h));
  }

  /* -------- Hero particles -------- */
  function mountParticles() {
    const c = $("canvas.particles");
    if (!c || reduced) return;
    const ctx = c.getContext("2d");
    let W = 0,
      H = 0,
      dpr = Math.min(2, window.devicePixelRatio || 1);
    let colors = themeColors();
    const resize = () => {
      const r = c.getBoundingClientRect();
      W = r.width;
      H = r.height;
      c.width = W * dpr;
      c.height = H * dpr;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);
    };
    resize();
    const N = 80;
    const pts = Array.from({ length: N }, () => ({
      x: Math.random() * W,
      y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.18,
      vy: (Math.random() - 0.5) * 0.18,
    }));
    let raf;
    const tick = () => {
      ctx.clearRect(0, 0, W, H);
      pts.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0 || p.x > W) p.vx *= -1;
        if (p.y < 0 || p.y > H) p.vy *= -1;
      });
      ctx.strokeStyle = colors.particleLine;
      ctx.lineWidth = 1;
      for (let i = 0; i < N; i++)
        for (let j = i + 1; j < N; j++) {
          const dx = pts[i].x - pts[j].x,
            dy = pts[i].y - pts[j].y,
            d2 = dx * dx + dy * dy;
          if (d2 < 120 * 120) {
            ctx.globalAlpha = 1 - d2 / (120 * 120);
            ctx.beginPath();
            ctx.moveTo(pts[i].x, pts[i].y);
            ctx.lineTo(pts[j].x, pts[j].y);
            ctx.stroke();
          }
        }
      ctx.globalAlpha = 1;
      ctx.fillStyle = colors.particleDot;
      pts.forEach((p) => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, 1.2, 0, 7);
        ctx.fill();
      });
      raf = requestAnimationFrame(tick);
    };
    tick();
    window.addEventListener("resize", () => {
      cancelAnimationFrame(raf);
      resize();
      tick();
    });
    document.addEventListener("geo:theme", () => { colors = themeColors(); });
  }

  /* -------- Graph TOC -------- */
  function mountGraph() {
    const wrap = $(".graph-toc .canvas-wrap");
    if (!wrap) return;
    const c = wrap.querySelector("canvas");
    const ctx = c.getContext("2d");
    const SECTIONS = window.GEO_SECTIONS || [];
    if (!SECTIONS.length) return;
    let W = 0,
      H = 0,
      dpr = Math.min(2, window.devicePixelRatio || 1);
    let t = 0,
      raf;
    let colors = themeColors();
    function resize() {
      const r = c.getBoundingClientRect();
      W = r.width;
      H = r.height || 420;
      c.width = W * dpr;
      c.height = H * dpr;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);
    }
    function paint() {
      resize();
      ctx.clearRect(0, 0, W, H);
      const cx = W / 2,
        cy = H / 2;
      ctx.strokeStyle = colors.graphRingStroke;
      [120, 170, 220].forEach((r) => {
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, 7);
        ctx.stroke();
      });
      SECTIONS.forEach((s) => {
        const a = s.angle + (reduced ? 0 : t * 0.0003);
        const x = cx + Math.cos(a) * s.r,
          y = cy + Math.sin(a) * s.r;
        ctx.strokeStyle = colors.graphLinkStroke;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(x, y);
        ctx.stroke();
        for (let i = 0; i < Math.min(s.count, 6); i++) {
          const sa = a + (i - 2.5) * 0.18;
          const sr = s.r + 40 + (i % 2) * 14;
          const sx = cx + Math.cos(sa) * sr,
            sy = cy + Math.sin(sa) * sr;
          ctx.strokeStyle = colors.graphSubStroke;
          ctx.beginPath();
          ctx.moveTo(x, y);
          ctx.lineTo(sx, sy);
          ctx.stroke();
          ctx.fillStyle = s.color + "aa";
          ctx.beginPath();
          ctx.arc(sx, sy, 1.6, 0, 7);
          ctx.fill();
        }
      });
      ctx.fillStyle = colors.graphCenterFill;
      ctx.shadowColor = colors.graphCenterShadow;
      ctx.shadowBlur = 18;
      ctx.beginPath();
      ctx.arc(cx, cy, 5, 0, 7);
      ctx.fill();
      ctx.shadowBlur = 0;
      ctx.fillStyle = colors.graphCenterLabel;
      ctx.font = "10px IBM Plex Mono, monospace";
      ctx.textAlign = "center";
      ctx.fillText("GEO 白皮书", cx, cy + 22);
      SECTIONS.forEach((s) => {
        const a = s.angle + (reduced ? 0 : t * 0.0003);
        const x = cx + Math.cos(a) * s.r,
          y = cy + Math.sin(a) * s.r;
        ctx.fillStyle = s.color;
        ctx.shadowColor = s.color + "88";
        ctx.shadowBlur = 12;
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, 7);
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.fillStyle = colors.graphLabel;
        ctx.font = "11px IBM Plex Mono, monospace";
        const align = Math.cos(a) >= 0 ? "left" : "right";
        ctx.textAlign = align;
        const tx = x + (Math.cos(a) >= 0 ? 10 : -10);
        ctx.fillText(s.id + " · " + s.name, tx, y + 4);
      });
      if (!reduced) {
        t += 16;
        raf = requestAnimationFrame(paint);
      }
    }
    paint();
    window.addEventListener("resize", () => {
      cancelAnimationFrame(raf);
      paint();
    });
    document.addEventListener("geo:theme", () => { colors = themeColors(); if (reduced) paint(); });
  }

  /* -------- Boot -------- */
  document.addEventListener("DOMContentLoaded", () => {
    mountThemeToggle();
    mountDrawer();
    mountPalette();
    mountProgress();
    mountOutline();
    mountParticles();
    mountGraph();
  });
})();
