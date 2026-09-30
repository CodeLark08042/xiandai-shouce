import pathlib
p = pathlib.Path(r"D:\考研学习\数学\27考研数学真题真刷\产物整理\线代手册\线代手册_发布版.html")
s = p.read_text(encoding="utf-8")
s = s.replace("getElementById('home_heatmap')", "getElementById('heatmap')")
s = s.replace("getElementById('home_bar')", "getElementById('bar')")
p.write_text(s, encoding="utf-8")
print("fixed")
