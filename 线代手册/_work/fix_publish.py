# -*- coding: utf-8 -*-
import pathlib, re
p = pathlib.Path(r"D:\考研学习\数学\27考研数学真题真刷\产物整理\线代手册\线代手册_发布版.html")
s = p.read_text(encoding="utf-8")

# 1) 替换 initCharts_home 函数体
old_home = re.search(r"function initCharts_home\(\) \{.*?\n\}", s, re.S).group(0)
new_home = '''function initCharts_home() {
  if (typeof echarts === 'undefined') return;
  try {
    const years = [];
    for (let y = 1987; y <= 2025; y++) years.push(String(y));
    const cNames = ['L1 行列式','L2 矩阵','L3 向量','L4 方程组','L5 特征值','L6 二次型'];
    const M = {
      L1:[1,1,1,0,1,0,0,1,1,1,0,0,1,0,0,0,0,0,1,1,1,0,0,0,0,0,1,1,1,1,1,0,1,0,1,1,0,0,0,0],
      L2:[1,1,1,1,2,1,1,1,2,2,2,1,0,1,1,0,0,1,1,1,1,2,0,0,0,0,0,1,1,0,1,1,1,1,1,1,1,0,0,1],
      L3:[1,1,0,1,1,1,1,1,0,0,2,1,0,1,0,0,2,1,1,1,1,0,1,1,1,1,1,1,0,1,0,1,1,1,1,2,1,1,1,0],
      L4:[1,0,1,1,0,1,1,1,0,0,0,1,0,1,1,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,0,0,1,0,1,1,3],
      L5:[1,1,1,0,0,1,0,0,1,0,1,1,2,1,1,1,1,1,1,0,1,1,1,0,1,1,1,1,2,1,1,1,1,1,1,1,1,1,2,0],
      L6:[0,0,0,1,1,0,1,0,0,1,0,1,1,0,1,1,0,0,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1]
    };
    const hData = [];
    ['L1','L2','L3','L4','L5','L6'].forEach((ck, ci) => {
      M[ck].forEach((v, yi) => { if (v > 0) hData.push([yi, ci, v]); });
    });
    const heatEl = document.getElementById('home_heatmap');
    if (heatEl) echarts.init(heatEl).setOption({
      tooltip:{position:'top', formatter:p=>cNames[p.value[1]]+' · '+years[p.value[0]]+' 年：'+p.value[2]+' 题'},
      grid:{height:'68%', top:'8%', left:'90'},
      xAxis:{type:'category', data:years, axisLabel:{rotate:45, fontSize:10}},
      yAxis:{type:'category', data:cNames},
      visualMap:{min:0, max:3, calculable:true, orient:'horizontal', left:'center', bottom:'2%',
        inRange:{color:['#e8eef5','#7a9cc0','#1e3a5f']}},
      series:[{type:'heatmap', data:hData}]
    });
    const barEl = document.getElementById('home_bar');
    if (barEl) echarts.init(barEl).setOption({
      tooltip:{trigger:'axis'},
      grid:{left:50, right:20, bottom:40, top:30},
      xAxis:{type:'category', data:cNames},
      yAxis:{type:'value', name:'题数'},
      series:[{type:'bar', data:[18,36,32,35,34,27], itemStyle:{color:'#1e3a5f'}, label:{show:true, position:'top'}}]
    });
  } catch(e) { console.error('home charts:', e); }
}'''
s = s.replace(old_home, new_home)

# 2) 给导航按钮绑 click（在 route 函数后加一段）
old_route_end = "window.addEventListener('DOMContentLoaded', route);"
new_route_end = """window.addEventListener('DOMContentLoaded', route);
// 导航按钮点击切章
document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const v = btn.dataset.view;
    location.hash = '#/' + v;
  });
});"""
s = s.replace(old_route_end, new_route_end)

# 3) 加 favicon（在 <head> 里第一个 <script> 前）
old_head = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
new_head = '''<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%231e3a5f'/%3E%3Ctext x='32' y='44' font-size='32' text-anchor='middle' fill='white' font-family='sans-serif' font-weight='bold'%3EA%3C/text%3E%3C/svg%3E">'''
s = s.replace(old_head, new_head, 1)

p.write_text(s, encoding="utf-8")
print("OK, size:", len(s)/1024, "KB")
