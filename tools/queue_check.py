# SNS 대기열 파일을 올리기 전에 게시 단계에서 막힐 항목을 본다.
# 2026-10-26 OKLO 36회차: Threads 투표 보기 '남아 있는 10억 달러'가 26바이트(제한 25)라 04:20 ET 글이 7시간 동안 매 회 실패.
# 2026-10-29 SNS 스레드 지침 6장: 첫 문장 티커·불릿 3개 한 줄·제작 배경 위치·2/2 투표 연결·내부 용어 괄호
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
    # SNS 스레드 지침 6장(2026-10-29, SLNH 스레드 조회 11회 진단)
    if 'threads' in d.get('channels', []):
        first = re.split(r'(?<=[.?!다])\s', t.strip(), maxsplit=1)[0]
        if not re.search(r'\([A-Z]{1,5}(?:\.[A-Z]{1,2})?\)', first): bad.append(f'{f}: 첫 문장에 종목명(티커) 병기 없음(6.2①): {first[:40]}')
        bl = [l.strip() for l in t.split('\n') if re.match(r'\s*[·•\-]\s', l)]
        if len(bl) > 3: bad.append(f'{f}: 숫자 불릿 {len(bl)}개 > 3(6.2② 모바일 첫 화면에 투표가 잘림)')
        for l in bl:
            if len(l) > 40: bad.append(f'{f}: 불릿 {len(l)}자 > 35~40(6.2② 한 줄): {l[:30]}…')
        if re.search(r'시청자 (질문|요청)|\d{4}년 \d{1,2}월 접수|접수\)', t): bad.append(f'{f}: 제작 배경(시청자 요청·접수 시점)은 본문 말고 2/2 답글 끝으로(6.2③)')
        reps = [r.get('text', '') for r in d.get('replies', [])]
        if o and reps and not re.search(r'투표', re.split(r'(?<=[.?!다])\s', reps[0].strip(), maxsplit=1)[0]): bad.append(f'{f}: 2/2 첫 문장이 1/2 투표 질문과 이어지지 않음(6.2④ "투표하신 시나리오의 …")')
        for x in reps:
            if re.search(r'\d{4}년 \d{1,2}월 접수', x): bad.append(f'{f}: 답글에 과거 접수 시점(6.2③ "다음 분석 원하는 종목은 댓글로"로)')
            m = re.search(r'\([^)\n]*(×|가능성 구간|평소 거래량 대비|분모)[^)\n]*\)', x)
            if m: bad.append(f'{f}: 답글에 내부 기획 용어 괄호 노출(6.2④ 문장으로 풀기): {m.group(0)[:40]}')
for b in bad: print('BAD', b)
print('QUEUE_OK' if not bad else f'QUEUE_FAIL {len(bad)}'); sys.exit(1 if bad else 0)
