# 'AI 느낌' 틀 검사(SKILL 8.0.2, 75회차 AGNC 첫 적용).
# 사용: python3 ai_feel_check.py <narration.txt 또는 리포트.md> [...]
#  - 대본·리포트: 다리 말 '그렇다면' 2번 이하(직전 6회차 RDW·JOBY·EOSE·LCID·IREN·NBIS 대본·리포트에 2~6번씩 같은 틀)
#  - 공통: 번역투·상투어(흥미롭게도·주목할 점은·결론적으로·~에 있어서·~를 통해·~하는 것이 중요합니다) 0개
#  - 대본: 같은 말로 시작하는 문단이 3개 연속이면 경고
#  - 대본(79회차 QS): '첫 번째 단서'(group_check 기준 문단)를 뺀 서수 문단('두 번째 단서는·세 번째 단서는·첫 번째 가설은') 3개 이상이면 경고(78회차 CEG 대본 4개)
#  - 리포트(.md): 서수로 여는 문단('첫째·둘째·셋째', '첫 번째 …은') 3개 이상이면 경고(78회차 CEG: 직전 RUM 리포트 '첫 번째 힘은·두 번째 힘은·첫째 갈래는·둘째 갈래는·셋째 갈래는' 5번)
#  - 대본(87회차 GPUS): 마무리 틀 '처음 질문으로 돌아가겠습니다'·'숫자로 정리하면'·'지켜볼 날은 두 번입니다'(TEM 84·QXO 85·FIG 86 세 편 같은 문장)
#  - 리포트(.md, 86회차 FIG): easy_check v3.4 안내 예시 '나란히 놓으면 공통점이 하나 보입니다'를 그대로 베낀 2부 묶음 문장(11월 리포트 20편) — 이번 사건들의 실제 연결을 그 자리의 말로
#  - 11-27 외부 규칙 반영(운영자 Threads 공유 '티 안 나게 하는 스킬 4개' → skill/runbooks/taste.md 13절): im-not-ai(epoko77-ai/im-not-ai, MIT)
#    한국어 AI 티 분류표·어휘표와 humanizer(blader/humanizer, MIT) 패턴 가운데 우리 글에 맞는 것만 옮겨 고쳐 씀. 기준은 최근 50 대본·52 쇼츠·79 리포트(11월)에서 잼:
#    STOCK2(실패, 기준 코퍼스 0건): 이중 피동·'단순한 X를 넘어'·의의 과장·결말 공식·자기 이야기·과장어·챗봇 잔재·사전 은유
#    개수(실패/경고): 'A가 아니라 B' 5↑/4, '~다는 것입니다·뜻입니다' 4↑/3, 같은 '~수 있습니다' 5↑/4, '결국' 3↑/2, '즉' 3↑, 본문 대시(—) 3↑,
#    이중 조사('에서의·으로부터의', '앞으로의' 제외) 3↑/2, '짚다' 3↑/2, '…을 가르는 기준·두 축' 경고 2↑, 문장 머리 같은 낱말 세 문장 연속 경고
#  - 11-27 content-skills(artemnovitckii/content-skills, MIT) viral-hooks·storytelling에서 옮김(taste.md 14절), 최근 50 대본에서 0건:
#    대본(narration*) 첫 문장이 인사·예고('안녕하세요·여러분·오늘은·자,·잠깐·이번 영상·끝까지 보시면·믿기 어려')로 열리면 실패(훅 DELAY),
#    '그리고·그 뒤·이어서·또' 로 여는 문장 3연속은 경고('그리고 나서' 나열 → 그런데·그래서로 잇기)
#    경고(WARN)는 종료 코드에 넣지 않는다. 연결어미 뒤 쉼표(im-not-ai C-11)는 TTS 숨 자리라 넣지 않았다(리포트도 11~33개가 기본 문체).
import sys, re
STOCK = ['흥미롭게도', '주목할 점은', '주목할 만한', '결론적으로', '에 있어서', '를 통해', '을 통해', '하는 것이 중요합니다', '라는 점입니다', '살펴보도록 하겠습니다', '반론도 있습니다']  # '반론도 있습니다' 81회차 LAES: BTQ 77·CEG 78·QS 79·CBRS 80 대본 4편 모두 반론 문단을 같은 말로 엶

sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from ai_tells import STOCK2  # 11-27 im-not-ai·humanizer·taste.md 3절 어휘(실패)
COUNTS = [  # (정규식, 실패 기준, 경고 기준, 이름·고치는 법)
    (r'(이|가) 아니라|것이 아니라|것은 아닙니다', 5, 4, "'A가 아니라 B' 대구 → 한 번만 살리고 나머지는 B만 평서문으로"),
    (r'다는 것입니다|다는 뜻입니다|라는 뜻입니다|라는 것입니다', 4, 3, "'~다는 것입니다·뜻입니다' 꼬리 → '~다'로 바로 닫기"),
    (r'(?<![가-힣])결국', 3, 2, "결산 '결국' → 1번만 남기고 인과를 구체로"),
    (r'(?<![가-힣])즉[,\s]', 3, 99, "'즉' → 생략하거나 '말하자면'·문장 나누기"),
    (r'—', 3, 99, "본문 대시(—) → 쉼표·괄호·문장 나누기"),
    (r'(에서의|에로의|으로부터의|로부터의|에의|(?<!앞)으로의)\s', 3, 2, "이중 조사 '에서의·으로의' → 절로 풀기('미국에서의 매출' → '미국 매출')"),
    (r'짚[어고는었]|짚을', 3, 2, "'짚다' → '보다·확인하다'"),
    (r'(을|를) 가르는 (것은|기준|지점|변수)|(?<![가-힣])(두|세|네) 축(?![가-힣])', 99, 2, "'…을 가르는 기준'·'두 축' 틀 → '판단 기준'처럼 평범하게"),
]
bad = []
warn = []
for p in sys.argv[1:]:
    t = open(p, encoding='utf-8').read()
    if p.endswith('.md') and t.startswith('---'):
        t = t.split('\n---\n', 1)[-1]
        t = re.sub(r'^\s*(title|url|date):.*$', '', t, flags=re.M)
    paras = [x.strip() for x in t.split('\n\n') if x.strip() and not x.lstrip().startswith(('|', '#', '>', '!', '-'))]

    pr = '\n'.join(l for l in t.split('\n') if l.strip() and not l.lstrip().startswith(('|', '#', '>', '!', '-', '*', '<')))
    for rx, why in STOCK2:
        hits = [m.group(0) for m in re.finditer(rx, pr)]
        if hits: bad.append(f"{p}: AI 티 어휘 {len(hits)}번 {sorted(set(hits))[:3]} — {why}")
    n_can = max([len(re.findall(r'%s 수 있습니다' % v, pr)) for v in ('할', '될', '볼', '일')] + [0])
    if n_can >= 5: bad.append(f"{p}: 같은 '~수 있습니다' {n_can}번 ≥ 5 — 단정으로 바꾸지 말고 일부만 '~할 수도 있습니다·여지가 있습니다'로 나누기")
    elif n_can >= 4: warn.append(f"{p}: 같은 '~수 있습니다' {n_can}번")
    for rx, fl, wl, why in COUNTS:
        if rx == '—' and re.search(r'(description|pinned)', p): continue  # 설명란·고정댓글 광고 줄('— 광고 —')은 운영자 원문 틀
        n = len(re.findall(rx, pr))
        if n >= fl: bad.append(f"{p}: {why} ({n}번 ≥ {fl})")
        elif n >= wl: warn.append(f"{p}: {why} ({n}번)")
    ss = [s.strip() for s in re.split(r'(?<=[.?!])\s+', pr) if s.strip()]
    hs = [(s.split() or [''])[0] for s in ss]
    for i in range(len(hs) - 2):
        if hs[i] == hs[i+1] == hs[i+2] and len(hs[i]) > 1: warn.append(f"{p}: 세 문장 연속 '{hs[i]}'로 시작 — 합치거나 주어·행동으로 열기(humanizer 7)"); break
    if 'narration' in __import__('os').path.basename(p) and ss and re.match(r'(안녕하세요|여러분|오늘은|오늘도|자,|잠깐|이번 영상|끝까지 보시면|믿기 어려)', ss[0]):
        bad.append(f"{p}: 첫 문장이 인사·예고로 시작('{ss[0][:20]}') — 회사 이름과 핵심 모순(숫자)으로 바로 열기(V1 훅, viral-hooks DELAY)")
    run = 0
    for x_ in ss:
        run = run + 1 if re.match(r'(그리고|그 뒤|그 다음|이어서|또한?)[ ,]', x_) else 0
        if run >= 3: warn.append(f"{p}: '그리고·그 뒤·이어서'로 여는 문장 3연속 — 사건 나열 대신 '그런데·그래서'로 긴장 잇기(storytelling)"); break
    nb = len(re.findall('그렇다면', t))
    if nb > 2: bad.append(f"{p}: 다리 말 '그렇다면' {nb}번 > 2 — 장면·숫자·이유로 바로 넘기기(직전 6회차 대본·리포트 4~6번씩)")
    for w in STOCK:
        n = len(re.findall(w, t))
        if n: bad.append(f"{p}: 상투어·번역투 '{w}' {n}번")
    heads = [re.split(r'[ ,]', x, maxsplit=1)[0] for x in paras]
    for i in range(len(heads) - 2):
        if heads[i] == heads[i+1] == heads[i+2] and len(heads[i]) > 1: bad.append(f"{p}: 문단 {i+1}~{i+3}이 모두 '{heads[i]}'로 시작"); break
    if p.endswith('.md') and re.search(r'나란히 놓으면 공통점이 하나 보입니다', t): bad.append(f"{p}: 2부 묶음 문장이 easy_check 예시 그대로('나란히 놓으면 공통점이 하나 보입니다', 11월 리포트 20편) — '…는 따로 나온 숫자지만 한 방향으로 겹쳤습니다'처럼 이번 사건의 연결을 직접")
    ns = len(re.findall('셈입니다', t))  # 83회차 SLDP: ASST 82 대본 4번·LAES 81·CBRS 80 2번씩 해석 꼬리 '…셈입니다'
    if not p.endswith('.md') and ns > 2: bad.append(f"{p}: 해석 꼬리 '셈입니다' {ns}번 > 2 — 숫자 뒤 뜻은 다른 말로(…라는 말입니다·…와 같습니다) 또는 생략")
    if p.endswith('.md') and 'style: story' in t:  # 89회차 RKLB: 88 SERV 발행 전 심사 9번 — 이야기형 리포트 결론·위치 문단이 '정리하면 …'·'이렇게 정리할 수 있습니다' 요약 틀로 앞 내용을 되풀이(GPUS 87·SERV 88, RKLB 89 초안에도 2번)
        body = t.split('## 숫자로 다시 보기')[0]
        sm = re.findall(r'(?m)^(?:정리하면|요약하면|한 줄로 말하면)[^\n]{0,30}|이렇게 정리할 수 있습니다', body)
        if sm: bad.append(f"{p}: 리포트 본문 요약 틀 {len(sm)}번 {sm[:2]} — 결론은 앞 장면을 되풀이하지 말고 처음 질문의 답과 이유로 닫기")
    if not p.endswith('.md'):  # 87회차 GPUS: TEM 84·QXO 85·FIG 86 대본 세 편이 같은 마무리 틀('처음 질문으로 돌아가겠습니다'·'숫자로 정리하면, 지난 리포트가 말한 …'·'지켜볼 날은 두 번입니다')
        tpl = [w for w in ('처음 질문으로 돌아가겠습니다', '숫자로 정리하면', '지켜볼 날은 두 번입니다') if w in t]
        if tpl: bad.append(f"{p}: 마무리 틀 반복 {tpl} (TEM 84·QXO 85·FIG 86 같은 문장) — 이번 회차의 답·날짜를 그 자리의 말로")
    od = [x[:14] for x in paras if re.match(r'(첫째|둘째|셋째|넷째|(첫|두|세|네) 번째 [가-힣]+(은|는))', x)]
    if not p.endswith('.md'): od = [x for x in od if not x.startswith('첫 번째 단서')]
    if True:
        if len(od) >= 3: bad.append(f"{p}: 서수로 여는 문단 {len(od)}개 ≥ 3 — 주제 낱말·날짜·장면으로 열기: " + ' / '.join(od))
for w in warn: print('WARN ' + w)
print('\n'.join(bad) if bad else 'AI_FEEL_OK' + (f' (경고 {len(warn)})' if warn else ''))
sys.exit(1 if bad else 0)
