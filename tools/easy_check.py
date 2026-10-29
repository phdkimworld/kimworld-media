# 리포트가 비전문가도 읽히는지 발행 전에 본다(운영자 지시 2026-10-26: "리포트가 좀 어려운거 같아. 딥다이브는 좋은데. 설명을 앞으로는 비전문가도 알아먹게 좀 해줘").
# 사용: python3 easy_check.py <리포트.md> [--glossary <사이트 data/glossary.yaml>]
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
        if h[:2] != ['지난 점검 항목', '당시 판단 기준'] or not h[2].startswith('실제 결과') or h[-1] != '판정':
            bad.append('R1.8 지난 리포트 판정표 머리는 | 지난 점검 항목 | 당시 판단 기준 | 실제 결과(<날짜>) | 판정 |')
        for r in re.findall(r'^\|(?!\s*-)(.*)\|\s*$', pt.group(1), re.M)[1:]:
            j = r.split('|')[-1].strip()
            if not re.match(r'(적중|빗나감|부분 적중|진행 중)', j): bad.append(f'R1.8 판정은 적중/빗나감/부분 적중/진행 중: {j[:20]}')
    for l in body.split('\n'):
        if re.search(r'[□☐]', l) and not re.match(r'- [□☐] \S', l): bad.append(f'R1.8 체크리스트는 한 단계 "- □ 항목": {l.strip()[:40]}')
    asof = (re.search(r'^data_as_of:\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M) or [None, '0'])[1]
    if asof >= '2026-10-29' and '가능성(추정)' in body:
        st = re.search(r'^\|[^\n]*가능성\(추정\)[^\n]*\|\n(?:^\|.*\n)+', body + '\n', re.M)
        if st:
            rows = [[c.strip() for c in r.strip().strip('|').split('|')] for r in st.group(0).strip().split('\n')[2:]]
            ax = [i for i in range(len(rows[0])) if all(r[i] in ('○', '×') for r in rows if i < len(r))]
            if len(ax) < 2 or len({tuple(r[i] for i in ax[:2]) for r in rows}) != 4 or len(rows) != 4: bad.append('R1.8 시나리오는 두 축(○/×) 2×2 네 칸')
            lo = hi = 0
            for r in rows:
                m = re.search(r'(높음|중간|낮음)\s*\((\d+)~(\d+)%\)', ' '.join(r))
                if not m: bad.append(f'R1.8 가능성은 높음(35~45%)·중간(20~30%)·낮음(10~20%) 구간: {r[0][:20]}'); continue
                lo += int(m.group(2)); hi += int(m.group(3))
            if rows and not lo <= 100 <= hi: bad.append(f'R1.8 구간 아래끝 합 {lo} ≤ 100 ≤ 위끝 합 {hi}가 아님')
            before = body[:st.start()][-600:]
            if not re.search(r'\d+번 중 \d+번|\d+회 중 \d+회|\d+번 모두', before): bad.append('R1.8 시나리오 표 앞 문단에 과거 빈도(N번 중 M번)를 먼저')
    # 통합 제작·검수 지침(2026-10-29) 1.4·2.2·2.4
    for m in re.finditer(r'\d[\d,.]*\s*[만억조]\s*\$|\$\s*\d[\d,.]*\s*[만억조]', body): bad.append(f"통합 1.4 '억$'·'$N억' 혼합 표기 금지 → '254억 달러' 또는 '254억 달러($25.4B)': {m.group(0)}")
    for l in body.split('\n'):
        if '$' in l and not l.lstrip().startswith(('|', '!', '<')) and not re.search(r'\(\$[\d.,]+[BMK]?\)', l): bad.append(f"통합 1.4 본문 서술은 '112.56달러'(기호 $는 표·괄호 축약에만): {l.strip()[:40]}")
    if asof >= '2026-10-30':
        for tb in re.finditer(r'^(\|[^\n]*\|)\n\|[\s:|-]+\|\n((?:\|[^\n]*\|\n?)+)', body, re.M):
            h = [c.strip() for c in tb.group(1).strip('|').split('|')]
            di = next((i for i, c in enumerate(h) if c.startswith('당일')), None); ni = next((i for i, c in enumerate(h) if '거래일 뒤' in c), None)
            if di is None or ni is None: continue
            rows = [[c.strip() for c in r.strip().strip('|').split('|')] for r in tb.group(2).strip().split('\n')]
            if not re.search(r'일|날짜', h[0]) or any(not re.match(r'\d{4}\.\d{2}\.\d{2}', r[0]) for r in rows): bad.append(f"통합 2.2 기록표 첫 열은 이벤트 일자(YYYY.MM.DD): {' | '.join(h)[:50]}")
            if not any(re.search(r'규모|물량|주식|금액|수량', c) for c in h[1:di]): bad.append(f"통합 2.2 기록표에 물량·규모 열(일자와 당일 사이)이 없음: {' | '.join(h)[:50]}")
            if di > ni: bad.append('통합 2.2 기록표 열 순서는 당일 → N거래일 뒤')
            if not re.search(r'함께|동반|내용|이벤트', h[-1]): bad.append(f"통합 2.2 기록표 마지막 열은 동반 이벤트(텍스트): {h[-1]}")
        for l in body.split('\n'):
            m = re.match(r'- [□☐] (.*)', l)
            if m and not (re.match(r'(\d+월|\d+일|\d{4}년|다음 실적|분기 보고서|실적|매일|주간)', m.group(1)) and len(re.findall(r'\d[\d,.]*', m.group(1))) >= 2):
                bad.append(f"통합 2.4 체크리스트는 '□ [점검 시점] [수치 기준] 달성 여부': {m.group(1)[:40]}")
print('\n'.join(bad) if bad else f'EASY_OK 문장 {len(sents)} · 90자↑ {len(longs)} · 숫자 많은 문장 {len(dense)}')
sys.exit(1 if bad else 0)
