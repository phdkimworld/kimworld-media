# 쇼츠 TTS 전에 문장 수와 장면 수가 같은지 본다(2026-10-25 SMR 34회차: 한 문단에 두 문장을 써서 렌더에서야 '문장 10 / 장면 9'로 실패, TTS를 다시 돌림).
# 사용: python3 shorts_check.py <쇼츠 폴더>   (narration.txt, shorts.json)
# 2026-10-29 통합 제작·검수 지침 4장: 자막 subtitle 이원화·큰 숫자 말하기·끝 쉼표·CTA 투표+관련 영상만·'몇 번' 답
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
    if em and em not in (sc.get('subtitle') or s): bad.append(f'장면 {i+1} em "{em}"이 문장에 없음: {s[:30]}…')
# 투표 보기 길이(2026-10-26 OKLO 36회차: '남아 있는 10억 달러' 12자로 make_shorts가 렌더 단계에서 실패)
for i, sc in enumerate(scenes):
    for e in sc.get('els', []):
        if e.get('kind') == 'poll':
            o = e.get('opts', [])
            if not 2 <= len(o) <= 4 or any(len(x) > 10 or len(x.encode()) > 25 for x in o): bad.append(f'장면 {i+1} 투표 보기는 2~4개·각 10자·25바이트 이하(Threads 제한): {o}')
# 첫 장면: 큰 숫자는 0초, 다음 요소는 0.3 이하(2026-10-26 앤트로픽 40회차: 6.8초 첫 문장에서 도장 0.45 → 3.25초 정지로 video_check 실패, 재렌더)
if scenes:
    ats = sorted(e.get('at', 0) for e in scenes[0].get('els', []) if e.get('kind') != 'poll')
    if ats and ats[0] > 0: bad.append(f'장면 1 첫 요소 at {ats[0]}: 큰 숫자는 at 0(썸네일 숫자)')
    if len(ats) > 1 and ats[1] > 0.3: bad.append(f'장면 1 둘째 요소 at {ats[1]}: 0.3 이하(첫 문장이 6초를 넘으면 3초 정지)')
# 통합 제작·검수 지침(2026-10-29) 4장
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tts_asr_check import script_nums, val
spec = json.load(open(os.path.join(d, 'shorts.json'), encoding='utf-8'))
for i, (s, sc) in enumerate(zip(sents, scenes)):
    # 4.1 화면 자막은 아라비아 숫자(subtitle), 음성은 한글 독음(narration) — 두 칸을 나눈다
    sub = sc.get('subtitle')
    if not sub: bad.append(f'장면 {i+1} "subtitle"(화면 자막, 아라비아 숫자·기호) 칸이 없음 — 4.1 tts_script/subtitle_text 이원화'); continue
    if re.search(r'퍼센트|(?<![가-힣])점 [영일이삼사오육칠팔구]|센트', sub): bad.append(f'장면 {i+1} 자막에 한글 독음: {sub[:30]}')
    if script_nums(s) and not re.search(r'\d', sub): bad.append(f'장면 {i+1} 음성에 숫자가 있는데 자막에 아라비아 숫자가 없음: {sub[:30]}')
    # 4.2 상단 카드의 큰 숫자(가장 큰 num)는 그 장면 내레이션에서 말한다
    nums = [e for e in sc.get('els', []) if e.get('kind') == 'num' and re.search(r'\d', str(e.get('text', '')))]
    if nums:
        main = max(nums, key=lambda e: e.get('size', 160))
        m = re.search(r'\d[\d,.]*(?:\s*[만억조천](?:\s*\d[\d,.]*)?)*', str(main['text'])); v = val(m.group(0).replace(',', ''))
        said = [x for x, _ in script_nums(s)]
        if v and not any(abs(x - v) <= 0.03 * v for x in said): bad.append(f"장면 {i+1} 큰 숫자 '{main['text']}'를 내레이션에서 말하지 않음(4.2 시각·청각 일치): {s[:30]}")
# 4.3 마지막 문장이 쉼표로 끊기지 않게(끝음절 잘림) — '…바로 이 숫자입니다.' 또는 '…바로...'
if sents and sents[-1].rstrip().endswith(','): bad.append(f'마지막 문장이 쉼표로 끝남(4.3 끝음절 잘림): {sents[-1][-20:]}')
# 4.4 엔딩 CTA는 댓글 투표 + 관련 영상(풀영상) 둘만. 리포트·사이트 검색은 롱폼과 고정 댓글 몫
cta = spec.get('cta', '')
if re.search(r'사이트|검색|리포트|drkimworld|고정 댓글', cta): bad.append(f'CTA "{cta}"에 리포트·사이트 안내 — 4.4 쇼츠 끝은 투표 + ▶ 관련 영상만')
for s in sents[-3:]:
    if re.search(r'리포트|홈페이지|사이트|검색', s): bad.append(f'끝 세 문장에 리포트·사이트 안내(4.4): {s[:30]}')
# 3.4·4.4 '몇 번?'을 물었으면 쇼츠 안에서 답(N번 중 M번)
for i, s in enumerate(sents):
    if re.search(r'몇 번', s) and not re.search(r'[가-힣]+ 번 (중|가운데)|번 (중|가운데) [가-힣]+ 번|[가-힣]+ 번 모두', ' '.join(sents[i + 1:i + 3])):
        bad.append(f'문장 {i+1} "몇 번"을 묻고 다음 두 문장 안에 답(N번 중 M번)이 없음')
print('\n'.join(bad) if bad else f'SHORTS_OK 문장·장면 {len(sents)}개')
sys.exit(1 if bad else 0)
