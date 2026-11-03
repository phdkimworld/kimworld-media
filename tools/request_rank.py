#!/usr/bin/env python3
"""요청 슬롯 트래픽 순위(운영자 지시 11-03 "요청종목 슬랏도 트래픽 순으로 처리해").
요청 장부 '대기'·'대기(2순위)' 행마다 점수 = 그 종목 기존 트래픽(검증 표 점수: 연결 롱폼 누적 조회 + 7일 페이지뷰×10)
 + 요청이 달린 영상의 지금 조회 수 + 요청 수(댓글 스레드 + 웹 요청 n명)×100 + 7일 사이트 검색 횟수×10.
1순위('대기')를 먼저, 그 안에서 점수 높은 순(같으면 먼저 들어온 순). 사용: python3 tools/request_rank.py [--no-refresh]
"""
import re, subprocess, sys, os, json
HERE=os.path.dirname(os.path.abspath(__file__)); MEDIA=os.path.dirname(HERE)
vt=subprocess.run(['python3',os.path.join(HERE,'verified_table.py'),'--top','9999']+(['--no-refresh'] if '--no-refresh' in sys.argv else []),capture_output=True,text=True,timeout=600).stdout
own={}
for l in vt.splitlines()[2:]:
    p=[x.strip() for x in l.split('|')]
    if len(p)>=3 and p[2].isdigit(): own[p[1].upper()]=int(p[2])
v=json.loads(open(os.path.join(MEDIA,'stats_snapshots.jsonl')).readlines()[-1])['v']
perf=subprocess.run(['python3',os.path.join(HERE,'report_perf.py')],cwd=MEDIA,capture_output=True,text=True,timeout=300).stdout
rows=[]
for l in open(os.path.join(MEDIA,'requests.md')):
    if not re.match(r'\|\s*대기',l): continue
    c=[x.strip() for x in l.strip().strip('|').split('|')]
    st,tk,name,threads,who,date=c[:6]; tier=2 if '2순위' in st else 1
    tids=[t for t in re.split(r'[ ,·]+',threads) if '@' in t]
    src=sum(v.get(t.split('@')[1],0) for t in tids if t.split('@')[1] in v)
    web=sum(int(n) for n in re.findall(r'웹 요청\s*(\d+)',l))
    srch=sum(int(n) for n in re.findall(r'검색[^|]*?(\d+)\s*회',l))
    score=own.get(tk.upper(),0)+src+(len(tids)+web)*100+srch*10
    rows.append((tier,-score,date,tk,score,own.get(tk.upper(),0),src,len(tids)+web,srch))
rows.sort()
print('순위 | 단계 | 종목 | 점수 | 종목 트래픽 | 요청 영상 조회 | 요청 수 | 검색 | 접수일')
for i,r in enumerate(rows,1): print(f"{i} | {'1순위' if r[0]==1 else '2순위'} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {r[8]} | {r[2]}")
