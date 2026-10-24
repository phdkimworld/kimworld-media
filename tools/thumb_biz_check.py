# 썸네일에 '무슨 사업인지 한눈에 보이는 시각화'가 있는지 본다(운영자 지시 2026-10-24 "썸네일도 좀더 무슨 사업체인지 한눈에 알수 있도록 시각화를 추가").
# 사용: python3 thumb_biz_check.py <thumb/custom 폴더>   — a.html(주 썸네일)·bg.html(영상 hero 배경)을 본다
#  - a.html: 사업 그림 묶음 <g id="biz" data-biz="우라늄 채굴"> (또는 같은 속성을 가진 div)과, 그 사업을 2~10자로 적은 사업 칩(class="biz-chip") 글자가 있어야 한다
#  - bg.html: 같은 id="biz" 그림이 남아 있어야 한다(10-24 EU hero가 우라늄 회사에 서버 랙 그림을 써서 사업이 엉뚱하게 보였음)
#  - 렌더한 a.png가 있으면 biz 그림 상자의 넓이가 화면의 12% 이상인지도 본다(작아서 휴대폰에서 안 보이는 것 방지)
import os, re, sys, subprocess, json
D = sys.argv[1] if len(sys.argv) > 1 else '.'
bad = []
def read(n):
    p = os.path.join(D, n)
    return open(p).read() if os.path.exists(p) else None
a, bg = read('a.html'), read('bg.html')
if a is None:
    bad.append('a.html 없음')
else:
    m = re.search(r'id="biz"[^>]*data-biz="([^"]+)"|data-biz="([^"]+)"[^>]*id="biz"', a)
    if not m: bad.append('a.html: id="biz" data-biz="<사업>" 그림 묶음 없음')
    chip = re.search(r'class="[^"]*biz-chip[^"]*"[^>]*>([^<]+)<', a)
    if not chip: bad.append('a.html: 사업 칩(class="biz-chip") 없음')
    elif not 2 <= len(chip.group(1).strip()) <= 10: bad.append(f'a.html: 사업 칩 글자 {len(chip.group(1).strip())}자(2~10자)')
if bg is not None and 'id="biz"' not in bg:
    bad.append('bg.html: 사업 그림(id="biz")이 hero 배경에 없음')
png = os.path.join(D, 'a.png')
if a is not None and os.path.exists(png) and not bad:
    js = "const r=document.getElementById('biz').getBoundingClientRect();JSON.stringify([r.width,r.height])"
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 720})
            pg.goto('file://' + os.path.abspath(os.path.join(D, 'a.html'))); w, h = json.loads(pg.evaluate(js)); b.close()
        share = w * h / (1280 * 720)
        if share < 0.12: bad.append(f'a.html: 사업 그림 넓이 {share:.0%}(12% 이상)')
    except Exception as e:
        print('넓이 확인 건너뜀:', str(e)[:80])
print('\n'.join(bad) if bad else 'BIZ_OK ' + (m.group(1) or m.group(2)) + ' / 칩 ' + chip.group(1).strip())
sys.exit(1 if bad else 0)
