# 리포트·대본 속 'M월 D일 종가 X달러'를 나스닥 공식 종가와 맞대 본다(91회차 SMR: 60회차가 실적 날 장 마감 직후 값 4.41달러를 종가로 적었고 공식 종가는 4.37달러였다).
# 사용: python3 tools/close_check.py <리포트.md> <티커> [연도=2026]
#  - 같은 문장에서 'M월 D일 종가(는) X달러' 또는 'M월 D일 … 종가 X달러'를 찾아 그날 나스닥 종가와 0.5% 넘게 다르면 CLOSE_DIFF
#  - 미국 주식만(코인은 건너뜀). 나스닥 API가 막히면 CLOSE_SKIP(실패로 치지 않음)
import json, re, subprocess, sys
p, tk = sys.argv[1], sys.argv[2].upper(); yr = sys.argv[3] if len(sys.argv) > 3 else '2026'
txt = open(p, encoding='utf-8').read()
try:
    out = subprocess.run(['curl', '-s', '-A', 'Mozilla/5.0 research', f'https://api.nasdaq.com/api/quote/{tk}/historical?assetclass=stocks&fromdate={int(yr)-1}-01-01&limit=9999'], capture_output=True, timeout=60).stdout
    rows = json.loads(out)['data']['tradesTable']['rows']
    C = {r['date']: float(r['close'].strip('$').replace(',', '')) for r in rows}
except Exception as e:
    print('CLOSE_SKIP', e); sys.exit(0)
bad = []; n = 0
for sen in re.split(r'(?<=[.?!])\s+|\n', txt):
    for m in re.finditer(r'(\d{1,2})월 (\d{1,2})일(?: 정규장)? 종가(?:는|가|인)? (\d+(?:\.\d+)?)달러', sen):
        mo, d, v = int(m.group(1)), int(m.group(2)), float(m.group(3))
        k = f'{mo:02d}/{d:02d}/{yr}'
        if k not in C: continue
        n += 1
        if abs(v / C[k] - 1) > 0.005: bad.append(f'{mo}월 {d}일 종가 {v}달러 ≠ 나스닥 {C[k]}달러: {sen.strip()[:60]}')
print('\n'.join('CLOSE_DIFF ' + b for b in bad) if bad else f'CLOSE_OK {n}개')
sys.exit(1 if bad else 0)
