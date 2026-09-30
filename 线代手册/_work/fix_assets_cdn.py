# -*- coding: utf-8 -*-
"""
章节页脚本资源加固：本地 assets 优先（保证本地双击/离线可用），
加载失败时自动回退 CDN（jsdelivr → bootcdn），解决 GitHub Pages 在国内加载大 JS 慢/失败导致公式图表不渲染的问题。
- 幂等：已含 __loadCdn 的文件跳过
"""
import pathlib, re

BASE = pathlib.Path(r"D:\考研学习\数学\27考研数学真题真刷\产物整理\线代手册")
FILES = [
    "线代L1行列式题型全解手册.html",
    "线代L2矩阵题型全解手册.html",
    "线代L3向量题型全解手册.html",
    "线代L4线性方程组题型全解手册.html",
    "线代L5特征值与相似对角化题型全解手册.html",
    "线代L6二次型题型全解手册.html",
]

FN = """<script>
window.__loadCdn = (function(){
  return function(urls){
    var i = 0;
    (function next(){
      if (i >= urls.length) return;
      var s = document.createElement('script');
      s.src = urls[i++];
      s.onerror = function(){ s.remove(); next(); };
      document.head.appendChild(s);
    })();
  };
})();
</script>"""

TEX = ('<script src="../assets/tex-svg.js" onerror="this.onerror=null;window.__loadCdn('
       "['https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js',"
       "'https://cdn.bootcdn.net/ajax/libs/mathjax/3.2.2/es5/tex-svg.js']);\"></script>")

ECH = ('<script src="../assets/echarts.min.js" onerror="this.onerror=null;window.__loadCdn('
       "['https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js',"
       "'https://cdn.bootcdn.net/ajax/libs/echarts/5.4.3/echarts.min.js',"
       "'https://cdn.staticfile.org/echarts/5.4.3/echarts.min.js']);\"></script>")

for fname in FILES:
    p = BASE / fname
    s = p.read_text(encoding="utf-8")
    if "__loadCdn" in s:
        print("SKIP(已处理):", fname)
        continue
    m = re.search(r'<script src="\.\./assets/tex-svg\.js"[^>]*></script>', s)
    if not m:
        print("SKIP(无tex引用):", fname)
        continue
    s = s.replace(m.group(0), FN + "\n" + TEX, 1)
    m2 = re.search(r'<script src="\.\./assets/echarts\.min\.js"[^>]*></script>', s)
    if m2:
        s = s.replace(m2.group(0), ECH, 1)
    p.write_text(s, encoding="utf-8")
    print("OK:", fname)
