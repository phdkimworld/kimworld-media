# 녹음(raw.wav·raw_timing.json)이 지금 대본(narration.txt)에서 나왔는지 합성 전에 본다.
# 53회차 PLUG 교훈(2026-11-03): TTS를 띄운 뒤 안내 문단을 고쳐 TTS를 끄고 다시 돌렸다. 사람이 놓치면
# 옛 대본 녹음 + 새 slides.json(문장 번호)으로 합성되어 화면과 말이 어긋난다(SKILL V6.3 3번).
# 사용: python3 tts_fresh_check.py <video 폴더>  → TTS_FRESH_OK / TTS_STALE (종료 코드 1)
#  - raw_timing.json의 문단 수·문장 수·문장 글자가 narration.txt와 같아야 한다(st_redo로 고친 문단도 맞아야 함)
import json, os, re, sys
V = sys.argv[1]
nar = os.path.join(V, 'narration.txt'); tm = os.path.join(V, 'raw_timing.json')
if not os.path.exists(tm): print('TTS_STALE raw_timing.json 없음'); sys.exit(1)
paras = [p.strip() for p in open(nar, encoding='utf-8').read().split('\n') if p.strip()]
T = json.load(open(tm, encoding='utf-8'))['paras']
bad = []
if len(paras) != len(T): bad.append(f'문단 수 대본 {len(paras)} / 녹음 {len(T)}')
norm = lambda s: re.sub(r'\s+', '', s)
for i, (p, t) in enumerate(zip(paras, T)):
    sents = [s for s in re.split(r'(?<=[.?!])\s+', p) if s.strip()]
    rec = [s.get('text', '') for s in t.get('sents', [])]
    if len(sents) != len(rec): bad.append(f'문단 {i+1} 문장 수 대본 {len(sents)} / 녹음 {len(rec)}'); continue
    for k, (a, b) in enumerate(zip(sents, rec)):
        if b and norm(a) != norm(b): bad.append(f'문단 {i+1} 문장 {k}: 대본 "{a[:24]}…" ≠ 녹음 "{b[:24]}…"')
print('\n'.join(['TTS_STALE ' + x for x in bad]) if bad else f'TTS_FRESH_OK 문단 {len(paras)}')
sys.exit(1 if bad else 0)
