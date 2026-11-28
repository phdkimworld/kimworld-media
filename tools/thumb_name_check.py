# 썸네일에 회사명과 티커가 크게 보이는지 본다(운영자 지시 2026-10-27 "썸네일에 회사명과 티커가 더 크게 보여야 돼").
# 사용: python3 thumb_name_check.py <thumb/custom 폴더> [회사명] [티커]
#   회사명·티커를 안 주면 ../../slides.json의 name·ticker를 쓴다.
#  - a.html(주 썸네일)과 b.html(있으면): class="name-tag" 요소에 회사명, class="ticker-tag" 요소에 티커가 있어야 한다
#  - 렌더 크기: name-tag 글자 72px 이상, ticker-tag 글자 60px 이상(1280×720 기준, 휴대폰 목록에서 읽히는 크기)
#  - 두 요소 모두 화면 위쪽 절반 안(top < 360)에 있어야 한다
#  - V8 틀(<body data-layout="v8">, 11-28 운영자 승인, taste.md 15절): 회사명은 아래 글자 상자 1줄(종목명 + 숫자)에 56px 이상,
#    티커는 상자 위 테두리 칩 36px 이상. 위·아래 위치 조건 대신 둘 다 글자 상자(#tbox) 근처(top ≥ 400)에 있어야 한다
import os, re, sys, json
D = sys.argv[1] if len(sys.argv) > 1 else '.'
name, tick = (sys.argv[2:4] + [None, None])[:2]
if not name or not tick:
    sj = os.path.join(D, '..', '..', 'slides.json')
    if os.path.exists(sj):
        d = json.load(open(sj, encoding='utf-8')); name = name or d.get('name'); tick = tick or d.get('ticker')
bad = []
files = [f for f in ('a.html', 'b.html') if os.path.exists(os.path.join(D, f))]
if 'a.html' not in files: bad.append('a.html 없음')
JS = """() => { const g = c => { const e = document.querySelector('.' + c); if (!e) return null;
  const r = e.getBoundingClientRect(); return {t: e.textContent.trim(), fs: parseFloat(getComputedStyle(e).fontSize), top: r.top, h: r.height}; };
  return {n: g('name-tag'), k: g('ticker-tag'), v8: document.body.dataset.layout === 'v8'}; }"""
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 720})
        for f in files:
            pg.goto('file://' + os.path.abspath(os.path.join(D, f))); r = pg.evaluate(JS)
            n, k = r['n'], r['k']
            v8 = r.get('v8'); nmin, kmin = (56, 36) if v8 else (72, 60)
            pos_bad = (lambda top: top < 400) if v8 else (lambda top: top >= 360)
            where = '글자 상자 밖에 있음' if v8 else '화면 아래 절반에 있음'
            if not n: bad.append(f'{f}: 회사명 요소(class="name-tag") 없음')
            else:
                if name and name.replace(' ', '') not in n['t'].replace(' ', ''): bad.append(f"{f}: name-tag '{n['t']}'에 회사명 '{name}' 없음")
                if n['fs'] < nmin: bad.append(f"{f}: 회사명 글자 {n['fs']:.0f}px({nmin}px 이상)")
                if pos_bad(n['top']): bad.append(f'{f}: 회사명이 {where}')
            if not k: bad.append(f'{f}: 티커 요소(class="ticker-tag") 없음')
            else:
                if tick and tick not in k['t']: bad.append(f"{f}: ticker-tag '{k['t']}'에 티커 '{tick}' 없음")
                if k['fs'] < kmin: bad.append(f"{f}: 티커 글자 {k['fs']:.0f}px({kmin}px 이상)")
                if pos_bad(k['top']): bad.append(f'{f}: 티커가 {where}')
        b.close()
except ImportError:
    bad.append('playwright 없음')
print('\n'.join(bad) if bad else f'NAME_OK {name} {tick}')
sys.exit(1 if bad else 0)
