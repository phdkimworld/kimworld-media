# 합성 전에 '정지 화면' 위험을 찾는다(2026-10-21 INFQ 교훈: stat→stat이 이어지면 화면 변화로 안 잡혀 video_check가 정지 25초·18초로 실패, 합성 세 번).
# 사용: python3 still_check.py <작업 폴더(video)>  — slides.json과 raw_timing.json을 읽는다
#  - 정적 화면(stat·quote·compare) 하나가 15초를 넘거나, 같은 layout(stat·quote) 화면이 이어져 합이 17초를 넘으면 알려 주고 종료 코드 1
#    (INFQ 실패 사례: stat 12.7초+12초=25초, stat 8.5초+9.5초=18초. 목록·타임라인·hero는 항목이 문장마다 나타나 제외)
#  - compare→compare 도 화면 변화로 안 잡힌다(2026-10-24 LAES 32회차: compare 6.4초+9.7초=16초로 video_check 실패). 합 15초 넘으면 알린다
#  - 항목이 하나뿐인 timeline이 이어져도 화면 변화로 안 잡힌다(2026-10-25 BTBT 35회차: 일정 문단 tl×3 = 17초로 video_check 실패). 연속 합 16.5초 넘으면 알린다(LAES 32의 16.2초는 통과)
#  - 항목이 한꺼번에 뜨는(at가 모두 같은) timeline이 문단 경계를 넘어 이어져도 화면 변화로 안 잡힌다(2026-10-26 OKLO 36회차: 목표가 tl 2항목 → 다음 문단 tl 2항목 = 15.3초로 video_check 실패). 문단을 넘는 연속 합 15초 넘으면 알린다
import json, os, sys
V = sys.argv[1] if len(sys.argv) > 1 else '.'
deck = json.load(open(os.path.join(V, 'slides.json'))); tm = json.load(open(os.path.join(V, 'raw_timing.json')))
P = tm['paras']; segs = []
for pi, (p, t) in enumerate(zip(deck['paras'], P)):
    sents = t['sents']; sl = p['slides']
    for k, s in enumerate(sl):
        f = s.get('from', s.get('at', 0)); nf = sl[k + 1].get('from', sl[k + 1].get('at', 0)) if k + 1 < len(sl) else None
        t0 = sents[min(f, len(sents) - 1)]['start']
        t1 = sents[nf]['start'] if nf is not None and nf < len(sents) else t['end']
        lay = s.get('layout')
        static_tl = lay == 'timeline' and len({it.get('at') for it in s.get('items', [])}) <= 1
        if lay == 'timeline' and len(s.get('items', [])) <= 1: lay = 'timeline1'
        segs.append((pi, f, lay, t0, t1, static_tl))
bad = []
for i in range(len(segs) - 1):
    a, b = segs[i], segs[i + 1]
    if a[5] and b[5] and b[0] != a[0] and b[4] - a[3] > 15:
        bad.append(f'p{a[0]} s{a[1]}→p{b[0]} s{b[1]} 문단을 넘는 정적 timeline 연속 합 {b[4] - a[3]:.1f}초')
segs = [x[:5] for x in segs]
i = 0
while i < len(segs):
    j = i
    while j + 1 < len(segs) and segs[j + 1][2] == 'timeline1' and segs[i][2] == 'timeline1' and segs[j + 1][0] == segs[i][0]: j += 1
    if j > i and segs[j][4] - segs[i][3] > 16.5:  # LAES 32 p21 16.2초는 video_check 통과
        bad.append(f'p{segs[i][0]} s{segs[i][1]}→s{segs[j][1]} 한 항목 timeline 연속 {j - i + 1}개 합 {segs[j][4] - segs[i][3]:.1f}초')
    i = j + 1
for i, (pi, f, lay, t0, t1) in enumerate(segs):
    if lay not in ('stat', 'quote', 'compare', 'source'):  # source도 한꺼번에 뜨는 정지 화면(2026-10-29 IREN 45회차: source 15.7초, video_check에서야 걸림)
        continue
    if t1 - t0 > 15:
        bad.append(f'p{pi} s{f} {lay} 혼자 {t1 - t0:.1f}초')
    if i + 1 < len(segs) and segs[i + 1][2] == lay and segs[i + 1][0] == pi:
        tot = segs[i + 1][4] - t0
        if tot > (15 if lay == 'compare' else 17):
            bad.append(f'p{pi} s{f}→s{segs[i + 1][1]} {lay}→{lay} 합 {tot:.1f}초')
print('\n'.join(bad) if bad else 'STILL_OK')
sys.exit(1 if bad else 0)
