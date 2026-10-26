# 지난 예측 성적표와 시나리오 가능성을 합성 전에 확인한다(운영자 지시 2026-10-25: "지난 리포트들이 있는 경우에 거기서 어떤 예측을 했는지를 정리하는 내용을 영상에 초반에 포함", "리포트엔 각 시나리오 각각에 대한 가능성 예측을 추가", "과거 예측 정리 및 결과 보고는 쓰레드 등 다른 공유 포스트에도 적용").
# 사용: python3 prev_calls_check.py <작업 폴더(video)> <리포트.md> [social/queue/*.json …]
#  - 모든 리포트: 5.6의 시나리오마다 '가능성(추정): 약 N%'
#  - 후속편('## 지난 리포트 이후'가 있는 리포트): 대본 앞 6문단 안 성적표 문단('리포트에서' + 맞았/빗나/확인 전/적중),
#    리포트의 '지난 예측 성적' 한 줄, 넘겨준 대기열 글마다 '지난 예측' 줄
import sys, re, os, json
V, R = sys.argv[1], sys.argv[2]; Q = sys.argv[3:]
rep = open(R, encoding='utf-8').read(); bad = []
m = re.search(r'^### 5\.6.*?(?=^##)', rep, re.S | re.M)
if not m: bad.append('리포트에 5.6 절이 없음')
else:
    sec = m.group(0)
    sc = re.findall(r'시나리오 \d', sec); sc = sorted(set(sc))
    pr = re.findall(r'가능성\(추정\)[^%\n]*?\d+%', sec)
    if not sc: bad.append('5.6에 시나리오가 없음')
    elif len(pr) < len(sc): bad.append(f'5.6 시나리오 {len(sc)}개 중 가능성 % {len(pr)}개')
follow = '## 지난 리포트 이후' in rep
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
print('\n'.join(bad) if bad else f"PREV_CALLS_OK {'후속편' if follow else '첫 리포트'}")
sys.exit(1 if bad else 0)
