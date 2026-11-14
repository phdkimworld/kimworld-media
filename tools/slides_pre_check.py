# 녹음 전에 slides.json과 대본의 짝을 본다(82회차 LAES, 80회차 CBRS 교훈: hero 둘째 줄 시각이 다음 장면보다 늦은 것을
# check_slides가 합성 직전에야 잡아 hero를 고치고 다시 돌림 — 대본·슬라이드 구조 오류는 시각표 없이도 잡힌다).
# 사용: python3 slides_pre_check.py <video 폴더>   (narration.txt + slides.json)
#  - 문단 수 = paras 수
#  - 장면 from·요소 at·hero 줄 at·list 항목 at·poll 보기 at이 그 문단 문장 수보다 작다
#  - hero 줄 at이 같은 문단 다음 장면 from보다 늦지 않다
#  - ad 번호 문장에 리포트·홈페이지·고정 댓글·설명란·앱 중 하나(ADTEXT를 녹음 전에)
#  - shop 번호 문장에 '쿠팡'과 '설명란'
import sys, os, re, json
V = sys.argv[1]
paras = [p for p in open(os.path.join(V, 'narration.txt'), encoding='utf-8').read().split('\n\n') if p.strip()]
deck = json.load(open(os.path.join(V, 'slides.json'), encoding='utf-8'))
P = deck['paras']; bad = []
if len(P) != len(paras): bad.append(f'문단 수 {len(paras)} ≠ slides paras {len(P)}')
def ats(s):
    out = [s.get('from', 0)]
    for k in ('at', 'sub_at', 'foot_at'):
        if isinstance(s.get(k), (int, float)): out.append(s[k])
    for k in ('lines', 'items', 'stats', 'options'):
        for e in s.get(k, []) or []:
            if isinstance(e, dict) and isinstance(e.get('at'), (int, float)): out.append(e['at'])
    for k in ('left', 'right'):
        if isinstance(s.get(k), dict) and isinstance(s[k].get('at'), (int, float)): out.append(s[k]['at'])
    return out
AD = re.compile(r'리포트|홈페이지|고정 댓글|설명란|앱')
for i, (p, sp) in enumerate(zip(paras, P)):
    sen = re.split(r'(?<=[.?!])\s+', p.strip()); n = len(sen); sl = sp.get('slides', [])
    for j, s in enumerate(sl):
        mx = max(ats(s))
        if mx >= n: bad.append(f'p{i+1} 장면{j+1}({s.get("layout")}) 시각 {mx} ≥ 문장 수 {n}')
        if s.get('layout') == 'hero' and j + 1 < len(sl):
            nf = sl[j+1].get('from', 0); late = [l['at'] for l in s.get('lines', []) if l.get('at', 0) > nf]
            if late: bad.append(f'p{i+1} hero 줄 시각 {late}이 다음 장면 from {nf}보다 늦음(80회차 CBRS)')
    for a in sp.get('ad', []):
        if a >= n: bad.append(f'p{i+1} ad {a} ≥ 문장 수 {n}')
        elif not AD.search(sen[a]): bad.append(f'p{i+1} ad {a}번 문장이 안내 문장이 아님: {sen[a][:40]}')
    for a in sp.get('shop', []):
        if a >= n or not ('쿠팡' in sen[a] and '설명란' in sen[a]): bad.append(f'p{i+1} shop {a}번 문장에 쿠팡·설명란 없음')
print('\n'.join(bad) if bad else f'SLIDES_PRE_OK 문단 {len(P)}')
sys.exit(1 if bad else 0)
