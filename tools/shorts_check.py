# 쇼츠 TTS 전에 문장 수와 장면 수가 같은지 본다(2026-10-25 SMR 34회차: 한 문단에 두 문장을 써서 렌더에서야 '문장 10 / 장면 9'로 실패, TTS를 다시 돌림).
# 사용: python3 shorts_check.py <쇼츠 폴더>   (narration.txt, shorts.json)
import sys, json, re, os
d = sys.argv[1]
paras = [p.strip() for p in open(os.path.join(d, 'narration.txt'), encoding='utf-8').read().split('\n') if p.strip()]
sents = [s for p in paras for s in re.split(r'(?<=[.?!])\s+', p) if s.strip()]
scenes = json.load(open(os.path.join(d, 'shorts.json'), encoding='utf-8'))['scenes']
bad = []
if len(sents) != len(scenes): bad.append(f'문장 {len(sents)} / 장면 {len(scenes)} 수가 다르다(한 줄 = 한 문장 = 한 장면)')
for i, p in enumerate(paras):
    n = len([s for s in re.split(r'(?<=[.?!])\s+', p) if s.strip()])
    if n > 1: bad.append(f'줄 {i+1}에 문장 {n}개: {p[:30]}…')
for i, (s, sc) in enumerate(zip(sents, scenes)):
    em = sc.get('em')
    if em and em not in s: bad.append(f'장면 {i+1} em "{em}"이 문장에 없음: {s[:30]}…')
# 투표 보기 길이(2026-10-26 OKLO 36회차: '남아 있는 10억 달러' 12자로 make_shorts가 렌더 단계에서 실패)
for i, sc in enumerate(scenes):
    for e in sc.get('els', []):
        if e.get('kind') == 'poll':
            o = e.get('opts', [])
            if not 2 <= len(o) <= 4 or any(len(x) > 10 for x in o): bad.append(f'장면 {i+1} 투표 보기는 2~4개·각 10자 이하: {o}')
print('\n'.join(bad) if bad else f'SHORTS_OK 문장·장면 {len(sents)}개')
sys.exit(1 if bad else 0)
