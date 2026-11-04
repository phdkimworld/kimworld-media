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
            bad.append(f'{f}: 링크 답글에 리포트 N부 <표 이름> 위치 안내 없음(K8.0, 1/2이 질문으로 끝났을 때만 '답은')')
    for x in [t] + [r.get('text', '') for r in d.get('replies', [])] + list((d.get('channel_text') or {}).values()):
        if '빚' in x: bad.append(f"{f}: '빚' 금지(빛 오인) → 부채·차입금(v2.1 1.2)"); break
    # 인스타 카드뉴스 전환(운영자 지시 2026-10-29 "인스타는 릴스 폐기하고 카드뉴스로 완전히 전환")
    m = d.get('media') or {}
    if 'instagram' in d.get('channels', []):
        if m.get('type') == 'reels': bad.append(f'{f}: 인스타 릴스는 폐기 — 인스타는 카드뉴스(carousel, tools/cardnews/make_cards.py), 릴스는 facebook 채널만')
        if m.get('type') == 'carousel':
            ps = m.get('paths') or []
            if not 7 <= len(ps) <= 10: bad.append(f'{f}: 카드뉴스 {len(ps)}장 — 7~10장')
            if any(not str(x).lower().endswith(('.jpg', '.jpeg')) for x in ps): bad.append(f'{f}: 인스타 캐러셀은 JPEG만')
            cap = (d.get('channel_text') or {}).get('instagram') or t
            if 'http' in cap: bad.append(f'{f}: 인스타 캡션에 URL 금지(프로필 링크 → 사이트 검색)')
            if not re.search(r'검색|바로 보기', cap) or '저장' not in cap: bad.append(f'{f}: 인스타 캡션에 사이트 첫 화면·검색 안내와 저장 유도가 있어야 함')
            # 캡션 첫 줄(...더 보기 앞)이 표지 제목을 되풀이하면 피드에서 같은 말을 두 번 본다(운영자 TNXP 카드 검토 11-02) → 넘기기·투표 유도로 시작
            l1 = cap.strip().split('\n')[0]
            if len(l1) > 45: bad.append(f'{f}: 인스타 캡션 첫 줄 {len(l1)}자 > 45(더 보기 앞에 잘림)')
            if not re.search(r'넘겨|장[)\]]|\d장|스와이프|투표', l1): bad.append(f'{f}: 인스타 캡션 첫 줄은 표지 반복 대신 넘기기·투표 유도(예: \'7장 기록과 8장 투표까지 넘겨 보세요 👉\'): {l1[:40]}')
    # SNS v3.2 (2026-11-04 MRVL 스레드 검수): 투표 축 주어, 1/2 문장 형태별 2/2 안내, 쌍방 티커, M&A 낱말
    allx = [t] + [r.get('text', '') for r in d.get('replies', [])] + list((d.get('channel_text') or {}).values())
    for x in allx:
        m = re.search(r'사들였|사들인다|사들이는|사들인 ', x)
        if m: bad.append(f"{f}: '{m.group().strip()}' → '인수했' (K9.0 M&A 낱말)"); break
    combo = [x for x in o if re.search(r'[+·]', x)]
    sp = [re.split(r'\s*[+·]\s*', x, maxsplit=1) for x in combo]
    # 2×2 매트릭스(왼쪽 축·오른쪽 축이 각각 두 값으로 되풀이)일 때만 축 주어를 본다
    if len(combo) >= 3 and all(len(a) == 2 for a in sp) and len({a[0] for a in sp}) <= 2 and len({a[1] for a in sp}) <= 2:
        for x in combo:
            for seg in re.split(r'\s*[+·]\s*', x):
                w = re.sub(r'[↑↓]', '', seg.split()[0]) if seg.split() else ''
                if not w or w not in t:
                    bad.append(f'{f}: 투표 보기 \'{x}\'의 축 \'{seg}\'에 주어가 없거나 본문에 없는 주어(v3.2 1: \'실적↑·합병 신뢰\'처럼 주어+상태, 주어는 본문에도)'); break
    qn = len(re.findall(r'\?', t))
    for x in [r.get('text', '') for r in d.get('replies', [])]:
        if re.search(r'(은|는) 답은', x): bad.append(f"{f}: 답글 'X는 답은 …' 비문 → 'X는 리포트 N부 …에 있다'"); 
        if '답은' in x and qn <= 1 and o: bad.append(f"{f}: 1/2이 투표 질문 하나뿐인데 2/2에 '답은' — 묻지 않은 질문에 답하는 꼴(v3.2 2 Case B: '상세 비교는 3부 기록표, … 계산은 4부에 정리했다')")
    if re.search(r'합병|합작 ?투자|맞대결', t):
        tk = set(re.findall(r'\(([A-Z]{1,5}(?:\.[A-Z]{1,2})?)\)', t))
        if len(tk) < 2 and not d.get('single_ticker_ok'): bad.append(f'{f}: 합병·합작·비교 글인데 티커 {len(tk)}개 — 상대 기업 티커도 첫 문단에(v3.2 3, 예: 루멘텀(LITE)). 상대가 비상장이면 "single_ticker_ok": true')
    # SNS 스레드 지침 6장(2026-10-29, SLNH 스레드 조회 11회 진단)
    if 'threads' in d.get('channels', []):
        first = re.split(r'(?<=[.?!다])\s', t.strip(), maxsplit=1)[0]
        if not re.search(r'\([A-Z]{1,5}(?:\.[A-Z]{1,2})?\)', first): bad.append(f'{f}: 첫 문장에 종목명(티커) 병기 없음(6.2①): {first[:40]}')
        bl = [l.strip() for l in t.split('\n') if re.match(r'\s*[·•\-]\s', l)]
        if len(bl) > 3: bad.append(f'{f}: 숫자 불릿 {len(bl)}개 > 3(6.2② 모바일 첫 화면에 투표가 잘림)')
        for l in bl:
            if len(l.lstrip('·- ')) > 35: bad.append(f'{f}: 불릿 {len(l.lstrip("·- "))}자 > 35(v2.8 5.1 한 줄 35자, 투표 보기 4개가 첫 화면에): {l[:30]}…')
        if re.search(r'시청자 (질문|요청)|\d{4}년 \d{1,2}월 접수|접수\)', t): bad.append(f'{f}: 제작 배경(시청자 요청·접수 시점)은 본문 말고 2/2 답글 끝으로(6.2③)')
        reps = [r.get('text', '') for r in d.get('replies', [])]
        if o and reps and not re.search(r'투표', re.split(r'(?<=[.?!다])\s', reps[0].strip(), maxsplit=1)[0]): bad.append(f'{f}: 2/2 첫 문장이 1/2 투표 질문과 이어지지 않음(6.2④ "투표하신 시나리오의 …")')
        for x in reps:
            if re.search(r'\d{4}년 \d{1,2}월 접수', x): bad.append(f'{f}: 답글에 과거 접수 시점(6.2③ "다음 분석 원하는 종목은 댓글로"로)')
            m = re.search(r'\([^)\n]*(×|가능성 구간|평소 거래량 대비|분모)[^)\n]*\)', x)
            if m: bad.append(f'{f}: 답글에 내부 기획 용어 괄호 노출(6.2④ 문장으로 풀기): {m.group(0)[:40]}')
for b in bad: print('BAD', b)
print('QUEUE_OK' if not bad else f'QUEUE_FAIL {len(bad)}'); sys.exit(1 if bad else 0)
