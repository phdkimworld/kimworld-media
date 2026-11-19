# 월요일 핵심 종목 주간 갱신 표(권고안 5장)를 한 번에 만든다(93회차 PLUG 11-16, vidIQ 없이 STATE.md 롱폼 ID + stats_snapshots.jsonl 마지막 줄).
# 사용: python3 tools/core_weekly.py [끝 날짜 MM-DD, 기본 어제(ET)]  → 지난 2주 롱폼을 핵심/새 종목으로 나눈 표 + 넣기·빼기 후보
import json, re, statistics, sys, os, datetime as dt
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, 'tools')
from core_tickers import load as _load  # noqa
core = set(_load())
end = dt.datetime.strptime('2026-' + sys.argv[1], '%Y-%m-%d') if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else dt.datetime.utcnow() - dt.timedelta(hours=29)
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

# ---- 매일 갱신(운영자 11-19 "2주를 모아 보는 건 맞는데 갱신은 매일 해") ----
# --apply: 오늘(ET) 처음 한 번만, 2주 창 넣기(새 종목 롱폼 300회+)와 28일 창 빼기(그 종목 롱폼 최고가 100회 미만, 또는 28일 동안 롱폼 없음)를
#          review/core_tickers.md 표와 갱신 기록에 바로 반영하고 한 줄로 알린다. 바뀐 것이 없으면 아무것도 출력하지 않는다.
if '--apply' in sys.argv:
    import subprocess
    from zoneinfo import ZoneInfo
    today = dt.datetime.now(ZoneInfo('America/New_York')).strftime('%m-%d')
    stamp = '.cache/core_daily'; os.makedirs('.cache', exist_ok=True)
    if os.path.exists(stamp) and open(stamp).read().strip() == today: sys.exit(0)
    open(stamp, 'w').write(today)
    s28 = end - dt.timedelta(days=27); r28 = {}
    for line in open('production/STATE.md', encoding='utf-8'):
        m = re.match(r'\| (\d\d-\d\d) \|[^|]*\| ([^|]*)\|[^|]*\| ([^|]*)\|', line)
        if not m or not md(s28) <= m.group(1) <= md(end): continue
        tk = re.match(r'\s*([A-Z]{2,5})', m.group(2)); lid = re.search(r'(?:롱폼|영상) ([A-Za-z0-9_-]{11})', m.group(3))
        if tk and lid: r28[tk.group(1)] = max(r28.get(tk.group(1), 0), views.get(lid.group(1)) or 0)
    add = sorted({r[1] for r in rows if r[1] not in core and (r[3] or 0) >= 300})
    drop = sorted(t for t in core if r28.get(t, 0) < 100)
    if not add and not drop: sys.exit(0)
    p = 'review/core_tickers.md'; s = open(p, encoding='utf-8').read()
    lines = s.split('\n')
    lines = [l for l in lines if not any(re.match(r'\|\s*' + re.escape(t) + r'\s*\|', l) for t in drop)] if drop else lines
    s = '\n'.join(lines)
    for t in add:
        row = f"| {t} | {t} | (갱신 때 무리 채움) | {today} | 2주 롱폼 {max(r[3] or 0 for r in rows if r[1]==t)}회 |"
        i = s.index('\n\n시리즈 이름은'); s = s[:i] + '\n' + row + s[i:]
    s = s.rstrip('\n') + f"\n| {today}(매일) | {', '.join(add) or '-'} | {', '.join(drop) or '-'} | 2주 창 넣기 300회+ · 28일 창 빼기 최고 100회 미만(core_weekly --apply) | - |\n"
    open(p, 'w', encoding='utf-8').write(s)
    print(f"핵심 종목 갱신: 넣음 {', '.join(add) or '-'} · 뺌 {', '.join(drop) or '-'}")
