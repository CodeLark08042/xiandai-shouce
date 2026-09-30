# -*- coding: utf-8 -*-
"""
把 7 个独立 HTML（总索引 + 6 章）合并成一个自包含的单页应用，
用于发布到豆包工作（doubao-html）。
"""
import re, os, json, pathlib

BASE = pathlib.Path(r"D:\考研学习\数学\27考研数学真题真刷\产物整理\线代手册")
OUT = BASE / "线代手册_发布版.html"

CHAPTERS = [
    ("L1", "线代L1行列式题型全解手册.html", "行列式", 18),
    ("L2", "线代L2矩阵题型全解手册.html", "矩阵", 36),
    ("L3", "线代L3向量题型全解手册.html", "向量（含数一专属向量空间）", 32),
    ("L4", "线代L4线性方程组题型全解手册.html", "线性方程组", 35),
    ("L5", "线代L5特征值与相似对角化题型全解手册.html", "特征值与相似对角化", 34),
    ("L6", "线代L6二次型题型全解手册.html", "二次型", 27),
]

def read(p):
    return p.read_text(encoding="utf-8")

def extract_style(html):
    m = re.search(r"<style>(.*?)</style>", html, re.S)
    return m.group(1) if m else ""

def extract_body_main(html):
    """抽 body 里 .main 容器内的内容；去掉 sidebar、backtop、script。"""
    # 去掉 script 块
    body = re.search(r"<body>(.*?)</body>", html, re.S).group(1)
    body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
    # 去掉 sidebar nav
    body = re.sub(r"<nav class=\"sidebar\">.*?</nav>", "", body, flags=re.S)
    # 去掉 backtop
    body = re.sub(r'<a href="#top" class="backtop">.*?</a>', "", body, flags=re.S)
    # 尝试抽 .main 容器
    m = re.search(r'<div class="main">(.*)</div>\s*$', body.strip(), re.S)
    if m:
        return m.group(1).strip()
    return body.strip()

def extract_echarts_script(html):
    """抽最后的 <script>...</script> 里的 ECharts 代码。"""
    scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
    out = []
    for s in scripts:
        if "echarts" in s or "getElementById" in s:
            out.append(s)
    return "\n".join(out)

def prefix_ids(content, prefix):
    """给 id="xxx" 加前缀，并把 getElementById('xxx') 同步替换。"""
    def repl_id(m):
        return f'id="{prefix}_{m.group(1)}"'
    content = re.sub(r'id="([^"]+)"', repl_id, content)
    def repl_gebi(m):
        return f"getElementById('{prefix}_{m.group(1)}')"
    content = re.sub(r"getElementById\('([^']+)'\)", repl_gebi, content)
    return content

def fix_anchor_links(content, chapter_key):
    """把页内锚点 href="#xxx" 改写成带章前缀的 hash 路由形式 #/Lx#xxx。
    简化：保持原 #xxx 锚点，但因为切章后同一 view 内锚点仍有效，直接保留。
    这里只处理跨章的文件名链接。"""
    # 把 href="线代Lx...html" 改成 hash 路由（章节内部一般没有这种链接）
    for k, _, _, _ in CHAPTERS:
        content = re.sub(r'href="线代L\d[^"]*\.html"', f'href="#/{k}"', content)
    return content

# ========== 读取所有章节 ==========
styles = []
views_html = []
init_funcs = []
side_navs = []  # 每章的二级目录

for key, fname, name, cnt in CHAPTERS:
    html = read(BASE / fname)
    styles.append(f"/* === {key} === */\n" + extract_style(html))
    main = extract_body_main(html)
    main = prefix_ids(main, key)
    main = fix_anchor_links(main, key)
    views_html.append(f'<section class="view" id="view-{key}" hidden>{main}</section>')

    ec = extract_echarts_script(html)
    ec = prefix_ids(ec, key)
    # 包成函数
    init_funcs.append(f"""
function initCharts_{key}() {{
  if (typeof echarts === 'undefined') return;
  try {{
{ec}
  }} catch(e) {{ console.error('{key} charts:', e); }}
}}
""")

# 抽总索引
idx_html = read(BASE / "线代总索引.html")
styles.append("/* === INDEX === */\n" + extract_style(idx_html))
idx_body = re.search(r"<body>(.*?)</body>", idx_html, re.S).group(1)
idx_body = re.sub(r"<script.*?</script>", "", idx_body, flags=re.S)
# 总索引的卡片链接改成 hash 路由
for key, fname, name, cnt in CHAPTERS:
    idx_body = re.sub(r'href="线代L\d[^"]*\.html"', f'href="#/{key}"', idx_body)

views_html.insert(0, f'<section class="view" id="view-home">{idx_body}</section>')

# 总索引的 ECharts（heatmap/bar）
idx_scripts = re.findall(r"<script>(.*?)</script>", idx_html, re.S)
idx_ec = "\n".join(s for s in idx_scripts if "echarts" in s or "heatmap" in s.lower() or "getElementById" in s)
idx_ec = prefix_ids(idx_ec, "home")
init_funcs.insert(0, f"""
function initCharts_home() {{
  if (typeof echarts === 'undefined') return;
  try {{
{idx_ec}
  }} catch(e) {{ console.error('home charts:', e); }}
}}
""")

# ========== 组装 ==========
NAV_BTNS = ''.join([
    f'<button class="nav-btn" data-view="home">总索引</button>',
] + [
    f'<button class="nav-btn" data-view="{k}">{k} {n}</button>'
    for k, _, n, _ in CHAPTERS
])

CSS = """
:root{--navy:#1e3a5f;--paper:#fafaf6;--card:#fff;--accent:#d97706;--line:#e3e0d6}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{font-family:'Microsoft YaHei','PingFang SC',system-ui,sans-serif;background:var(--paper);color:#222;line-height:1.75}
.topnav{position:sticky;top:0;z-index:100;background:var(--navy);padding:10px 16px;display:flex;flex-wrap:wrap;gap:8px;box-shadow:0 2px 6px rgba(0,0,0,.15)}
.nav-btn{background:transparent;color:#dce6f1;border:1px solid rgba(255,255,255,.25);padding:6px 14px;border-radius:5px;cursor:pointer;font-size:13.5px}
.nav-btn:hover{background:rgba(255,255,255,.12);color:#fff}
.nav-btn.active{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:700}
.view{max-width:1100px;margin:0 auto;padding:24px 20px 80px}
.view[hidden]{display:none}
.back-home{display:inline-block;margin:0 0 18px;color:var(--navy);text-decoration:none;font-size:13.5px;border:1px solid var(--line);padding:5px 12px;border-radius:5px;background:#fff}
.back-home:hover{border-color:var(--navy)}
"""

JS_ROUTER = """
const INITED = {};
function switchView(key, scrollTop=true) {
  document.querySelectorAll('.view').forEach(v => v.hidden = (v.id !== 'view-' + key));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.toggle('active', b.dataset.view === key));
  if (!INITED[key]) {
    setTimeout(() => {
      try { window['initCharts_' + key] && window['initCharts_' + key](); } catch(e) {}
      INITED[key] = true;
    }, 50);
  }
  if (scrollTop) window.scrollTo({top:0, behavior:'instant'});
}
function route() {
  const h = location.hash.replace(/^#\\//, '');
  const key = h || 'home';
  const baseKey = key.split('#')[0] || 'home';
  switchView(baseKey, false);
  const anchor = key.includes('#') ? key.split('#')[1] : null;
  if (anchor) {
    setTimeout(() => {
      const el = document.getElementById(anchor);
      if (el) el.scrollIntoView({behavior:'instant'});
    }, 80);
  } else {
    window.scrollTo({top:0});
  }
}
window.addEventListener('hashchange', route);
window.addEventListener('DOMContentLoaded', route);
// MathJax 切章后重新渲染
document.addEventListener('click', e => {
  const a = e.target.closest('a[href^="#/"]');
  if (a) {
    setTimeout(() => {
      if (window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise();
    }, 200);
  }
});
"""

# MathJax 配置（CDN 版）
MATHJAX_CFG = """
window.MathJax = {
  tex: { inlineMath: [['$','$'],['\\\\(','\\\\)']], displayMath: [['$$','$$'],['\\\\[','\\\\]']] },
  svg: { fontCache: 'global' }
};
"""

out = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>考研数学（一）· 线性代数题型全解手册（1987—2025）</title>
<script>{MATHJAX_CFG}</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js" async></script>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<style>{CSS}{''.join(styles)}</style>
</head>
<body>
<nav class="topnav">{NAV_BTNS}</nav>
{''.join(views_html)}
<script>{''.join(init_funcs)}{JS_ROUTER}</script>
</body>
</html>
"""

OUT.write_text(out, encoding="utf-8")
print(f"OK: {OUT}")
print(f"size: {OUT.stat().st_size/1024:.1f} KB")
