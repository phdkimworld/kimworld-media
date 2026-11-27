# 테이스트 검사(skill/runbooks/taste.md 11절, 운영자 2026-11-21 "테이스트 적용").
# 디자인의 'AI가 만든 티'(같은 틀 반복·한 화면 글자 과다·이모지·회차마다 같은 쇼츠 순서)를 잡는다.
# 사용: python3 tools/taste_check.py <video 폴더> [...]   (같은 회차의 ../shorts/shorts.json, ../cards/cards.json도 읽음)
#  - TASTE_EMOJI (실패): slides·shorts·cards 화면 글자에 이모지
#  - TASTE_RUN   (경고): 롱폼 같은 레이아웃·anim 틀 5장 연속 / 쇼츠 같은 틀 3장면 연속
#  - TASTE_DENSE (경고): 정지 장면 화면 글자 80자 초과(source·outro·poll 제외)
#  - TASTE_COPY  (경고, 11-27 unslop Copy·im-not-ai): 화면 글자에 느낌표, ai_tells.py 'AI 티' 어휘
#  - TASTE_SAME  (경고): 쇼츠 장면 틀 순서가 다른 회차 둘 이상과 같음(/home/claude/*/shorts/shorts.json 읽기만)
# 종료 코드: 실패 1, 경고만 0. 기준: 2026-11-21 최근 33회차(이모지 0, 80자 초과는 거의 source 장면).
import sys, os, re, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_tells import STOCK2  # 11-27 taste.md 13절
EMO = re.compile('[\U0001F300-\U0001FAFF\U0001F000-\U0001F2FF☀-➿⭐⭕⬛⬜️]')
NOTXT = {'bg', 'sfx', 'tone', 'layout', 'tpl', 'hi', 'dir', 'from', 'at', 'sub_at', 'foot_at', 'beats', 'ad', 'shop',
         'next', 'num_color', 'color', 'file', 'path', 'kind', 'group', 'unit', 'decimals', 'log', 'midroll', 'midroll_app', 'em'}
def texts(o, skip=NOTXT):
    if isinstance(o, str): yield o
    elif isinstance(o, dict):
        for k, v in o.items():
            if k not in skip: yield from texts(v, skip)
    elif isinstance(o, list):
        for v in o: yield from texts(v, skip)
def runs(seq, n):
    out, i = [], 0
    while i < len(seq):
        j = i
        while j + 1 < len(seq) and seq[j + 1] == seq[i]: j += 1
        if j - i + 1 >= n: out.append((i, j - i + 1, seq[i]))
        i = j + 1
    return out
def shorts_seq(path):
    sj = json.load(open(path, encoding='utf-8'))
    return [(sc.get('anim') or {}).get('tpl', 'els') for sc in sj.get('scenes', [])]
fails, warns = [], []
for V in sys.argv[1:]:
    V = os.path.abspath(V); ep = os.path.basename(os.path.dirname(V))
    f = os.path.join(V, 'slides.json')
    if os.path.exists(f):
        deck = json.load(open(f, encoding='utf-8')); seq, pos = [], []
        for i, p in enumerate(deck.get('paras', [])):
            for j, x in enumerate(p.get('slides', [])):
                seq.append((x.get('anim') or {}).get('tpl') or x.get('layout') or '?'); pos.append(f'p{i+1}s{j+1}')
                t = ''.join(texts(x))
                e = EMO.findall(t)
                if e: fails.append(f'{ep} TASTE_EMOJI 슬라이드 p{i+1}s{j+1} 이모지 {"".join(e)} (V6.4 금지)')
                if 'anim' not in x and x.get('layout') not in ('source', 'outro', 'poll'):
                    n = len(re.sub(r'\s|\*', '', t))
                    if n > 80: warns.append(f'{ep} TASTE_DENSE p{i+1}s{j+1} {x.get("layout")} 화면 글자 {n}자 > 80 — 대본 문장을 옮겨 적지 말고 숫자·이름만')
        for s, n, v in runs(seq, 5):
            warns.append(f'{ep} TASTE_RUN 롱폼 {pos[s]}부터 {v} {n}장 연속 — 문장이 보여 주는 것(흐름·맞대기·기록·질문)에 맞춰 틀을 섞기')
    sh = os.path.join(os.path.dirname(V), 'shorts', 'shorts.json')
    if os.path.exists(sh):
        sj = json.load(open(sh, encoding='utf-8'))
        for k, sc in enumerate(sj.get('scenes', [])):
            e = EMO.findall(''.join(texts(sc)))
            if e: fails.append(f'{ep} TASTE_EMOJI 쇼츠 장면 {k+1} 이모지 {"".join(e)}')
        sq = shorts_seq(sh)
        for s, n, v in runs(sq, 3):
            if v != 'els': warns.append(f'{ep} TASTE_RUN 쇼츠 장면 {s+1}부터 {v} {n}번 연속')
        same = []
        for o in glob.glob('/home/claude/*/shorts/shorts.json'):
            if os.path.abspath(o) == os.path.abspath(sh): continue
            try:
                if shorts_seq(o) == sq: same.append(o.split('/')[3])
            except Exception: pass
        if len(same) >= 2 and any(t != 'els' for t in sq):
            warns.append(f'{ep} TASTE_SAME 쇼츠 장면 순서 {"→".join(sq)} 가 다른 회차 {len(same)}편({", ".join(sorted(same)[:6])})과 같음 — 이 회차 이야기 순서로 한 장면 이상 바꾸기')
    cf = os.path.join(os.path.dirname(V), 'cards', 'cards.json')
    if os.path.exists(cf):
        cj = json.load(open(cf, encoding='utf-8')); cards = cj.get('cards', []) if isinstance(cj, dict) else cj
        for k, c in enumerate(cards):
            e = EMO.findall(''.join(texts(c)))
            if e: fails.append(f'{ep} TASTE_EMOJI 카드 {k+1} 이모지 {"".join(e)}')
def copy_warn(ep, where, t):
    if '!' in t or '！' in t: warns.append(f'{ep} TASTE_COPY {where} 화면 글자 느낌표 — 평서 문구로(unslop Copy)')
    for rx, why in STOCK2:
        m = re.search(rx, t)
        if m: warns.append(f"{ep} TASTE_COPY {where} '{m.group(0)}' — {why}")
for V in sys.argv[1:]:
    V = os.path.abspath(V); ep = os.path.basename(os.path.dirname(V))
    f = os.path.join(V, 'slides.json')
    if os.path.exists(f):
        for i, p in enumerate(json.load(open(f, encoding='utf-8')).get('paras', [])):
            for j, x in enumerate(p.get('slides', [])): copy_warn(ep, f'슬라이드 p{i+1}s{j+1}', ''.join(texts(x)))
    sh = os.path.join(os.path.dirname(V), 'shorts', 'shorts.json')
    if os.path.exists(sh):
        for k, sc in enumerate(json.load(open(sh, encoding='utf-8')).get('scenes', [])): copy_warn(ep, f'쇼츠 장면 {k+1}', ''.join(texts(sc)))
for m in fails: print('FAIL', m)
for m in warns: print('WARN', m)
print('TASTE_FAIL' if fails else ('TASTE_OK (경고 %d)' % len(warns)))
sys.exit(1 if fails else 0)
