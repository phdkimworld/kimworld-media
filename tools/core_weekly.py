# 월요일 핵심 종목 주간 갱신 표(권고안 5장)를 한 번에 만든다(93회차 PLUG 11-16, vidIQ 없이 STATE.md 롱폼 ID + stats_snapshots.jsonl 마지막 줄).
# 사용: python3 tools/core_weekly.py [끝 날짜 MM-DD, 기본 어제(ET)]  → 지난 2주 롱폼을 핵심/새 종목으로 나눈 표 + 넣기·빼기 후보
import json, re, statistics, sys, os, datetime as dt
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, 'tools')
from core_tickers import load as _load  # noqa
core = set(_load())
end = dt.datetime.strptime('2026-' + sys.argv[1], '%Y-%m-%d') if len(sys.argv) > 1 else dt.datetime.utcnow() - dt.timedelta(hours=29)
start = end - dt.timedelta(days=13); wk = end - dt.timedelta(days=6)
md = lambda d: d.strftime('%m-%d')
last = json.loads(open('stats_snapshots.jsonl').readlines()[-1])
views = last['v']; rows = []
for line in open('production/STATE.md', encoding='utf-8'):
    m = re.match(r'\| (\d\d-\d\d) \|[^|]*\| ([^|]*)\|[^|]*\| ([^|]*)\|', line)
    if not m or not md(start) <= m.group(1) <= md(end): continue
    tk = re.match(r'\s*([A-Z]{2,5})', m.group(2)); lid = re.search(r'(?:롱폼|영상) ([A-Za-z0-9_-]{11})', m.group(3))
    if tk and lid: rows.append((m.group(1), tk.group(1), lid.group(1), views.get(lid.group(1))))
print(f"스냅숏 {last['t'][:16]}Z · 롱폼 {md(start)}~{md(end)} {len(rows)}편")
for name, g in (('핵심 종목', [r for r in rows if r[1] in core]), ('새 종목·기타', [r for r in rows if r[1] not in core])):
    v = [r[3] for r in g if r[3] is not None]
    print(f"| {name} | {len(g)} | {sum(v):,} | {statistics.median(v) if v else '-'} |")
print('넣기 후보(새 종목 300회+):', ', '.join(f'{r[1]} {r[3]}' for r in rows if r[1] not in core and (r[3] or 0) >= 300) or '없음')
best = {}
for r in rows:
    if r[0] >= md(wk) and r[1] in core: best[r[1]] = max(best.get(r[1], 0), r[3] or 0)
print('지난주 100회 미만(빼기 연속 주수 +1):', ', '.join(f'{t} {best.get(t, "롱폼 없음")}' for t in sorted(core) if best.get(t, 0) < 100) or '없음')
