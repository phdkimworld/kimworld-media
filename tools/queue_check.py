# SNS 대기열 파일을 올리기 전에 게시 단계에서 막힐 항목을 본다.
# 2026-10-26 OKLO 36회차: Threads 투표 보기 '남아 있는 10억 달러'가 26바이트(제한 25)라 04:20 ET 글이 7시간 동안 매 회 실패.
# 사용: python3 queue_check.py <queue json>...
import json, sys
bad = []
for f in sys.argv[1:]:
    d = json.load(open(f, encoding='utf-8'))
    o = d.get('poll') or []
    if o and not 2 <= len(o) <= 4: bad.append(f'{f}: 투표 보기 2~4개: {len(o)}')
    for i, x in enumerate(o, 1):
        if len(x.encode()) > 25: bad.append(f'{f}: poll[{i}] {len(x.encode())}바이트 > 25 (한글 1자 = 3바이트): {x}')
    if 'threads' in d.get('channels', []) and len(d.get('text', '')) > 500: bad.append(f'{f}: Threads 본문 {len(d["text"])}자 > 500')
    for r in d.get('replies', []):
        if len(r.get('text', '')) > 500: bad.append(f'{f}: 답글 {len(r["text"])}자 > 500')
    if not d.get('publish_at'): bad.append(f'{f}: publish_at 없음')
for b in bad: print('BAD', b)
print('QUEUE_OK' if not bad else f'QUEUE_FAIL {len(bad)}'); sys.exit(1 if bad else 0)
