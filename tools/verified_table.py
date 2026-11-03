#!/usr/bin/env python3
"""검증 종목 표(운영자 지시 11-03 "실시간 트래픽을 항상 최우선으로 검증"): 정규 선정 전에 반드시 돌린다.
1) yt_stats.py로 지금 조회 수를 새로 받는다(--no-refresh로 생략 가능) 2) report_perf.py의 7일 페이지뷰를 읽는다
3) 종목별 점수 = 연결 롱폼 누적 조회 + 7일 페이지뷰×10, 최신 data_as_of와 경과일·적격(7일 이상)을 표로 낸다.
사용: python3 tools/verified_table.py [--no-refresh] [--top 20] [--ticker AEHR]
"""
import json, glob, re, subprocess, sys, datetime, os
HERE = os.path.dirname(os.path.abspath(__file__)); MEDIA = os.path.dirname(HERE)
SITE = os.path.join(os.path.dirname(MEDIA), 'kimworld-site')
args = sys.argv[1:]
top = int(args[args.index('--top')+1]) if '--top' in args else 20
want = args[args.index('--ticker')+1].upper() if '--ticker' in args else None
if '--no-refresh' not in args:
    subprocess.run(['python3', os.path.join(HERE, 'yt_stats.py')], cwd=MEDIA, capture_output=True, timeout=300)
snap = json.loads(open(os.path.join(MEDIA, 'stats_snapshots.jsonl')).readlines()[-1])
v = snap['v']
out = subprocess.run(['python3', os.path.join(HERE, 'report_perf.py')], cwd=MEDIA, capture_output=True, text=True, timeout=300).stdout
pv = {}
for l in out.splitlines():
    m = re.match(r'\s+([a-z0-9.-]+-20\d\d-\d\d(?:-\d+)?)\s+(\d+)\s', l)
    if m: pv.setdefault(m.group(1), int(m.group(2)))
agg = {}
for f in glob.glob(os.path.join(SITE, 'content/reports/*.md')):
    t = open(f).read(4000)
    tk = re.search(r'^ticker:\s*(\S+)', t, re.M)
    if not tk: continue
    tk = tk.group(1).strip("'\"")
    y = re.search(r"^youtube_id:\s*['\"]?([\w-]+)", t, re.M)
    d = re.search(r"^data_as_of:\s*['\"]?(\d{4}-\d\d-\d\d)", t, re.M)
    slug = os.path.basename(f)[:-3]
    a = agg.setdefault(tk, {'views': 0, 'pv': 0, 'latest': ''})
    if y: a['views'] += v.get(y.group(1), 0)
    a['pv'] += pv.get(slug, 0)
    if d and d.group(1) > a['latest']: a['latest'] = d.group(1)
today = datetime.date.today()
rows = sorted(((x['views'] + x['pv']*10, k, x['views'], x['pv'], x['latest']) for k, x in agg.items()), reverse=True)
print(f"검증 종목 표 · 조회 스냅샷 {snap['t'][:16]}Z · 점수=롱폼 누적 조회+7일 페이지뷰×10")
print("순위 | 종목 | 점수 | 조회 | 7일PV | 최신 기준일 | 경과일 | 정규 적격(7일↑)")
for i, (s, k, vw, p, lt) in enumerate(rows, 1):
    if i > top and k != want: continue
    age = (today - datetime.date.fromisoformat(lt)).days if lt else 999
    print(f"{i} | {k} | {s} | {vw} | {p} | {lt} | {age} | {'적격' if age >= 7 else '-'}")
