#!/usr/bin/env python3
"""요청 슬롯 트래픽 순위(운영자 지시 11-03 "요청종목 슬랏도 트래픽 순으로 처리해").
요청 장부 '대기'·'대기(2순위)' 행마다 점수 = 그 종목 기존 트래픽(검증 표 점수: 연결 롱폼 누적 조회 + 7일 페이지뷰×10)
 + 요청이 달린 영상의 지금 조회 수 + 요청 수(댓글 스레드 + 웹 요청 n명)×100 + 7일 사이트 검색 횟수×10.
0순위('대기(0순위)': 운영자 11-09 '레거시 성적 좋은 종목 소진될 때까지 요청 0순위', 점수에 레거시 조회 합을 더함) → 1순위('대기') → 2순위, 그 안에서 점수 높은 순(같으면 먼저 들어온 순).
트래픽 컷오프(운영자 지시 11-05): 이미 만든 종목은 편당 조회와 참여율이 둘 다 중앙값 이상일 때만 통과, 하나라도 미달이면 '제외(컷오프)'(11-06) — 제작 불가(tools/traffic_cut.py).
통과 종목이 하나도 없으면 그날 요청 슬롯은 정규 한 편을 더 만든다. 사용: python3 tools/request_rank.py [--no-refresh]
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
sys.path.insert(0,HERE); from traffic_cut import load, verdict
S=load()
rows=[]
for l in open(os.path.join(MEDIA,'requests.md')):
    if not re.match(r'\|\s*대기',l): continue
    c=[x.strip() for x in l.strip().strip('|').split('|')]
    st,tk,name,threads,who,date=c[:6]; tier=0 if '0순위' in st else (2 if '2순위' in st else 1)
    tids=[t for t in re.split(r'[ ,·]+',threads) if '@' in t]
    from traffic_cut import engagement, eng_points
    E=engagement()
    src=sum(v.get(t.split('@')[1],0)*(0.7+0.3*min(eng_points(t.split('@')[1],E)/max(v.get(t.split('@')[1],0),1)/S['me'],3.0) if S['me'] else 1) for t in tids if t.split('@')[1] in v); src=round(src)
    web=sum(int(n) for n in re.findall(r'웹 요청\s*(\d+)',l))
    srch=sum(int(n) for n in re.findall(r'검색[^|]*?(\d+)\s*회',l))
    legacy=sum(int(n.replace(',','')) for n in re.findall(r'레거시 조회\s*([\d,]+)',l))  # 0순위(운영자 11-09): 채널 레거시 롱폼 조회 합
    score=own.get(tk.upper(),0)+src+(len(tids)+web)*100+srch*10+legacy
    low=False  # 운영자 11-06 최종안: 컷오프 없이 트래픽 순
    rows.append((low,tier,-score,date,tk,score,own.get(tk.upper(),0),src,len(tids)+web,srch,verdict(tk,S)[1]))
rows.sort()
print("요청 순위: 점수 = 그 종목 과거 트래픽 + 요청 영상 조회 + 요청 수×100 (운영자 11-06 최종안, 컷오프 없음)")
print('순위 | 단계 | 종목 | 점수 | 편당 조회·참여·지수 | 종목 트래픽 | 요청 영상 조회 | 요청 수 | 검색 | 접수일')
for i,r in enumerate(rows,1): print(f"{i} | {'제외(컷오프)' if r[0] else ({0:'0순위',1:'1순위',2:'2순위'}[r[1]])} | {r[4]} | {r[5]} | {r[10]} | {r[6]} | {r[7]} | {r[8]} | {r[9]} | {r[3]}")
if not any(not r[0] for r in rows): print('통과한 요청 종목 없음 → 오늘 요청 슬롯은 정규 한 편 더(verified_table.py의 다음 적격 종목)')
