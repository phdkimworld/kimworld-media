# 썸네일 시안(thumb/custom/a.html·b.html) 'AI 티' 정적 검사 — 브라우저 없이 HTML만 읽는다(skill/runbooks/taste.md 13절, 11-27).
# 출처: impeccable(pbakaus/impeccable, Apache-2.0) 탐지 규칙 gradient-text·flat-type-hierarchy,
#       unslop(heydamir/unslop, CC BY 4.0, Damir Sokolovsky) signs.md 'Type·Copy'를 우리 썸네일(V5.7 글자색 둘)에 맞게 옮김. 코드는 가져오지 않았다.
# 사용: python3 tools/thumb_taste_check.py <thumb/custom 폴더>
#  - THUMB_GRADTEXT (실패): 글자에 그라데이션 채움(background-clip:text·text-fill-color:transparent·<text fill="url(#…)">)
#  - THUMB_COLORS   (실패): 글자 요소(.t) 색 계열 4개 이상(흰색 계열은 하나로 셈). V5.7 '글자색 둘', 11-24 이후 시안은 2~3
#  - THUMB_BANG     (실패): 화면 글자에 느낌표
#  - THUMB_FLAT     (경고): 가장 큰 글자와 둘째 크기 비가 1.25배 미만(위계 없음)
#  - THUMB_V8_POS   (실패): V8 틀(<body data-layout="v8">, 11-28~ taste.md 15절)의 고정 위치가 어긋남 — 인용 (40,34), 글자 상자 (32,456,828×236)
#                          + 상자 오른쪽 끝 880 초과(재생 시간 자리), 인용 따옴표 안 22자 초과
# 기준: 2026-11-27 최근 30시안 — 그라데이션 글자 0, 느낌표 0, 4계열은 V5.7 전 b안 대부분(11-23 이전), 11-24 이후 6회차 0 · 1.25배 미만 경고 2(wk1122·joby1124 b).
import sys, os, re, glob, colorsys

def family(c):
    c = c.strip().lower()
    m = re.fullmatch(r'#([0-9a-f]{3}|[0-9a-f]{6})', c)
    if not m:
        return 'white' if c in ('white', '#fff', '#ffffff') else c
    h = m.group(1)
    if len(h) == 3: h = ''.join(x * 2 for x in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    if l > 0.85 and s < 0.6 or l > 0.93: return 'white'  # 흰색·연회색(#e6edf5·#e2e8f0)
    return 'h%d' % (round(hh * 12) % 12)  # 30도 단위 색상

fails, warns = [], []
D = sys.argv[1]
for h in sorted(glob.glob(os.path.join(D, '[ab].html'))):
    s = open(h, encoding='utf-8').read(); n = os.path.basename(h)
    if re.search(r'background-clip:\s*text|text-fill-color:\s*transparent|<text[^>]*fill="url\(', s):
        fails.append(f'{n} THUMB_GRADTEXT 글자 그라데이션 — 단색 글자(효과를 쌓을수록 휴대폰 목록에서 흐려짐)')
    body = s.split('</style>', 1)[-1]
    ts = re.findall(r'<div class="t[^"]*"[^>]*style="([^"]*)"[^>]*>(.*?)</div>', body, re.S)
    cols, sizes, txt = set(), set(), ''
    for st, inner in ts:
        c = re.search(r'(?<![-\w])color:\s*([^;]+)', st); f = re.search(r'font-size:\s*(\d+)', st)
        if c: cols.add(family(c.group(1)))
        if f: sizes.add(int(f.group(1)))
        for sc in re.findall(r'style="[^"]*?(?<![-\w])color:\s*([^;"]+)', inner): cols.add(family(sc))
        txt += re.sub('<[^>]+>', '', inner)
    if len(cols) >= 4: fails.append(f'{n} THUMB_COLORS 글자색 {len(cols)}계열 ≥ 4 — 흰색 + 강조 하나(V5.7), 좋은·나쁜 숫자 색 나눔만 예외')
    if '!' in txt or '！' in txt: fails.append(f'{n} THUMB_BANG 느낌표 — 평서 문구로')
    if 'data-layout="v8"' in s:
        qm = re.search(r'<div class="t q[^"]*"[^>]*style="left:(\d+)px;top:(\d+)px[^"]*"[^>]*>"([^<]*)"</div>', body)
        bm = re.search(r'<div class="box" id="tbox" style="left:(\d+)px;top:(\d+)px;width:(\d+)px;height:(\d+)px"', body)
        if not qm: fails.append(f'{n} THUMB_V8_POS 인용 줄 없음 — 왼쪽 위 "…" 한 줄')
        else:
            if (int(qm.group(1)), int(qm.group(2))) != (40, 34): fails.append(f'{n} THUMB_V8_POS 인용 위치 ({qm.group(1)},{qm.group(2)}) ≠ (40,34)')
            ql = len(re.sub(r'&[a-z]+;|&#\d+;', 'x', qm.group(3)))
            if ql > 22: fails.append(f'{n} THUMB_V8_POS 인용 {ql}자 > 22자')
        if not bm: fails.append(f'{n} THUMB_V8_POS 글자 상자(#tbox) 없음')
        else:
            x, y, w, h = map(int, bm.groups())
            if (x, y, w, h) != (32, 456, 828, 236): fails.append(f'{n} THUMB_V8_POS 글자 상자 ({x},{y},{w}×{h}) ≠ (32,456,828×236)')
            if x + w > 880: fails.append(f'{n} THUMB_V8_POS 글자 상자 오른쪽 끝 {x + w} > 880(재생 시간 자리)')
    sz = sorted(sizes, reverse=True)
    if len(sz) >= 2 and sz[0] / sz[1] < 1.25: warns.append(f'{n} THUMB_FLAT 큰 글자 {sz[0]}px / 둘째 {sz[1]}px = {sz[0] / sz[1]:.2f}배 < 1.25 — 주인공 한 줄을 더 크게')
for m in fails: print('FAIL', m)
for m in warns: print('WARN', m)
print('THUMB_TASTE_FAIL' if fails else 'THUMB_TASTE_OK (경고 %d)' % len(warns))
sys.exit(1 if fails else 0)
