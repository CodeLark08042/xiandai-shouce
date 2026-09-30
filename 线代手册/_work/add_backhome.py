# -*- coding: utf-8 -*-
"""
给 6 个章节 HTML 的侧栏顶部统一插入「← 返回总索引」链接。
- 链接指向同级 线代总索引.html（相对路径，本地双击与线上 GitHub Pages 均有效）
- 幂等：已含「返回总索引」的文件跳过，不会重复插入
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
BACK = ('  <a href="线代总索引.html" style="display:block;margin:0 14px 12px;'
        'text-align:center;font-size:13px;color:#9fb4cc;border:1px solid #3d5a7a;'
        'border-radius:4px;padding:6px 8px;text-decoration:none">← 返回总索引</a>\n')

for fname in FILES:
    p = BASE / fname
    s = p.read_text(encoding="utf-8")
    m = re.search(r'<(?:nav|aside) class="sidebar">', s)
    if not m:
        print("SKIP(无sidebar):", fname)
        continue
    if "返回总索引" in s:
        print("SKIP(已存在):", fname)
        continue
    pos = m.end()
    s = s[:pos] + "\n" + BACK + s[pos:]
    p.write_text(s, encoding="utf-8")
    print("OK:", fname)
