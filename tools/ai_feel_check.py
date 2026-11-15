# 'AI 느낌' 틀 검사(SKILL 8.0.2, 75회차 AGNC 첫 적용).
# 사용: python3 ai_feel_check.py <narration.txt 또는 리포트.md> [...]
#  - 대본·리포트: 다리 말 '그렇다면' 2번 이하(직전 6회차 RDW·JOBY·EOSE·LCID·IREN·NBIS 대본·리포트에 2~6번씩 같은 틀)
#  - 공통: 번역투·상투어(흥미롭게도·주목할 점은·결론적으로·~에 있어서·~를 통해·~하는 것이 중요합니다) 0개
#  - 대본: 같은 말로 시작하는 문단이 3개 연속이면 경고
#  - 대본(79회차 QS): '첫 번째 단서'(group_check 기준 문단)를 뺀 서수 문단('두 번째 단서는·세 번째 단서는·첫 번째 가설은') 3개 이상이면 경고(78회차 CEG 대본 4개)
#  - 리포트(.md): 서수로 여는 문단('첫째·둘째·셋째', '첫 번째 …은') 3개 이상이면 경고(78회차 CEG: 직전 RUM 리포트 '첫 번째 힘은·두 번째 힘은·첫째 갈래는·둘째 갈래는·셋째 갈래는' 5번)
#  - 대본(87회차 GPUS): 마무리 틀 '처음 질문으로 돌아가겠습니다'·'숫자로 정리하면'·'지켜볼 날은 두 번입니다'(TEM 84·QXO 85·FIG 86 세 편 같은 문장)
#  - 리포트(.md, 86회차 FIG): easy_check v3.4 안내 예시 '나란히 놓으면 공통점이 하나 보입니다'를 그대로 베낀 2부 묶음 문장(11월 리포트 20편) — 이번 사건들의 실제 연결을 그 자리의 말로
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
print('\n'.join(bad) if bad else 'AI_FEEL_OK')
sys.exit(1 if bad else 0)
