# 지난 예측 성적표와 시나리오 가능성을 합성 전에 확인한다(운영자 지시 2026-10-25: "지난 리포트들이 있는 경우에 거기서 어떤 예측을 했는지를 정리하는 내용을 영상에 초반에 포함", "리포트엔 각 시나리오 각각에 대한 가능성 예측을 추가", "과거 예측 정리 및 결과 보고는 쓰레드 등 다른 공유 포스트에도 적용").
# 사용: python3 prev_calls_check.py <작업 폴더(video)> <리포트.md> [social/queue/*.json …]
#  - 모든 리포트: 5.6의 시나리오마다 '가능성(추정): 약 N%'
#  - 후속편('## 지난 리포트 이후'가 있는 리포트): 대본 앞 6문단 안 성적표 문단('리포트에서' + 맞았/빗나/확인 전/적중),
#    리포트의 '지난 예측 성적' 한 줄, 넘겨준 대기열 글마다 '지난 예측' 줄
import sys, re, os, json
V, R = sys.argv[1], sys.argv[2]; Q = sys.argv[3:]
rep = open(R, encoding='utf-8').read(); bad = []
# 시나리오 절: 옛 형식 '### 5.6 …' 또는 R1.6 말로 쭉 형식 '### 앞으로 일어날 수 있는 일'(2026-10-27, 소제목 번호 없음)
# 이야기형(style: story, 11-15~) 부록은 '### 5부 표 · 앞으로 일어날 …'·'### 앞으로 일어날 …'처럼 앞에 이름이 붙고, 부록이 글 끝이라 다음 ##가 없을 수 있다(88회차 SERV)
m = re.search(r'^### (?:5\.6|[^\n]*앞으로 일어날).*?(?=^##|\Z)', rep, re.S | re.M)
if not m: bad.append("리포트에 시나리오 절('### 5.6' 또는 '### 앞으로 일어날 수 있는 일')이 없음")
else:
    sec = m.group(0)
    sc = sorted(set(re.findall(r'시나리오 \d', sec)))
    pr = re.findall(r'가능성\(추정\)[^%\n]*?\d+%', sec)
    # R1.7 시나리오 표(2026-10-28): 머리 줄에 '가능성'이 있는 표면 그 표의 행마다 % 하나로 센다
    for t in re.findall(r'(?:^\|.*\n)+', sec, re.M):
        ln = t.strip().split('\n')
        if '가능성' in ln[0]:
            pr += [r for r in ln[2:] if re.search(r'\d+%', r)]
    if sc and len(pr) < len(sc): bad.append(f'시나리오 {len(sc)}개 중 가능성 % {len(pr)}개')
    elif not sc and len(pr) < 3: bad.append(f'시나리오 절에 가능성(추정) % {len(pr)}개(3개 이상)')
    # 유력 갈래 보정(운영자 11-18 "유력 갈래가 계속 틀리는 이유 분석해서 예측 방식 고쳐", review/predictions/README '유력 갈래 오답 분석'):
    # 가장 높은 갈래는 40% 이하가 기본. 넘기려면 장부 기저율(n≥5)이 받쳐야 하고, 모든 회차는 research/prob_basis.md(기저율·조정·사전 부검)가 있어야 한다
    nums = [max(int(x) for x in re.findall(r'(\d+)\s*%', p)) for p in pr if re.findall(r'(\d+)\s*%', p)]
    top = max(nums) if nums else 0
    pb = os.path.join(os.path.dirname(os.path.abspath(V)), 'research', 'prob_basis.md')
    if os.environ.get('PROB_BASIS') != 'skip':
        if not os.path.exists(pb):
            bad.append("research/prob_basis.md 없음: 갈래마다 '기저율(장부 n)', '조정 근거(±15%p 이내)', 유력 갈래 '틀린다면 이유' 한 줄(사전 부검)")
        else:
            t = open(pb, encoding='utf-8').read()
            for k in ('기저율', '틀린다면'):
                if k not in t: bad.append(f"prob_basis.md에 '{k}' 줄 없음")
            if top > 40 and not re.search(r'n\s*[=≥]\s*([5-9]|\d\d)', t):
                bad.append(f'유력 갈래 {top}% > 40%: 장부 기저율 n≥5 근거가 prob_basis.md에 없음(없으면 40% 이하로)')
# 이야기형 후속편은 '## 지난 리포트 이후' 소제목이 없다 → 같은 티커 지난 리포트 링크(/r/<티커>-…)로 후속편을 알아본다(88회차 SERV: GPUS 87회차가 '첫 리포트'로 읽혀 대본·대기열 성적 줄 검사가 꺼져 있었음)
_tk = (re.search(r'^ticker:\s*"?([A-Za-z0-9.]+)', rep, re.M) or [None, '#'])[1].lower()
_slug = os.path.basename(R)[:-3]
follow = '## 지난 리포트 이후' in rep or any(x != _slug for x in re.findall(r'\(/r/(' + re.escape(_tk) + r'-[0-9a-z-]+)/\)', rep))
if follow:
    nar = os.path.join(V, 'narration.txt')
    if os.path.exists(nar):
        paras = [p for p in open(nar, encoding='utf-8').read().split('\n\n') if p.strip()][:6]
        if not any('리포트에서' in p and re.search(r'맞았|빗나|확인 전|적중', p) for p in paras):
            bad.append('후속편인데 대본 앞 6문단 안에 지난 예측 성적표 문단이 없음')
    if '지난 예측 성적' not in rep: bad.append("후속편인데 리포트에 '지난 예측 성적' 한 줄이 없음")
    for q in Q:
        d = json.load(open(q, encoding='utf-8'))
        txt = d.get('text', '') + json.dumps(d.get('channel_text', {}), ensure_ascii=False)
        if '지난 예측' not in txt: bad.append(f"{os.path.basename(q)}에 '지난 예측' 줄이 없음")
# 예측 장부 대조(11-18): 리포트 '지난 예측' 적중·빗나감 숫자가 장부 --score와 다르면 경고만(실패 아님)
if follow:
    try:
        import subprocess as _sp
        _o = _sp.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pred_ledger.py'), '--score', _slug], capture_output=True, text=True, timeout=60).stdout
        _l = re.search(r'적중·일어남 (\d+) · 빗나감·안 일어남 (\d+)', _o)
        _r = re.search(r'지난 예측[^\n]*?적중 (\d+)[^\n]*?빗나감 (\d+)', rep)
        if _l and _r and (_l.group(1), _l.group(2)) != (_r.group(1), _r.group(2)):
            print(f"LEDGER_DIFF 리포트 적중 {_r.group(1)}·빗나감 {_r.group(2)} vs 장부 {_l.group(1)}·{_l.group(2)} — 장부를 --set으로 채우거나 리포트 숫자를 장부에 맞춘다")
    except Exception: pass
print('\n'.join(bad) if bad else f"PREV_CALLS_OK {'후속편' if follow else '첫 리포트'}")
sys.exit(1 if bad else 0)
