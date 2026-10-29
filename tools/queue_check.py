# SNS 대기열 파일을 올리기 전에 게시 단계에서 막힐 항목을 본다.
# 2026-10-26 OKLO 36회차: Threads 투표 보기 '남아 있는 10억 달러'가 26바이트(제한 25)라 04:20 ET 글이 7시간 동안 매 회 실패.
# 사용: python3 queue_check.py <queue json>...
import json, re, sys
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
    # K8.0 (2026-10-29 스레드 작성 표준): 43회차 CBRS 질문 '몇 번이었을까?' + 시나리오 보기 불일치
    t = d.get('text', '')
    q = [l for l in t.strip().split('\n') if l.strip()][-1:] or ['']
    if o and not any(re.search(r'\d', x) for x in o) and re.search(r'몇 ?(번|개|일|%)|얼마|며칠', q[0]):
        bad.append(f'{f}: 마지막 질문이 숫자를 묻는데 투표 보기는 시나리오(질문과 보기를 같은 질문으로): {q[0][:40]}')
    for x in re.findall(r'[^.\n]*(?:때문에|탓에|여파로|영향으로)[^.\n]*', t):
        if not re.search(r'수 있|보인|추정|가능성|일까|\?|라면', x):
            bad.append(f'{f}: 인과 단정(사실·가설 구분, K8.0): {x.strip()[:40]}')
    for x in [t] + [r.get('text', '') for r in d.get('replies', [])]:
        m = re.search(r'국면 ?[A-DＡ-Ｄ]\b|P[1-9]\b', x)
        if m: bad.append(f'{f}: 내부 약어 \'{m.group()}\'는 풀어 쓴다(K8.0)')
    for r in d.get('replies', []):
        if 'drkimworld.com/r/' in r.get('text', '') and not re.search(r'[1-6]부', r['text']):
            bad.append(f'{f}: 링크 답글에 \'답은 리포트 N부 <표 이름>\' 위치 안내 없음(K8.0)')
for b in bad: print('BAD', b)
print('QUEUE_OK' if not bad else f'QUEUE_FAIL {len(bad)}'); sys.exit(1 if bad else 0)
