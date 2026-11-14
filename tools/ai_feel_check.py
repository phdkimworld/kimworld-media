# 'AI 느낌' 틀 검사(SKILL 8.0.2, 75회차 AGNC 첫 적용).
# 사용: python3 ai_feel_check.py <narration.txt 또는 리포트.md> [...]
#  - 대본·리포트: 다리 말 '그렇다면' 2번 이하(직전 6회차 RDW·JOBY·EOSE·LCID·IREN·NBIS 대본·리포트에 2~6번씩 같은 틀)
#  - 공통: 번역투·상투어(흥미롭게도·주목할 점은·결론적으로·~에 있어서·~를 통해·~하는 것이 중요합니다) 0개
#  - 대본: 같은 말로 시작하는 문단이 3개 연속이면 경고
#  - 대본(79회차 QS): '첫 번째 단서'(group_check 기준 문단)를 뺀 서수 문단('두 번째 단서는·세 번째 단서는·첫 번째 가설은') 3개 이상이면 경고(78회차 CEG 대본 4개)
#  - 리포트(.md): 서수로 여는 문단('첫째·둘째·셋째', '첫 번째 …은') 3개 이상이면 경고(78회차 CEG: 직전 RUM 리포트 '첫 번째 힘은·두 번째 힘은·첫째 갈래는·둘째 갈래는·셋째 갈래는' 5번)
import sys, re
STOCK = ['흥미롭게도', '주목할 점은', '주목할 만한', '결론적으로', '에 있어서', '를 통해', '을 통해', '하는 것이 중요합니다', '라는 점입니다', '살펴보도록 하겠습니다', '반론도 있습니다']  # '반론도 있습니다' 81회차 LAES: BTQ 77·CEG 78·QS 79·CBRS 80 대본 4편 모두 반론 문단을 같은 말로 엶
bad = []
for p in sys.argv[1:]:
    t = open(p, encoding='utf-8').read()
    if p.endswith('.md') and t.startswith('---'):
        t = t.split('\n---\n', 1)[-1]
        t = re.sub(r'^\s*(title|url|date):.*$', '', t, flags=re.M)
    paras = [x.strip() for x in t.split('\n\n') if x.strip() and not x.lstrip().startswith(('|', '#', '>', '!', '-'))]
    nb = len(re.findall('그렇다면', t))
    if nb > 2: bad.append(f"{p}: 다리 말 '그렇다면' {nb}번 > 2 — 장면·숫자·이유로 바로 넘기기(직전 6회차 대본·리포트 4~6번씩)")
    for w in STOCK:
        n = len(re.findall(w, t))
        if n: bad.append(f"{p}: 상투어·번역투 '{w}' {n}번")
    heads = [re.split(r'[ ,]', x, maxsplit=1)[0] for x in paras]
    for i in range(len(heads) - 2):
        if heads[i] == heads[i+1] == heads[i+2] and len(heads[i]) > 1: bad.append(f"{p}: 문단 {i+1}~{i+3}이 모두 '{heads[i]}'로 시작"); break
    ns = len(re.findall('셈입니다', t))  # 83회차 SLDP: ASST 82 대본 4번·LAES 81·CBRS 80 2번씩 해석 꼬리 '…셈입니다'
    if not p.endswith('.md') and ns > 2: bad.append(f"{p}: 해석 꼬리 '셈입니다' {ns}번 > 2 — 숫자 뒤 뜻은 다른 말로(…라는 말입니다·…와 같습니다) 또는 생략")
    od = [x[:14] for x in paras if re.match(r'(첫째|둘째|셋째|넷째|(첫|두|세|네) 번째 [가-힣]+(은|는))', x)]
    if not p.endswith('.md'): od = [x for x in od if not x.startswith('첫 번째 단서')]
    if True:
        if len(od) >= 3: bad.append(f"{p}: 서수로 여는 문단 {len(od)}개 ≥ 3 — 주제 낱말·날짜·장면으로 열기: " + ' / '.join(od))
print('\n'.join(bad) if bad else 'AI_FEEL_OK')
sys.exit(1 if bad else 0)
