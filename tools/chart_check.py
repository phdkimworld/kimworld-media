# 리포트 대표 차트(chart.json)의 날짜·종가·'N거래일' 라벨을 시세 원자료로 대조한다.
# 2026-10-27 SNDK 42회차: 차트 라벨 '9거래일'이 실제 7거래일이라 발행 직전 손으로 고침 → 자동 검사로 바꿈.
# 사용: python3 chart_check.py <chart.json> <나스닥 historical JSON>  (코인 등 원자료가 다르면 건너뛴다)
import json, sys, re, datetime
c = json.load(open(sys.argv[1], encoding='utf-8'))
try: rows = json.load(open(sys.argv[2]))['data']['tradesTable']['rows']
except Exception: print('CHART_SKIP 나스닥 원자료가 아님'); sys.exit(0)
px = {datetime.datetime.strptime(r['date'], '%m/%d/%Y').date(): float(r['close'].strip('$').replace(',', '')) for r in rows}
days = sorted(px); bad = []
def d(s):
    a = s.split('.')
    if len(a) == 2 and len(a[0]) == 4: return None  # 'YYYY.MM' 월 단위 행은 대조하지 않음
    if len(a) == 2:  # 'MM.DD' → 원자료 마지막 해(미래면 전년)
        y = days[-1].year; t = datetime.date(y, int(a[0]), int(a[1]))
        return t if t <= days[-1] else datetime.date(y - 1, int(a[0]), int(a[1]))
    y = int(a[0]); return datetime.date(y if y > 1000 else 2000 + y, int(a[1]), int(a[2]))
prev = None
for r in c['rows']:
    try: dt = d(r[0])
    except Exception: bad.append(f'날짜 형식 {r[0]}'); continue
    if dt is None: prev = None; continue
    if dt not in px: bad.append(f'{r[0]} 거래일 아님/시세 없음')
    elif abs(px[dt] - r[2]) > 0.006 * max(1, r[2]): bad.append(f'{r[0]} 종가 {r[2]} ≠ 원자료 {px[dt]}')
    m = re.search(r'(\d+)거래일', r[1])
    if m and prev and dt in px and prev in px:
        n = days.index(dt) - days.index(prev)
        if n != int(m[1]): bad.append(f'{r[0]} 라벨 {m[0]} ≠ 직전 행부터 {n}거래일')
    prev = dt
print('CHART_FAIL\n- ' + '\n- '.join(bad) if bad else f'CHART_OK {len(c["rows"])}행')
sys.exit(1 if bad else 0)
