# 합성 전에 '정지 화면' 위험을 찾는다(2026-10-21 INFQ 교훈: stat→stat이 이어지면 화면 변화로 안 잡혀 video_check가 정지 25초·18초로 실패, 합성 세 번).
# 사용: python3 still_check.py <작업 폴더(video)>  — slides.json과 raw_timing.json을 읽는다
#  - 정적 화면(stat·quote·compare) 하나가 15초를 넘거나, 같은 layout(stat·quote) 화면이 이어져 합이 17초를 넘으면 알려 주고 종료 코드 1
#    (INFQ 실패 사례: stat 12.7초+12초=25초, stat 8.5초+9.5초=18초. 목록·타임라인·hero는 항목이 문장마다 나타나 제외)
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
        segs.append((pi, f, s.get('layout'), t0, t1))
bad = []
for i, (pi, f, lay, t0, t1) in enumerate(segs):
    if lay not in ('stat', 'quote', 'compare'):
        continue
    if t1 - t0 > 15:
        bad.append(f'p{pi} s{f} {lay} 혼자 {t1 - t0:.1f}초')
    if i + 1 < len(segs) and segs[i + 1][2] == lay and lay in ('stat', 'quote') and segs[i + 1][0] == pi:
        tot = segs[i + 1][4] - t0
        if tot > 17:
            bad.append(f'p{pi} s{f}→s{segs[i + 1][1]} {lay}→{lay} 합 {tot:.1f}초')
print('\n'.join(bad) if bad else 'STILL_OK')
sys.exit(1 if bad else 0)
