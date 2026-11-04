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
    # 47·48회차(LEU·TNXP): 첫 장면 요소가 둘(0·0.3)뿐이면 6초 넘는 첫 문장에서 뒤 70%가 정지(4.8·5.0초) → 0.6~0.7 지점에 하나 더
    if len(ats) < 3: bad.append(f'장면 1 요소 {len(ats)}개: 0.6~0.7 지점에 도장 하나를 더(첫 문장 뒤쪽 정지 방지)')
    if len(ats) > 1 and ats[1] > 0.3: bad.append(f'장면 1 둘째 요소 at {ats[1]}: 0.3 이하(첫 문장이 6초를 넘으면 3초 정지)')
# 통합 제작·검수 지침(2026-10-29) 4장
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tts_asr_check import script_nums, val
spec = json.load(open(os.path.join(d, 'shorts.json'), encoding='utf-8'))
for i, (s, sc) in enumerate(zip(sents, scenes)):
    # 4.1 화면 자막은 아라비아 숫자(subtitle), 음성은 한글 독음(narration) — 두 칸을 나눈다
    sub = sc.get('subtitle')
    if not sub: bad.append(f'장면 {i+1} "subtitle"(화면 자막, 아라비아 숫자·기호) 칸이 없음 — 4.1 tts_script/subtitle_text 이원화'); continue
    ls = sub.split('\n')
    if len(ls) > 2 or any(len(x.replace('**', '')) > 20 for x in ls): bad.append(f'장면 {i+1} 자막은 1문장 1프레임 — \\n으로 2줄 이하·줄당 20자 이하(4.1): {sub[:30]}')
    if i > 0 and any(e.get('kind') == 'stamp' and 0 < e.get('at', 0) < 0.5 for e in sc.get('els', [])): bad.append(f'장면 {i+1} 스탬프 at < 0.5 — 문장 후반 키워드에서 찍는다(4.4)')
    if re.search(r'퍼센트|(?<![가-힣])점 [영일이삼사오육칠팔구]|센트', sub): bad.append(f'장면 {i+1} 자막에 한글 독음: {sub[:30]}')
    if script_nums(s) and not re.search(r'\d', sub): bad.append(f'장면 {i+1} 음성에 숫자가 있는데 자막에 아라비아 숫자가 없음: {sub[:30]}')
    # 4.2 상단 카드의 큰 숫자(가장 큰 num)는 그 장면 내레이션에서 말한다
    nums = [e for e in sc.get('els', []) if e.get('kind') == 'num' and re.search(r'\d', str(e.get('text', '')))]
    if nums:
        main = max(nums, key=lambda e: e.get('size', 160))
        m = re.search(r'\d[\d,.]*(?:\s*[만억조천](?:\s*\d[\d,.]*)?)*', str(main['text'])); v = val(m.group(0).replace(',', ''))
        said = [x for x, _ in script_nums(s)]
        if v and not any(abs(x - v) <= 0.03 * v for x in said): bad.append(f"장면 {i+1} 큰 숫자 '{main['text']}'를 내레이션에서 말하지 않음(4.2 시각·청각 일치): {s[:30]}")
# v2.8 4.2(운영자 11-02 LAES 쇼츠): 위쪽 흰 소제목(text)과 노란 배지(stamp)를 같은 높이에 겹쳐 띄우지 않는다(Echo·레이어 충돌)
for i, sc in enumerate(scenes):
    els = [e for e in sc.get('els', []) if e.get('kind') not in ('poll', 'chart')]
    for a in range(len(els)):
        for b in range(a + 1, len(els)):
            ya, yb = els[a].get('y', 0), els[b].get('y', 0)
            if abs(ya - yb) < 100 and {els[a].get('kind'), els[b].get('kind')} & {'stamp'}:
                bad.append(f"장면 {i+1} '{els[a].get('text','')}'(y {ya})와 '{els[b].get('text','')}'(y {yb})가 같은 높이 — 위 소제목과 배지를 겹치지 않게(v2.8 4.2)")
# v2.9(운영자 11-02 LAES 쇼츠): 장면당 스탬프 1개(첫 장면만 업종 배지 + 핵심 스탬프 2개), 스탬프 14자 이내, 질문 자막에 '몇 번' 스탬프 중복 금지
for i, (s, sc) in enumerate(zip(sents, scenes)):
    st = [e for e in sc.get('els', []) if e.get('kind') == 'stamp']
    lim = 2 if i == 0 else 1
    if len(st) > lim: bad.append(f"장면 {i+1} 스탬프 {len(st)}개 > {lim}(v2.9 1장면 1스탬프{', 첫 장면은 배지+스탬프' if i == 0 else ''})")
    for e in st:
        if len(e.get('text', '')) > 14: bad.append(f"장면 {i+1} 스탬프 '{e['text']}' {len(e['text'])}자 > 14(오른쪽 끝 잘림, v2.9)")
        if '몇 번' in e.get('text', '') and '몇 번' in sc.get('subtitle', ''): bad.append(f"장면 {i+1} 스탬프 '{e['text']}'가 질문 자막과 중복 → '상장 이후 전수 조사' 같은 보충 사실(v2.9)")
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
# v2.5(2026-11-02 운영자 TNXP 쇼츠 검토): 위 카드·스탬프와 아래 자막의 같은 문구 반복, 첫 장면 배지와 첫 문장 불일치, 첫 문장 법인 접미사
import difflib
_n = lambda t: re.sub(r'[\s*()·,]|약|은|는', '', str(t or ''))
for i, (s, sc) in enumerate(zip(sents, scenes)):
    sub = sc.get('subtitle') or ''; sn = _n(sub.replace('\n', ''))
    for e in sc.get('els', []):
        t = e.get('text')
        if not t or e.get('kind') not in ('num', 'stamp', 'text'): continue
        if e.get('kind') == 'stamp' and re.search(r'\d', t) and _n(t) and (_n(t) in sn or difflib.SequenceMatcher(None, _n(t), sn).find_longest_match(0, len(_n(t)), 0, len(sn)).size >= max(5, len(_n(t)) - 1)):
            bad.append(f"장면 {i+1} 스탬프 '{t}'가 아래 자막과 같은 문구(v2.5 반복) → 보충 사실로 바꾸거나 자막을 말하는 문장으로")
    lab = [e.get('text') for e in sc.get('els', []) if e.get('kind') == 'text' and e.get('text')]
    num = [e.get('text') for e in sc.get('els', []) if e.get('kind') == 'num' and e.get('text')]
    l1 = _n(sub.split('\n')[0])
    if num and _n(num[0]) in sn and not any(re.search(r'([다요]|\?)[.!]?$', x.strip()) for x in sub.split('\n')):
        bad.append(f"장면 {i+1} 위 카드 숫자 '{num[0]}'와 명사구 자막 '{sub.replace(chr(10), ' / ')}'가 같은 명사구(v2.5) → 자막은 말하는 문장(아라비아 숫자)으로")
if sents and scenes:
    said = [x for x, _ in script_nums(sents[0])]
    for e in scenes[0].get('els', []):
        m = re.search(r'(\d[\d,.]*)\s*(배|%|번|만|억)', str(e.get('text') or ''))
        if m and '$' not in str(e.get('text')):
            v = val(m.group(1).replace(',', ''))
            if v and not any(abs(abs(x) - v) <= 0.03 * v for x in said): bad.append(f"장면 1 배지 '{e.get('text')}'가 첫 문장에 없음(v2.5 시각·청각 일치) → 첫 문장과 맞는 배지로")
    m = re.search(r'파마슈티컬스|홀딩스|코퍼레이션|테크놀로지스|인더스트리스|바이오사이언스|커뮤니케이션스', sents[0])
    if m: bad.append(f"첫 문장 법인 접미사 '{m.group(0)}'(빠른 첫 호흡에서 뭉개짐, v2.5) → '미국 제약사 토닉스는'처럼 업종 + 짧은 이름")
# 쇼츠 v3.1(운영자 11-04 MRVL 쇼츠 검수)
for i, sc in enumerate(scenes):
    els = sc.get('els', []); sub = sc.get('subtitle') or ''
    # 1) 괴리율·할인율을 일간 하락처럼 빨간 '-12.1%'로 쓰지 않는다
    if re.search(r'가치보다|할인|괴리|환산', sub):
        for e in els:
            t = str(e.get('text') or '')
            if e.get('kind') in ('num', 'text') and re.match(r'^-\d', t):
                bad.append(f"장면 {i+1} 괴리율 '{t}'를 하락률처럼 표기 → 큰 숫자 '12.1% 낮음'(노란색), 위 라벨 '합병 가치 대비 괴리율'")
        tops = [str(e.get('text') or '') for e in els if e.get('kind') == 'text' and (e.get('y') or 999) < 200]
        if tops and not any(re.search(r'합병 가치 대비|환산가 대비|괴리율', t) for t in tops):
            bad.append(f"장면 {i+1} 괴리율 장면 위 라벨에 '합병 가치 대비'·'합병 환산가 대비' 명시(종가 라벨 금지): {tops[0]}")
    # 2) 위 라벨을 장면 중간에 무음으로 바꾸지 않는다(until 뒤 같은 자리 새 글자)
    top = [e for e in els if e.get('kind') == 'text' and (e.get('y') or 999) < 200]
    if any(e.get('until') is not None for e in top) and len(top) > 1:
        bad.append(f"장면 {i+1} 위 라벨 교체('{top[0].get('text')}' → '{top[-1].get('text')}') 깜빡임 → 장면 내내 한 라벨로")
    # 3) 자막 마지막 줄은 완결된 말하는 문장
    last = re.sub(r'\*\*', '', sub.split('\n')[-1]).strip()
    if last and not re.search(r'([다요]|\?)[.!]?$', last):
        bad.append(f"장면 {i+1} 자막 끝 '{last}'가 숫자·명사로 끝남 → '31.7% 내렸습니다'처럼 서술문")
print('\n'.join(bad) if bad else f'SHORTS_OK 문장·장면 {len(sents)}개')
sys.exit(1 if bad else 0)
