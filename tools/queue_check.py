# SNS 대기열 파일을 올리기 전에 게시 단계에서 막힐 항목을 본다.
# 2026-10-26 OKLO 36회차: Threads 투표 보기 '남아 있는 10억 달러'가 26바이트(제한 25)라 04:20 ET 글이 7시간 동안 매 회 실패.
# 2026-10-29 SNS 스레드 지침 6장: 첫 문장 티커·불릿 3개 한 줄·제작 배경 위치·2/2 투표 연결·내부 용어 괄호
# 사용: python3 queue_check.py <queue json>...
import json, os, re, sys
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
        # 이야기형 리포트(11-15~)는 부 번호가 없다 → '리포트 끝 <부록 표 이름>'(예: '리포트 끝 급등 기록표')도 위치 안내로 인정(88회차 SERV)
        if 'drkimworld.com/r/' in r.get('text', '') and not re.search(r'[1-6]부|리포트 끝 \S+', r['text']):
            bad.append(f'{f}: 링크 답글에 리포트 N부 <표 이름> 위치 안내 없음(K8.0, 1/2이 질문으로 끝났을 때만 "답은")')
    for x in [t] + [r.get('text', '') for r in d.get('replies', [])] + list((d.get('channel_text') or {}).values()):
        if '빚' in x: bad.append(f"{f}: '빚' 금지(빛 오인) → 부채·차입금(v2.1 1.2)"); break
    # 인스타·페이스북 = 릴스 + 카드뉴스 둘 다(운영자 지시 2026-11-06 "둘다 해 페북도" — 10-29 '릴스 폐기'를 되돌림.
    # 근거: 30일 인스타 릴스 34개 조회 평균 17.8·최고 146 vs 카드 12개 평균 7.9·최고 약 10, 릴스는 비팔로워 도달, 카드는 중앙값 7로 꾸준)
    m = d.get('media') or {}
    if 'instagram' in d.get('channels', []):
        if m.get('type') == 'reels':
            cap = (d.get('channel_text') or {}).get('instagram') or t
            if 'http' in cap: bad.append(f'{f}: 인스타 릴스 캡션에 URL 금지(프로필 링크 → 사이트 검색)')
            if not re.search(r'검색|프로필', cap): bad.append(f'{f}: 인스타 릴스 캡션에 프로필 링크·사이트 검색 안내가 있어야 함')
            if not m.get('path', '').endswith('.mp4'): bad.append(f'{f}: 인스타 릴스 media.path는 쇼츠 mp4')
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
# S1 SNS 새 형식(2026-11-24 운영자 "다른 SNS 채널들도 비슷한 개선 적용", 미디어 review/sns_design_study.md) — publish_at 11-25~
#   Threads: 첫 줄은 혼자 서는 한 줄(45자 이하, 뒤에 빈 줄), 문단 100자 이하(휴대폰 5줄). 86글 첫 줄 중앙 60자·문단 최장 중앙 96자였다.
#   인스타 릴스: 첫 줄 45자 이하(더 보기 앞), 해시태그 5개 이하(인스타 상한), 표지는 격자(3:4)용 cover_ig.jpg(tools/shorts/reel_cover.py),
#   체험 릴스 금지(팔로워 피드·격자에 안 보임: 21일 릴스 32편 조회 중앙 0). 페이스북 릴스: 첫 줄 45자 이하, 캡션 속 리포트 링크 1개(관련 리포트는 첫 댓글로).
S1_FROM = '2026-11-25'
for f in sys.argv[1:]:
    try: d = json.load(open(f, encoding='utf-8'))
    except Exception: continue
    if str(d.get('publish_at', ''))[:10] < S1_FROM: continue
    ch, t, m = d.get('channels', []), d.get('text', ''), d.get('media') or {}
    # 11-24 운영자 "광고가 완전히 뜨잖아" + 철학 "수요와 공급을 연결": SNS의 💊·건강몰 줄은 링크 목록 사이에 툭 끼우지 않는다.
    #  ① 빈 줄로 떨어진 자기 문단 ② 누구(조건·상황 호명) ③ 앞 문단과 잇는 다리(그 회차 장면·시청자 처지) ④ 광고 표시
    _caps = [t] + [str((d.get('captions') or {}).get(c, '')) for c in ('instagram', 'facebook')]
    for _c in _caps:
        for _para in re.split(r'\n\s*\n', _c):
            if '💊' not in _para and 'health.drkimworld.com' not in _para: continue
            if 'drkimworld.com/r/' in _para or '텔레그램' in _para or '@drkimworld' in _para:
                bad.append(f'{f}: [S1·수요공급] 💊 광고 줄이 리포트 링크·텔레그램 목록과 같은 문단 — 빈 줄로 떼고 자기 문단으로')
            if not re.search(r'분이라면|분들은|하시는 분|드시는 분|보시는 분|이라면|이시라면|신 분|날이 많다면|많으시다면', _para):
                bad.append(f'{f}: [S1·수요공급] 💊 문단에 "누구"(조건·상황 호명) 없음 — 예: "차트를 오래 보는 날이 많다면" (health_midroll 0절)')
            if not re.search(r'광고|파트너스', _para):
                bad.append(f'{f}: [S1·수요공급] 💊 문단에 광고 표시 없음')
    if 'threads' in ch and t.strip():
        l1 = t.strip().split('\n')[0]
        if len(l1) > 45: bad.append(f'{f}: [S1] Threads 첫 줄 {len(l1)}자 > 45 — 첫 줄은 종목(티커)+모순 한 줄만, 숫자 설명은 빈 줄 뒤로: {l1[:30]}…')
        elif '\n\n' not in t.strip()[:len(l1) + 2]: bad.append(f'{f}: [S1] Threads 첫 줄 뒤에 빈 줄(첫 줄이 제목처럼 혼자 보이게)')
        for para in re.split(r'\n\s*\n', t.strip()):
            if len(para) > 100: bad.append(f'{f}: [S1] Threads 문단 {len(para)}자 > 100(휴대폰 5줄) — 문단을 나눈다: {para[:24]}…'); break
    for c in ('instagram', 'facebook'):
        if c in ch and m.get('type') == 'reels':
            cap = (d.get('channel_text') or {}).get(c) or t
            l1 = cap.strip().split('\n')[0]
            if len(l1) > 45: bad.append(f'{f}: [S1] {c} 릴스 캡션 첫 줄 {len(l1)}자 > 45(더 보기 앞에 잘림): {l1[:30]}…')
            if c == 'instagram':
                if len(re.findall(r'(?<![\w/&])#[^\s#]+', cap)) > 5: bad.append(f'{f}: [S1] 인스타 해시태그 5개 초과(인스타 상한 5개)')
                if not str(m.get('cover', '')).endswith('cover_ig.jpg'): bad.append(f'{f}: [S1] 인스타 릴스 표지는 격자용 cover_ig.jpg(python3 tools/shorts/reel_cover.py shorts.json static/social/<slug>/cover_ig.jpg)')
                if m.get('trial'): bad.append(f'{f}: [S1] 체험 릴스(trial) 금지 — 팔로워 피드·프로필 격자에 안 보인다')
            if c == 'facebook' and len(re.findall(r'drkimworld\.com/r/', cap)) > 1: bad.append(f'{f}: [S1] 페이스북 캡션 리포트 링크 {len(re.findall(r"drkimworld[.]com/r/", cap))}개 — 그 회차 리포트 1개만, 관련 리포트는 첫 댓글(replies)로')
# AD2(2026-11-26 운영자 "광고는 시각적으로나 호흡으로나 딱 구분되는게 더 이목을 끌거 같아. 링크는 이제 몰이 아니라 제품 링크를 바로 달기로 했어.") — publish_at 11-26~
#   💊 문단: ① 구분선 줄(─── 또는 '— 광고 —')로 시작하거나 바로 앞 문단이 구분선, 앞뒤 빈 줄 ② 그 회차 이야기 뒤(첫 문단 아님), 리포트·텔레그램 링크와 다른 문단
#   ③ 누구(조건·상황) ④ '광고' 표시 + 쿠팡 파트너스 문장("쿠팡 파트너스 활동의 일환으로") ⑤ 링크는 쿠팡 제품 직접(link.coupang.com) — 건강몰 가이드 링크 금지.
#   인스타 캡션은 URL 금지라 ⑤ 대신 링크 없음(프로필 링크 안내만). 답글(Threads 둘째 글)도 본다.
AD2_FROM = '2026-11-26'
DIV = re.compile(r'^\s*(?:[─━—–\-=·]{3,}|[─━—–\-]+\s*광고\s*[─━—–\-]+)\s*$')
WHO_S = r'분이라면|분들은|하시는 분|드시는 분|보시는 분|이라면|이시라면|신 분|날이 많다면|많으시다면'
def ad2_problems(name, txt, ig=False):
    out = []
    paras = [x for x in re.split(r'\n\s*\n', txt.strip())]
    for k, para in enumerate(paras):
        if '💊' not in para: continue
        lines = [l for l in para.split('\n') if l.strip()]
        body = [l for l in lines if not DIV.match(l)]
        has_div = (lines and DIV.match(lines[0])) or (k > 0 and all(DIV.match(l) for l in paras[k - 1].split('\n') if l.strip()))
        if not has_div: out.append(f'{name}: [AD2] 💊 문단 앞에 구분선 줄 없음 — 빈 줄 + "─────" 또는 "— 광고 —" 줄 + 빈 줄 없이 💊 문단')
        if k == 0 or (k == 1 and has_div and not (lines and DIV.match(lines[0]))): out.append(f'{name}: [AD2] 💊 문단이 맨 앞 — 그 회차 이야기 뒤에 둔다')
        if re.search(r'drkimworld\.com/r/|텔레그램|t\.me/|@drkimworld', '\n'.join(body)): out.append(f'{name}: [AD2] 💊 문단 안에 리포트·텔레그램 링크 — 링크 목록과 다른 문단으로')
        if not re.search(WHO_S, para): out.append(f'{name}: [AD2] 💊 문단에 "누구"(조건·상황) 없음')
        if '광고' not in para: out.append(f"{name}: [AD2] 💊 문단에 '광고' 표시 없음")
        if not re.search(r'쿠팡 ?파트너스 활동의 일환', txt): out.append(f'{name}: [AD2] 쿠팡 파트너스 문장("이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.") 없음')
        if 'health.drkimworld.com' in para: out.append(f'{name}: [AD2] 💊 문단에 건강몰 가이드 링크 — 11-26부터 쿠팡 제품 직접 링크(tools/product_link.py)')
        if ig:
            if 'http' in para: out.append(f'{name}: [AD2] 인스타 캡션 💊 문단에 URL(인스타는 프로필 링크 안내만)')
        elif not re.search(r'https://link\.coupang\.com/(a|re)/', para): out.append(f'{name}: [AD2] 💊 문단에 쿠팡 제품 직접 링크(link.coupang.com) 없음')
    return out
def ad2_date(d):
    # 회차 날짜 = 글이 가리키는 리포트 data_as_of(사이트 content/reports), 못 찾으면 publish_at — 옛 회차 글은 늦게 올라가도 옛 규칙
    allt = json.dumps(d, ensure_ascii=False)
    for slug in re.findall(r'drkimworld\.com/r/([a-z0-9\-]+)/', allt)[:1]:  # 첫 리포트 링크 = 그 회차(관련 리포트 링크는 뒤에)
        try:
            fm = open(os.path.join(os.environ.get('KW_SITE', '/home/user/kimworld-site'), 'content', 'reports', slug + '.md'), encoding='utf-8').read(3000)
            return re.search(r'^data_as_of:\s*["\']?(\d{4}-\d\d-\d\d)', fm, re.M).group(1)
        except Exception: pass
    return str(d.get('publish_at', ''))[:10]
for f in sys.argv[1:]:
    try: d = json.load(open(f, encoding='utf-8'))
    except Exception: continue
    if ad2_date(d) < AD2_FROM: continue
    ig_only = d.get('channels') == ['instagram']
    srcs = [('본문', d.get('text', ''), ig_only)] + [(f'답글{i + 1}', r.get('text', ''), False) for i, r in enumerate(d.get('replies', []))]
    srcs += [(f'channel_text.{c}', v, c == 'instagram') for c, v in (d.get('channel_text') or {}).items()]
    srcs += [(f'captions.{c}', v, c == 'instagram') for c, v in (d.get('captions') or {}).items()]
    for nm, txt, ig in srcs:
        bad += ad2_problems(f'{f} {nm}', str(txt or ''), ig)
# 쇼츠 표지(cover) 빈 화면 검사(SMR 60회차: ffmpeg -ss 1.5 프레임이 4KB 빈 화면) — 릴스 cover는 15KB 이상이고 밝기 변화가 있어야 한다
SITE = os.environ.get('KW_SITE', '/home/user/kimworld-site')
for f in sys.argv[1:]:
    try: d = json.load(open(f, encoding='utf-8'))
    except Exception: continue
    m = d.get('media') or {}
    cv = m.get('cover') if m.get('type') == 'reels' else None
    if not cv: continue
    pth = cv if os.path.isabs(cv) else os.path.join(SITE, cv)
    if not os.path.exists(pth): bad.append(f'{f}: 릴스 cover 파일 없음 {cv}'); continue
    if os.path.getsize(pth) < 15000: bad.append(f'{f}: 릴스 cover {os.path.getsize(pth)//1024}KB — 빈 화면 의심(ffmpeg -ss 4 이후 프레임으로 다시)')
    else:
        try:
            from PIL import Image, ImageStat
            st = ImageStat.Stat(Image.open(pth).convert('L').resize((64, 64)))
            if st.stddev[0] < 8: bad.append(f'{f}: 릴스 cover 밝기 변화 {st.stddev[0]:.1f} < 8 — 단색 화면 의심')
        except ImportError: pass
# 회차 묶음 검사(운영자 지시 2026-11-06): 카드뉴스가 있으면 인스타 릴스·페이스북 릴스·페이스북 카드뉴스도 같은 폴더에 있어야 한다
import os
for f in sys.argv[1:]:
    b = os.path.basename(f)
    if b.endswith('-cards.json'):
        base = f[:-len('-cards.json')]
        for suf, what in (('-igreels.json', '인스타 릴스'), ('-reels.json', '페이스북 릴스'), ('-fbcards.json', '페이스북 카드뉴스')):
            if not any(os.path.exists(base.replace(x, y) + suf) for x, y in (('/queue/', '/queue/'), ('/queue/', '/posted/'), ('/posted/', '/queue/'))):
                bad.append(f'{f}: {what} 파일 {os.path.basename(base + suf)} 없음 — 인스타·페이스북은 릴스와 카드뉴스 둘 다')

# 가독성(운영자 지시 2026-11-11 "모든 컨텐츠에 가독성 개선 지침"): SNS 글도 화살표·가운뎃점 나열·기호 계산·긴 문장 검사(tools/plain_check.py)
import subprocess
pc = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plain_check.py')] + [f for f in sys.argv[1:] if f.endswith('.json')], capture_output=True, text=True).stdout
if 'PLAIN_FAIL' in pc: bad += ['가독성(plain_check): ' + l.strip() for l in pc.splitlines() if l.startswith(('FAIL', '   '))]
# 시장·거시 한 줄(운영자 11-22, SKILL K8): publish_at 11-23~ Threads 첫 글·둘째 글 중 하나에 — tools/macro_check.py queue
mq = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'macro_check.py'), 'queue'] + [f for f in sys.argv[1:] if f.endswith('.json')], capture_output=True, text=True).stdout
bad += [l.strip() for l in mq.splitlines() if l.startswith('MACRO_THREADS')]
for b in bad: print('BAD', b)
print('QUEUE_OK' if not bad else f'QUEUE_FAIL {len(bad)}'); sys.exit(1 if bad else 0)
