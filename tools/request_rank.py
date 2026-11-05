#!/usr/bin/env python3
"""요청 슬롯 트래픽 순위(운영자 지시 11-03 "요청종목 슬랏도 트래픽 순으로 처리해").
요청 장부 '대기'·'대기(2순위)' 행마다 점수 = 그 종목 기존 트래픽(검증 표 점수: 연결 롱폼 누적 조회 + 7일 페이지뷰×10)
 + 요청이 달린 영상의 지금 조회 수 + 요청 수(댓글 스레드 + 웹 요청 n명)×100 + 7일 사이트 검색 횟수×10.
1순위('대기')를 먼저, 그 안에서 점수 높은 순(같으면 먼저 들어온 순).
과거 실적 부진(운영자 지시 11-05 "이미 만든 적이 있고 과거에 트래픽 실적이 안 좋았으면 우선순위 하위로"): 그 종목의 공개 3일 지난 롱폼
편당 평균 조회가 채널 종목별 편당 평균의 중앙값 미만이면 '하위'로 단계와 상관없이 맨 아래로 보낸다. 만든 적이 없으면 영향 없음. 사용: python3 tools/request_rank.py [--no-refresh]
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
import glob, datetime
SITE=os.path.join(os.path.dirname(MEDIA),'kimworld-site'); today=datetime.date.today(); per={}
for f in glob.glob(os.path.join(SITE,'content/reports/*.md')):
    h=open(f,encoding='utf-8').read(4000)
    tk=re.search(r"^ticker:\s*['\"]?([A-Za-z0-9.]+)",h,re.M); y=re.search(r"^youtube_id:\s*['\"]?([\w-]{6,})",h,re.M); d=re.search(r"^date:\s*['\"]?(\d{4}-\d\d-\d\d)",h,re.M)
    if not (tk and y and d) or y.group(1) not in v: continue
    if (today-datetime.date.fromisoformat(d.group(1))).days<3: continue
    per.setdefault(tk.group(1).upper(),[]).append(v[y.group(1)])
avg={k:sum(x)/len(x) for k,x in per.items()}
med=sorted(avg.values())[len(avg)//2] if avg else 0
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
    low=tk.upper() in avg and avg[tk.upper()]<med
    rows.append((low,tier,-score,date,tk,score,own.get(tk.upper(),0),src,len(tids)+web,srch,round(avg.get(tk.upper(),0)) if tk.upper() in avg else '신규'))
rows.sort()
print(f'편당 평균 조회 중앙값(공개 3일 지난 롱폼, 종목 {len(avg)}개): {round(med)} — 미만이면 하위')
print('순위 | 단계 | 종목 | 점수 | 편당 평균 조회 | 종목 트래픽 | 요청 영상 조회 | 요청 수 | 검색 | 접수일')
for i,r in enumerate(rows,1): print(f"{i} | {'하위(과거 실적 부진)' if r[0] else ('1순위' if r[1]==1 else '2순위')} | {r[4]} | {r[5]} | {r[10]} | {r[6]} | {r[7]} | {r[8]} | {r[9]} | {r[3]}")
