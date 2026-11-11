# 투표 보기 동기화 검사(73회차 NBIS, 72회차 LCID 실수: 롱폼 투표 보기 '국부펀드 지원 기대'가 Threads 25바이트를 넘어
# SNS 단계에서야 queue_check에 걸려 롱폼·쇼츠·캡션을 모두 고침).
# 사용: python3 poll_sync_check.py <video 폴더> [쇼츠 폴더]
#  - 롱폼 slides.json poll options, 쇼츠 shorts.json poll opts가 모두 25바이트(한글 8자) 이하인지
#  - 롱폼과 쇼츠의 보기 문구·순서가 같은지(SNS 투표에 그대로 옮겨 쓰기 위해)
# 녹음·합성 전에 돌린다(chain_long.sh). 실패하면 POLL_SYNC_FAIL과 이유.
import json, os, sys
V = sys.argv[1]; S = sys.argv[2] if len(sys.argv) > 2 else ''
bad = []; lo = []; so = []
sj = os.path.join(V, 'slides.json')
if os.path.exists(sj):
    for p in json.load(open(sj)).get('paras', []):
        for x in p.get('slides', []):
            if x.get('layout') == 'poll': lo = [o['text'] for o in x.get('options', [])]
sh = os.path.join(S, 'shorts.json') if S else ''
if sh and os.path.exists(sh):
    for sc in json.load(open(sh)).get('scenes', []):
        for e in sc.get('els', []):
            if e.get('kind') == 'poll': so = list(e.get('opts', []))
for name, ops in (('롱폼', lo), ('쇼츠', so)):
    for i, o in enumerate(ops):
        n = len(o.encode())
        if n > 25: bad.append(f'{name} 보기 {i + 1} "{o}" {n}바이트 > 25(Threads 투표 한도, 한글 1자 3바이트)')
if lo and so and lo != so: bad.append(f'롱폼 보기 {lo} ≠ 쇼츠 보기 {so} (SNS 투표에 같은 문구로)')
if not lo: bad.append('롱폼 slides.json에 poll 보기가 없음')
print('\n'.join('POLL_SYNC_FAIL ' + b for b in bad) if bad else f'POLL_SYNC_OK {" / ".join(lo)}')
sys.exit(1 if bad else 0)
