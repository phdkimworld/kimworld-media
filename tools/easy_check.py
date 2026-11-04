# 리포트가 비전문가도 읽히는지 발행 전에 본다(운영자 지시 2026-10-26: "리포트가 좀 어려운거 같아. 딥다이브는 좋은데. 설명을 앞으로는 비전문가도 알아먹게 좀 해줘").
# 사용: python3 easy_check.py <리포트.md> [--glossary <사이트 data/glossary.yaml>]
#  - v3.3(2026-11-04 운영자 MRVL 분석, 공개일 11-05~·--v33): 시나리오 대표값 '약 N%' 합 100, 'N거래일 동안 X%'에 기준 종가, 6부 끝 판단 기준 세 가지
#  - v3.2(2026-11-04 운영자 SLDP 가독성 분석, 공개일 11-05~·--v32): 짧은 답 문제 제기형 첫 문단, 국면 정의는 5부, 3부 기준의 이유, 4부 끝 확인 조건 두 가지, 시나리오 조건은 말로
#  - v3.1(2026-11-03 운영자 PLUG 가독성 분석, 공개일 11-04~·--v31): 국면 쉬운 말 병기, 5부 가능성 뜻·사실/과거/추정 구분, 같은 소수% 4번↑ 반복, 숫자 10개↑ 문단
#  - v3.0 Patch(2026-11-03 운영자 PLUG 검수, 공개일 11-03~·--v30): 숫자 3열 표 1열 줄당 18자, 판정표 2열+배지, 음수 범위 '~-' 붙여 쓰기·단독 '~숫자%' 금지
#  - v2.1 Master(2026-10-29, data_as_of 10-30~): 표 3열 이하·기록표 '이벤트일 · 공시 내용 | 당일 | N거래일 뒤'·판정표 3열·한 칸 수치 둘·'빚' 금지
#  - 통합 제작·검수 지침(2026-10-29): 억$ 혼합 표기·본문 $ 금지, (10-30~) 기록표 열 스키마, 체크리스트 [시점][수치]
#  - R1.8(2026-10-29): key_points 개조식, 짧은 답 숫자 반복, 용어 병기(EV·RPO·중앙값), 수급 분모 셋, 국면 정의, 표 칸 수·열 자료형, 판정표 머리, 체크리스트, 2×2 시나리오·구간 가능성
#  - 1~6부 제목 아래 '> **핵심:**' 콜아웃, 끝에 다음 부 예고 문장 없음, ## 위계, ① 나열 없음, 시나리오 표, 표·### 5개 이하(SKILL R1.7, 2026-10-28). --legacy면 옛 '쉽게 말하면' 검사
#  - 본문 문장(표·제목·인용·출처 제외) 가운데 90자 넘는 문장 비율 10% 이하, 날짜를 뺀 숫자 4개 이상 든 문장 5% 이하
#  - 영어 약어(대문자 2자 이상)는 처음 나올 때 괄호 풀이나 용어 사전 항목이 있어야 한다(티커·단위 제외)
#  - 말로 쭉 이어 쓰기(운영자 지시 2026-10-26 "리포트가 너무 읽기 어려워 섹션이나 카드를 너무 쪼개지 말고 그냥 차라리 말로 쭉 친절하게 설명해", SKILL R1.6):
#    `###` 소제목 4개 이하, 사건 카드 머리(**YYYY.MM.DD · …**) 0개, 글머리 목록 줄 8개 이하, 표 3개 이하,
#    '이 리포트에서 확인할 수 있는 것'·'먼저 알아둘 용어' 절 없음, 한 문장짜리 문단 25% 이하. --legacy를 주면 이 검사를 건너뛴다(옛 리포트 고칠 때)
import sys, re, os
p = sys.argv[1]
gl = sys.argv[sys.argv.index('--glossary') + 1] if '--glossary' in sys.argv else '/home/user/kimworld-site/data/glossary.yaml'
txt = open(p, encoding='utf-8').read()
body = txt.split('\n---', 2)[-1] if txt.startswith('---') else txt
fm = txt[:len(txt) - len(body)]
ticker = (re.search(r'^ticker:\s*"?([A-Z0-9.]+)', fm, re.M) or [None, ''])[1]
terms = set(re.findall(r'term:\s*"([^"]+)"', open(gl, encoding='utf-8').read())) if os.path.exists(gl) else set()
bad = []
parts = re.split(r'^## (\d)부', body, flags=re.M)
R17 = '--legacy' not in sys.argv
_dt = max((re.search(r'^data_as_of:\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M) or [None, '0'])[1], (re.search(r'^date:\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M) or [None, '0'])[1])
_v32 = _dt >= '2026-11-05' or '--v32' in sys.argv
_v33 = _dt >= '2026-11-05' or '--v33' in sys.argv  # v3.3(운영자 11-04 MRVL 블로그·리포트 분석)  # v3.2(운영자 11-04 SLDP 가독성 분석)
for i in range(1, len(parts), 2):
    sec = parts[i + 1]
    if R17:
        # R1.7(2026-10-28 운영자 "작성 지침에도 반영"): 부 제목 아래 첫 줄은 '> **핵심:** …', 끝은 다음 부 예고 문장 없이
        first = next((l for l in sec.split('\n')[1:] if l.strip()), '')
        if not first.startswith('> **핵심:**'): bad.append(f'R1.7 {parts[i]}부 제목 바로 아래 > **핵심:** 콜아웃이 없음')
        if re.match(r'\s*쉽게 말하면', '\n'.join(sec.split('\n')[1:]).replace(first, '', 1).lstrip()): bad.append(f"R1.7 {parts[i]}부 본문이 '쉽게 말하면'으로 시작(콜아웃으로 대신)")
        tail = [l for l in sec.split('\n') if l.strip() and not l.lstrip().startswith(('|', '#', '>', '!', '-'))][-1:] or ['']
        if re.search(r'[1-6]부(에서|가|의)[^.]{0,30}(보겠|모아|정리합|답합|이어|살펴)', tail[0]): bad.append(f'R1.7 {parts[i]}부 끝이 다음 부 예고 문장: {tail[0][:50]}…')
    elif '쉽게 말하면' not in sec[:1500]:
        bad.append(f'{parts[i]}부 첫머리(1500자 안)에 쉽게 말하면 문장이 없음')
if R17 and (re.search(r'^data_as_of:\s*"?(\d{4}-\d{2}-\d{2})', txt, re.M) or [0, '0'])[1] >= '2026-10-27':
    # 운영자 형식 검토 재확인(2026-10-29, INOD): 부 첫머리만이 아니라 짧은 답·본문 어디서든 대본체 '쉽게 말하면', 짧은 답의 '그렇다면 ~일까요' 다리 문단을 막는다
    for m in re.finditer(r'(?m)^(?![>|#]).*쉽게 말하면.*$', body): bad.append(f"R1.7 대본체 '쉽게 말하면'(핵심 콜아웃·평서문으로): {m.group(0).strip()[:40]}")
    sa = re.search(r'^## 짧은 답\n(.*?)(?=^## )', body, re.M | re.S)
    if sa:
        for para in [x.strip() for x in sa.group(1).split('\n\n') if x.strip()]:
            if re.match(r'그렇다면', para) and re.search(r'까요[.?]', para): bad.append(f'R1.7 짧은 답에 예고 다리 문단(질문 대신 표 위치 한 줄): {para[:40]}…')
lines = [re.sub(r'\]\([^)]*\)|https?://\S+', ']', l) for l in body.split('\n') if l.strip() and not l.lstrip().startswith(('|', '#', '>', '!', '<'))]
sents = [s.strip() for l in lines for s in re.split(r'(?<=[.?!다])\s+(?=\S)', re.sub(r'^\s*[-*\d.□]+\s*', '', l)) if len(s.strip()) > 5]
longs = [s for s in sents if len(s) > 90]
DATE = r'\d{4}년|\d{1,2}월|\d{1,2}일|\d{4}\.\d{1,2}\.\d{1,2}|\d{1,2}\.\d{1,2}(?=[ ·~)])|[1-6]부|\d\.\d(?=\s)|P\d+'
dense = [s for s in sents if len(re.findall(r'\d[\d,.]*', re.sub(DATE, '', s))) >= 4]
if sents and len(longs) / len(sents) > 0.10: bad.append(f'90자 넘는 문장 {len(longs)}/{len(sents)}({len(longs)/len(sents):.0%}) > 10% · 예: {longs[0][:60]}…')
if sents and len(dense) / len(sents) > 0.05: bad.append(f'숫자 4개 이상 문장 {len(dense)}/{len(sents)}({len(dense)/len(sents):.0%}) > 5% · 예: {dense[0][:60]}…')
skip = {ticker, 'ET', 'USD', 'ETF', 'AI', 'SEC', 'IR', 'CEO', 'CFO', 'PNG', 'URL', 'UTC', 'KST', 'TVA'}
seen = set()
for m in re.finditer(r'(?<![A-Za-z])([A-Z][A-Z0-9]{1,6})(?![A-Za-z])', '\n'.join(lines)):
    a = m.group(1)
    if a in seen or a in skip or a.isdigit(): continue
    seen.add(a)
    after = '\n'.join(lines)[m.end():m.end() + 3]
    before = '\n'.join(lines)[max(0, m.start() - 2):m.start()]
    if re.fullmatch(r'P\d+', a) or any(x.startswith(a) for x in terms) or after.startswith('(') or before.endswith('('): continue
    bad.append(f"약어 '{a}' 첫 등장에 풀이 없음(괄호 풀이 또는 용어 사전)")
if '--legacy' not in sys.argv:
    h3 = re.findall(r'^### ', body, re.M); cards = re.findall(r'^\*\*\d{4}\.\d{2}\.\d{2}[^*\n]*·', body, re.M)
    bullets = [l for l in body.split('\n') if re.match(r'\s*([-*]|\d+\.)\s', l)]
    tables = re.findall(r'(?:^\|.*\n)+', body, re.M)
    paras = [x.strip() for x in body.split('\n\n') if x.strip() and not x.lstrip().startswith(('|', '#', '>', '!', '-', '*', '<')) and not re.match(r'\d+\.\s', x.strip())]
    one = [x for x in paras if len(re.findall(r'[.?!다요]\s', x + ' ')) <= 1]
    if len(h3) > 5: bad.append(f'R1.6·R1.7 ### 소제목 {len(h3)}개 > 5(쪼개지 말고 문단으로 이어 쓰기)')
    for h in re.findall(r'^## (.+)$', body, re.M):
        if not re.match(r'(짧은 답|지난 리포트 이후|[1-6]부)', h): bad.append(f"R1.7 '## {h[:20]}'는 ###로(## 는 짧은 답·지난 리포트 이후·1~6부만)")
    if '①' in body: bad.append('R1.7 ① 나열 대신 6부 체크리스트로 일원화')
    if '가능성(추정)' in body and not re.search(r'^\|[^\n]*가능성[^\n]*\|', body, re.M): bad.append('R1.7 시나리오 표(가능성·계기·예상 반응·판정 날짜 열)가 없음')
    if cards: bad.append(f'R1.6 사건 카드 머리 {len(cards)}개(카드 대신 시간순 문단)')
    if len(bullets) > 8: bad.append(f'R1.6 글머리 목록 {len(bullets)}줄 > 8(체크리스트 외에는 문장으로)')
    if len(tables) > 5: bad.append(f'R1.7 표 {len(tables)}개 > 5')
    for sec in ('## 이 리포트에서 확인할 수 있는 것', '## 먼저 알아둘 용어'):
        if sec in body: bad.append(f"R1.6 '{sec[3:]}' 절은 빼기(용어는 처음 쓰는 문장 안에서 풀기)")
    if paras and len(one) / len(paras) > 0.25: bad.append(f'R1.6 한 문장짜리 문단 {len(one)}/{len(paras)} > 25%(2~4문장으로 이어 쓰기)')
if '--legacy' not in sys.argv:
    # R1.8(2026-10-29 운영자 검토 「세레브라스 리포트 기반 SOP 개선안」): 도입부 압축·용어 병기·수급 분모·국면 정의·표 검수·시나리오
    kps = re.findall(r'^\s+-\s+"(.*)"\s*$', fm.split('key_points:')[1].split('\n', 4)[-1] if False else '\n'.join(fm.split('key_points:')[1].split('\n')[1:4]), re.M) if 'key_points:' in fm else []
    for k in kps:
        if re.search(r'(습니다|입니다|였다|했다)\.?$', k): bad.append(f'R1.8 key_points는 개조식 단문(주가:/재료:/일정:): {k[:30]}…')
    sa = (re.search(r'^## 짧은 답\n(.*?)(?=^## )', body, re.S | re.M) or [None, ''])[1]
    num = lambda x: set(re.findall(r'[+-]?\d[\d,.]*(?:%|달러|만 주)', x))
    rep = num(sa) & num(' '.join(kps))
    if len(rep) > 1: bad.append(f'R1.8 짧은 답이 key_points 숫자 {len(rep)}개를 되풀이: {", ".join(sorted(rep))[:60]}')
    for easy, std in (('현금을 뺀 회사 가치', r'EV|기업가치'), ('쌓인 일감', r'RPO|수주잔고|잔여수행의무'), ('가운데 값', r'중앙값')):
        i = body.find(easy)
        if i >= 0 and not re.search(std, body[i:i + len(easy) + 20]): bad.append(f"R1.8 '{easy}' 처음 나올 때 표준 용어 병기({std.split('|')[0]})")
    if re.search(r'(풀린|풀리는|해제)[^\n]{0,40}전체 주식의 약', body) or re.search(r'전체 주식의 약[^\n]{0,20}\|', body):
        if not re.search(r'(유통|거래되는)[^\n]{0,30}약 \d', body): bad.append('R1.8 수급 물량에 유통주식 대비 비율이 없음(분모 셋: 전체·유통·평균 거래량)')
        if not re.search(r'평균[^\n]{0,20}(거래량)?[^\n]{0,30}(\d[\d.]*\s*(배|일치))|일치', body): bad.append('R1.8 수급 물량에 평균 거래량 대비 배수(며칠치)가 없음')
    if re.search(r'국면 [A-D]', body) and '국면 정의' not in body: bad.append("R1.8 '국면 A·B·C'를 쓰면 처음 나오는 자리에 > **국면 정의(…):** 상자")
    T = {'date': r'\**\d{4}\.\d{2}\.\d{2}\**', 'pct': r'\**[+-−]?\d[\d.]*%\**', 'shares': r'\**(약 )?[\d,.]+(억 )?[\d,]*만 주\**', 'usd': r'\**(약 )?[\d,.]+(억 )?[\d,]*달러\**'}
    for t in re.findall(r'(?:^\|.*\n)+', body + '\n', re.M):
        rows = [[c.strip() for c in r.strip().strip('|').split('|')] for r in t.strip().split('\n')]
        head, data = rows[0], [r for r in rows[2:]]
        for r in data:
            if len(r) != len(head): bad.append(f'R1.8 표 칸 수 {len(r)} ≠ 머리 {len(head)}(| 누락?): {"|".join(r)[:50]}')
        for c in range(len(head)):
            col = [r[c] for r in data if c < len(r) and r[c] not in ('—', '-', '')]
            kinds = [next((k for k, rx in T.items() if re.fullmatch(rx, x)), None) for x in col]
            typed = [k for k in kinds if k]
            if len(typed) >= 3:
                main = max(set(typed), key=typed.count)
                if typed.count(main) / len(col) >= 0.6:
                    for x, k in zip(col, kinds):
                        if k and k != main: bad.append(f"R1.8 표 '{head[c]}' 열은 {main}인데 {k} 값: {x}")
    pt = re.search(r'^## 지난 리포트 이후\n(.*?)(?=^## )', body, re.S | re.M)
    if pt and '|' in pt.group(1):
        h = [c.strip() for c in re.search(r'^\|(.*)\|\s*$', pt.group(1), re.M).group(1).split('|')]
        _asof = (re.search(r'^data_as_of:\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M) or [None, '0'])[1]
        # v2.1은 공개일(date) 10-30 이후 리포트에도 적용(47회차 LEU: 기준일 10-29라 옛 4열 판정표를 요구받음)
        _pub = (re.search(r'^date:\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M) or [None, '0'])[1]
        _v30 = True  # v3.0은 공개일과 무관하게 모든 리포트(11-04 운영자 v3.0 재검수: 옛 리포트 19편 일괄 교정)
        if _v30:
            # v3.0 Patch 1.2(운영자 11-03 PLUG 검수): 3열 판정표는 오른쪽 '진행 중'이 '진'으로 잘림 → 2열 + 배지
            if len(h) != 2 or not h[0].startswith('지난 점검 항목 · 당시 기준') or not h[1].startswith('판정 및 실제 결과'):
                bad.append('v3.0 지난 리포트 판정표는 2열 | 지난 점검 항목 · 당시 기준 | 판정 및 실제 결과(<날짜>) |, 판정은 2열 첫 줄 배지 **[적중]**')
        elif max(_asof, _pub) >= '2026-10-30':
            if len(h) != 3 or not h[0].startswith('지난 점검 항목 · 당시 기준') or not h[1].startswith('실제 결과') or h[2] != '판정':
                bad.append('v2.1 지난 리포트 판정표 머리는 3열 | 지난 점검 항목 · 당시 기준 | 실제 결과(<날짜>) | 판정 |')
        elif h[:2] != ['지난 점검 항목', '당시 판단 기준'] or not h[2].startswith('실제 결과') or h[-1] != '판정':
            bad.append('R1.8 지난 리포트 판정표 머리는 | 지난 점검 항목 | 당시 판단 기준 | 실제 결과(<날짜>) | 판정 |')
        for r in re.findall(r'^\|(?!\s*-)(.*)\|\s*$', pt.group(1), re.M)[1:]:
            j = r.split('|')[-1].strip()
            if _v30: j = (re.match(r'\*\*\[([^\]]+)\]\*\*<br>', j) or [None, '배지 없음'])[1]
            if not re.match(r'(적중|빗나감|부분 적중|진행 중)', j): bad.append(f'R1.8 판정은 적중/빗나감/부분 적중/진행 중: {j[:20]}')
    for l in body.split('\n'):
        if re.search(r'[□☐]', l) and not re.match(r'- [□☐] \S', l): bad.append(f'R1.8 체크리스트는 한 단계 "- □ 항목": {l.strip()[:40]}')
    asof = (re.search(r'^data_as_of:\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M) or [None, '0'])[1]
    if asof >= '2026-10-29' and '가능성(추정)' in body:
        st = re.search(r'^\|[^\n]*가능성\(추정\)[^\n]*\|\n(?:^\|.*\n)+', body + '\n', re.M)
        if st:
            rows = [[c.strip() for c in r.strip().strip('|').split('|')] for r in st.group(0).strip().split('\n')[2:]]
            ax = [i for i in range(len(rows[0])) if all(r[i] in ('○', '×') for r in rows if i < len(r))]
            cx = [i for i in range(len(rows[0])) if all(re.fullmatch(r'[○×]\s*/\s*[○×]', r[i]) for r in rows if i < len(r))]
            # v3.2(2026-11-04 SLDP 가독성 검토): 조건은 기호 대신 말로 '발행 없음 · 합작 발표'(가운뎃점 둘로 나뉜 한 칸)
            wx = [i for i in range(len(rows[0])) if all(len(re.split(r'\s+·\s+', r[i])) == 2 and not re.search(r'[○×]', r[i]) for r in rows if i < len(r))]
            pairs = {tuple(r[i] for i in ax[:2]) for r in rows} if len(ax) >= 2 else {tuple(re.split(r'\s*/\s*', r[cx[0]])) for r in rows} if cx else {tuple(re.split(r'\s+·\s+', r[wx[0]])) for r in rows} if wx else set()
            if len(pairs) != 4 or len(rows) != 4: bad.append('R1.8 시나리오는 두 조건 2×2 네 칸(조건 칸은 말로 "발행 없음 · 합작 발표")')
            if _v32 and (ax or cx): bad.append('v3.2 시나리오 조건은 ○/× 기호 대신 말로("발행 없음 · 합작 발표")')
            lo = hi = 0; mids = []
            for r in rows:
                m = re.search(r'(높음|중간|낮음)(?:\s*약\s*(\d+)%)?\s*(?:<br>)?\s*\((\d+)~(\d+)%\)', ' '.join(r))
                if not m: bad.append(f'R1.8 가능성은 높음(35~45%)·중간(20~30%)·낮음(10~20%) 구간: {r[0][:20]}'); continue
                lo += int(m.group(3)); hi += int(m.group(4))
                if m.group(2):
                    mids.append(int(m.group(2)))
                    if not int(m.group(3)) <= int(m.group(2)) <= int(m.group(4)): bad.append(f'v3.3 대표값 약 {m.group(2)}%가 구간 밖: {r[0][:20]}')
            if rows and not lo <= 100 <= hi: bad.append(f'R1.8 구간 아래끝 합 {lo} ≤ 100 ≤ 위끝 합 {hi}가 아님')
            # v3.3(운영자 11-04 MRVL 분석): 구간만 쓰면 '하한 합 80·상한 합 115를 어떻게 읽나' 혼란 → 대표값 '약 N%'를 적고 합 100
            if mids and len(mids) == len(rows) and sum(mids) != 100: bad.append(f'v3.3 시나리오 대표값(약 N%) 합 {sum(mids)}% → 100%로 맞추기')
            if _v33 and len(mids) != len(rows): bad.append("v3.3 시나리오 가능성에 대표값 '높음 약 40%<br>(35~45%)'를 적고 합 100%")
            before = body[:st.start()][-600:]
            if not re.search(r'\d+번 중 \d+번|\d+회 중 \d+회|\d+번 모두', before): bad.append('R1.8 시나리오 표 앞 문단에 과거 빈도(N번 중 M번)를 먼저')
    # 통합 제작·검수 지침(2026-10-29) 1.4·2.2·2.4
    for m in re.finditer(r'\d[\d,.]*\s*[만억조]\s*\$|\$\s*\d[\d,.]*\s*[만억조]', body): bad.append(f"통합 1.4 '억$'·'$N억' 혼합 표기 금지 → '254억 달러' 또는 '254억 달러($25.4B)': {m.group(0)}")
    for l in body.split('\n'):
        if '$' in l and not l.lstrip().startswith(('|', '!', '<')) and not re.search(r'\(\$[\d.,]+[BMK]?\)', l): bad.append(f"통합 1.4 본문 서술은 '112.56달러'(기호 $는 표·괄호 축약에만): {l.strip()[:40]}")
    if max(asof, (re.search(r'^date:\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M) or [None, '0'])[1]) >= '2026-10-30':
        # v2.1 Master(2026-10-29): 모바일 375px에서 오른쪽 열이 잘리지 않게 모든 표 3열 이하, 기록표는 '이벤트일 · 공시 내용 | 당일 | N거래일 뒤'
        for tb in re.finditer(r'^(\|[^\n]*\|)\n\|[\s:|-]+\|\n((?:\|[^\n]*\|\n?)+)', body, re.M):
            h = [c.strip() for c in tb.group(1).strip('|').split('|')]
            rows = [[c.strip() for c in r.strip().strip('|').split('|')] for r in tb.group(2).strip().split('\n')]
            if len(h) > 3: bad.append(f"v2.1 표는 3열 이하(모바일 잘림): {' | '.join(h)[:50]}")
            for r in rows:
                for c in r:
                    if re.search(r'[+-−]?\d[\d.]*%\s+[+-−]\d[\d.]*%', re.sub(r'<br>|\(.*?\)', ' | ', c)): bad.append(f'v2.1 한 칸에 수치 두 개(| 누락?): {c[:30]}')
            di = next((k for k, c in enumerate(h) if c.startswith('당일')), None); ni = next((k for k, c in enumerate(h) if '거래일 뒤' in c), None)
            if di is None or ni is None: continue
            if not (h[0].startswith('이벤트일') and di == 1 and ni == 2): bad.append(f"v2.1 기록표 머리는 | 이벤트일 · 공시 내용 | 당일 | N거래일 뒤 |: {' | '.join(h)[:50]}")
            for r in rows:
                if not re.match(r'\**\d{4}\.\d{2}\.\d{2}\**<br>\S', r[0]): bad.append(f"v2.1 기록표 첫 칸은 '**YYYY.MM.DD**<br>공시 내용': {r[0][:30]}")
        # K10 블로거 티저 SEO(2026-10-29): 블로그 전용 고유 도입·질문 3개·영문 주소
        bi = (re.search(r'^blog_intro:\s*"?(.+?)"?\s*$', fm, re.M) or [None, ''])[1]
        if len(bi) < 200: bad.append(f'K10 머리말 blog_intro {len(bi)}자 < 200(블로그 전용 서술형 도입)')
        if len(re.findall(r'^\s+- q:', fm, re.M)) != 3: bad.append('K10 머리말 blog_faq 질문 3개(q·a)')
        if not re.search(r'^blog_slug:', fm, re.M): bad.append('K10 머리말 blog_slug(티커 + 사건 영문 키워드 + stock analysis)')
        for m in re.finditer(r'[^\n]{0,15}빚[^\n]{0,10}', body): bad.append(f"v2.1 1.2 '빚' 금지(빛 오인) → 부채·차입금: {m.group(0).strip()}")
        for l in body.split('\n'):
            m = re.match(r'- [□☐] (.*)', l)
            if m and not (re.match(r'(\d+월|\d+일|\d{4}년|다음 실적|분기 보고서|실적|매일|주간)', m.group(1)) and len(re.findall(r'\d[\d,.]*', m.group(1))) >= 2):
                bad.append(f"통합 2.4 체크리스트는 '□ [점검 시점] [수치 기준] 달성 여부': {m.group(1)[:40]}")
    if max(asof, (re.search(r'^date:\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M) or [None, '0'])[1]) >= '2026-11-02' or '--v23' in sys.argv:
        # v2.3(2026-11-02 운영자 TNXP 리포트 검토): 모바일 표 칸 너비·기록표 날짜 순서·공통 판정일·병합 전 가격·목차 아래 문단
        if re.sub(r'\s+', '', body.split('\n## ', 1)[0]): bad.append('v2.3 목차와 짧은 답 사이에 소속 없는 문단 → 짧은 답 핵심 콜아웃 아래로')
        for tb in re.finditer(r'^(\|[^\n]*\|)\n\|[\s:|-]+\|\n((?:\|[^\n]*\|\n?)+)', body, re.M):
            h = [c.strip() for c in tb.group(1).strip('|').split('|')]
            rows = [[c.strip() for c in r.strip().strip('|').split('|')] for r in tb.group(2).strip().split('\n')]
            ds = [re.match(r'\**(\d{4}\.\d{2}\.\d{2})', r[0]) for r in rows]
            ds = [d.group(1) for d in ds if d]
            if len(ds) >= 3 and ds != sorted(ds): bad.append(f'v2.3 기록표 날짜가 오름차순이 아님: {" → ".join(ds)[:60]}')
            if '가능성' in ' '.join(h) and len(rows) >= 3:
                tails = {(re.search(r'·\s*(\d+월 \d+일)\s*$', r[0]) or [None, None])[1] for r in rows}
                if len(tails) == 1 and None not in tails: bad.append(f'v2.3 시나리오 판정일이 모두 {tails.pop()} → 칸마다 반복하지 말고 머리에 한 번')
            if '액면병합' in body and h[0].startswith('이벤트일'):
                for r in rows:
                    if re.search(r'\d[\d.,]*달러', r[0]) and '병합' not in r[0]: bad.append(f"v2.3 병합 종목 기록표의 과거 가격은 '(병합 전 기준)' 또는 금액 빼기: {r[0][:30]}")
if max(asof, (re.search(r'^date:\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M) or [None, '0'])[1]) >= '2026-11-03' or '--v28' in sys.argv:
    # v2.8 Master(운영자 11-02): 시나리오 표 둘째 머리글 8자 이하(모바일에서 셋째 '가능성' 칸이 잘림), 체크리스트는 '☐'
    for tb in re.finditer(r'^(\|[^\n]*\|)\n\|[\s:|-]+\|', body, re.M):
        h = [c.strip() for c in tb.group(1).strip('|').split('|')]
        if any('가능성' in c for c in h) and len(h) >= 3 and len(h[1]) > 8: bad.append(f"v2.8 시나리오 표 둘째 머리글 '{h[1]}' {len(h[1])}자 → 8자 이하('조건(성장·무증자)')")
        if len(h) > 3: bad.append(f"v2.8 표 {len(h)}열 → 3열 이하: {' | '.join(h)[:50]}")
    for l in body.split('\n'):
        if re.match(r'- □ ', l): bad.append(f"v2.8 체크리스트 기호는 '☐': {l[:40]}")
    for w, alt in (('빚', '부채·차입금'), ('ETF', '상장지수펀드(ETF)')):
        if w == 'ETF' and 'ETF' in body and '상장지수펀드' not in body: bad.append("v2.8 'ETF' 첫 등장은 '상장지수펀드(ETF)'로 병기")
if max(asof, (re.search(r'^date:\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M) or [None, '0'])[1]) >= '2026-11-03' or '--v29' in sys.argv:
    # v2.9 1.6(운영자 11-02 LAES 블로그 검수): 원문(리포트·blog_intro·blog_faq) 단계에서 금지 어휘를 막아 블로그·대본까지 한 번에
    full = fm + '\n' + body
    for w, alt in ((r'(?<![가-힣])(이틀|사흘|나흘|닷새|열흘|열하루)', '2·3·4·5·10거래일'), (r'하루 만에', '1거래일 만에'),
                   (r'(?<![가-힣])(스무|스물|서른|마흔|쉰|예순|일흔|여든|아흔)(\s?(한|두|세|네|다섯|여섯|일곱|여덟|아홉))?\s?(번째|번|곳|개|거래일|회)', '20번째·36곳·53번·64번'),
                   (r'몫', '상승분·추가 상승 효과(TTS가 목숨으로)'), (r'빚', '부채·차입금'), (r'하는 안입니다', '하는 안건입니다'),
                   (r'(?<![가-힣\d])[123]상(?![가-힣])', '임상 1·2·3단계'), (r'특허 이의', '특허 분쟁')):
        for m in re.finditer(w, full): bad.append(f"v2.9 원문 금지 '{m.group(0)}' → {alt}")
    kp = re.findall(r'^\s*-\s*"?(.+?)"?\s*$', (re.search(r'^key_points:\n((?:\s+-.*\n)+)', fm, re.M) or [None, ''])[1], re.M)
    if len(kp) >= 3 and not re.search(r'일정|\d+/\d+|\d+월 \d+일', kp[2]): bad.append(f"v2.9 핵심 3줄의 셋째는 '향후 일정'(실적·해제일·전시회·증자 기한): {kp[2][:40]}")
if True:  # v3.0 음수 범위 검사도 모든 리포트
    # v3.0 Patch(운영자 11-03 PLUG 검수) 1.1: 숫자가 든 3열 표(기록표·비교표)는 1열이 길면 2·3열이 화면 밖으로 밀린다
    #   → 1열은 <br>로 끊어 줄당 18자 이하(** · * 꾸밈 제외, 공백 포함). 사이트는 3열 표를 56:22:22로 고정(build.py table-3)
    for tb in re.finditer(r'^(\|.*\|)\n\|[\s:|-]+\|\n((?:\|.*\|\n?)+)', body, re.M):
        h = [c.strip() for c in tb.group(1).strip('|').split('|')]
        rows = [[c.strip() for c in r.strip().strip('|').split('|')] for r in tb.group(2).strip().split('\n')]
        if len(h) != 3 or not rows: continue
        if sum(1 for r in rows if len(r) > 1 and re.search(r'\d', r[1]) and re.search(r'[%원$달러배]', r[1])) < len(rows) * 0.6: continue
        for r in rows:
            for seg in r[0].split('<br>'):
                v = re.sub(r'[*]', '', seg).strip()
                if len(v) > 18: bad.append(f"v3.0 3열 숫자 표 1열 한 줄 {len(v)}자 → <br>로 끊어 18자 이하: {v[:30]}")
    # 2: 음수 범위 '-1.2~-4.0%'는 물결표와 마이너스가 붙어 '~~'로 보임 → '-1.2%에서 -4.0% 사이' 또는 '-1.2% ~ -4.0%'
    for m in re.finditer(r'\d%?~-\d', fm + '\n' + body): bad.append(f"v3.0 음수 범위 붙여 쓰기 '{m.group(0)}' → '-1.2% ~ -4.0%' 또는 '…에서 … 사이'")
    for m in re.finditer(r'(?:^|[\s(])~\d+(?:\.\d+)?%', body, re.M): bad.append(f"v3.0 단독 '~숫자%'(마이너스 오타?): '{m.group(0).strip()}'")
if max(asof, (re.search(r'^date:\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M) or [None, '0'])[1]) >= '2026-11-04' or '--v31' in sys.argv:
    # v3.1 가독성 공통 지침(운영자 11-03 PLUG 가독성 분석 7.4/10): 깊이는 그대로, 읽는 부담은 절반으로
    secs = re.split(r'^## ', body, flags=re.M)
    for sec in secs[1:]:
        name = sec.split('\n', 1)[0][:12]
        prose = '\n'.join(l for l in sec.split('\n')[1:] if l.strip() and not l.lstrip().startswith(('|', '#', '!')) and not l.startswith('> **국면 정의'))
        m = re.search(r'국면 [A-Z](?![A-Za-z])(.{0,2})', prose)
        if m and not m.group(1).startswith('('): bad.append(f"v3.1 '{name}' 첫 '국면 X'에 쉬운 말 병기 → '국면 C(매수세가 서서히 사라지는 단계)'")
    p5 = re.search(r'^## 5부.*?(?=^## )', body, re.M | re.S)
    if '가능성(추정)' in body and p5:
        t5 = p5.group(0)
        if '주관적' not in t5 or not re.search(r'(주가|가격)(가|이)? (오를|상승|방향)', t5): bad.append("v3.1 5부에 가능성의 뜻(분석자의 주관적 추정, 주가가 오를 확률이 아님)을 밝히는 문장이 없음")
        if not all(k in t5 for k in ('**확인된 사실:**', '**과거 기록:**', '**추정:**')): bad.append("v3.1 5부에 '**확인된 사실:** · **과거 기록:** · **추정:**' 구분 문단이 없음")
    prose_all = '\n'.join(l for l in body.split('\n') if l.strip() and not l.lstrip().startswith(('|', '#', '!')))
    from collections import Counter
    for num, c in Counter(re.findall(r'[-+]?\d+\.\d+%', prose_all)).items():
        if c > 3: bad.append(f"v3.1 같은 숫자 {num}가 본문 문단에 {c}번 → 한 번 정의하고 뒤에서는 뜻으로 부르기(3번 이하)")
    for para in [x for x in body.split('\n\n') if x.strip() and not x.lstrip().startswith(('|', '#', '!', '>', '-'))]:
        n = len(re.findall(r'\d[\d,.]*', re.sub(DATE, '', para)))
        if n >= 10: bad.append(f"v3.1 숫자 {n}개 몰린 문단 → 핵심 숫자는 표 한 줄로 올리고 문단은 뜻 설명: {para[:40]}…")
if _v33:
    # v3.3(운영자 11-04 MRVL 분석): 기간 등락률은 기준 종가를 밝히고, 6부 끝은 '기억할 판단 기준'으로 닫는다
    for sent in re.split(r'(?<=[.?!])\s+', body):
        if re.search(r'\d+거래일 (동안|만에)[^.]*?[-+]?\d+(\.\d+)?%', sent) and '종가' not in sent:
            bad.append(f"v3.3 'N거래일 동안 X%'에는 기준 종가(○월 ○일 종가 대비)를 같은 문장에: {sent[:40]}…")
    p6 = re.search(r'^## 6부[^\n]*\n(.*)', body, re.S | re.M)
    if p6 and '판단 기준' not in p6.group(1): bad.append("v3.3 6부 끝에 '**기억할 판단 기준 세 가지:**' 한 문단(이번 사건의 핵심 차이 3개)")
if _v32:
    # v3.2(운영자 11-04 SLDP 가독성 분석): 독자가 궁금해하는 순서대로 — 문제 제기형 도입, 기록표 기준의 이유, 4→5부 다리
    sa = re.search(r'^## 짧은 답\n(.*?)(?=^## )', body, re.S | re.M)
    if sa:
        ps = [x.strip() for x in sa.group(1).split('\n\n') if x.strip() and not x.lstrip().startswith(('>', '|', '#'))]
        if not ps or '?' not in ps[0]: bad.append("v3.2 짧은 답 첫 문단은 핵심 모순을 묻는 질문으로 시작(예: '매출은 93% 줄었습니다. 그런데 주가는 왜 무너지지 않았을까요?')")
        if '국면 정의' in sa.group(1): bad.append('v3.2 국면 정의 상자는 짧은 답이 아니라 국면을 처음 진단하는 5부에')
    p3 = re.search(r'^## 3부[^\n]*\n(.*?)(?=^\|)', body, re.S | re.M)
    if p3 and not re.search(r'때문|비슷한 조건|같은 조건', p3.group(1)): bad.append('v3.2 3부 기록표 앞에 사례를 고른 기준과 그 이유(지금과 비슷한 조건이기 때문)를 한 문장')
    p4 = re.search(r'^## 4부[^\n]*\n(.*?)(?=^## )', body, re.S | re.M)
    if p4:
        last = [x for x in p4.group(1).strip().split('\n\n') if x.strip()][-1]
        if not re.search(r'(확인할|볼) (것|조건)은|두 가지', last): bad.append('v3.2 4부 마지막 문단은 과거 기록 → 앞으로 확인할 조건 두 가지로 5부 시나리오 축을 미리 세움')
print('\n'.join(bad) if bad else f'EASY_OK 문장 {len(sents)} · 90자↑ {len(longs)} · 숫자 많은 문장 {len(dense)}')
sys.exit(1 if bad else 0)
