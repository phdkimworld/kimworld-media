# TTS 녹음의 숨 들이쉬는 소리(문장 사이 저에너지 구간)를 무음으로 바꾼다 — 길이·문장 시각은 그대로.
# 근거: 2026-11-16 시청자 댓글 "코 들이마시는 소리 듣기 싫다"(BTQ atbo6XnK2Tw, review/pending_feedback.md F7).
#   btq5 raw.wav: 문장 사이 쉼 안쪽에 0.2~0.4초짜리 120~2000Hz 잡음(말소리 p95 대비 약 -40dB)이 깔림 → 합성의
#   loudnorm(-16 LUFS)이 키워 들숨처럼 들림. 말 앞머리 자음(ㄱ 파열 등)은 -25dB 이상이라 말소리 쪽으로 남는다.
# 사용: python3 debreath.py raw.wav [raw_timing.json]          → 제자리 처리 + 검사 (DEBREATH_OK / DEBREATH_FAIL)
#       python3 debreath.py --check raw.wav [raw_timing.json]  → 검사만(처리 안 함)
# 방법: 10ms 프레임의 100~4000Hz 에너지로 말소리를 찾고(앞 40ms·뒤 80ms 여유), 0.15초 이상 말 없는 구간을
#   10ms 페이드로 0으로 만든다. 샘플 수는 바꾸지 않으므로 raw_timing.json·슬라이드 동기는 그대로.
# 검사: 문장 경계(raw_timing 문장 시작)마다 그 쉼 안쪽의 30ms 최대 에너지가 말소리 p95 대비 -45dB를 넘으면 '잔여 숨'.
#   잔여 숨 경계가 10% 넘으면 FAIL(종료 코드 1). 여러 번 돌려도 결과가 같다(이미 0인 구간은 그대로).
import sys, json, wave
import numpy as np

SR_HOP = 0.01; SPEECH_DB = -32.0; PRE, POST = 4, 8; MIN_GAP = 15; FADE = 0.01; RESID_DB = -45.0; FAIL_FRAC = 0.10

def read(p):
    w = wave.open(p); sr = w.getframerate(); ch = w.getnchannels(); sw = w.getsampwidth()
    assert sw == 2, '16비트 PCM만'
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch)
    return a, sr

def band_env(x, sr):
    hop = int(sr * SR_HOP); n = len(x) // hop
    fr = x[:n * hop].astype(np.float32).reshape(n, hop)
    X = np.abs(np.fft.rfft(fr * np.hanning(hop), axis=1)) ** 2; f = np.fft.rfftfreq(hop, 1 / sr)
    e = np.sqrt(X[:, (f >= 100) & (f <= 4000)].sum(1) / hop)
    return e, hop

def speech_mask(e):
    ref = np.percentile(e, 95)
    sp = e > ref * 10 ** (SPEECH_DB / 20)
    d = sp.copy()
    for k in range(1, PRE + 1): d[:-k] |= sp[k:]
    for k in range(1, POST + 1): d[k:] |= sp[:-k]
    return d, ref

def runs(mask):
    out = []; i = 0; n = len(mask)
    while i < n:
        if not mask[i]:
            j = i
            while j < n and not mask[j]: j += 1
            out.append((i, j)); i = j
        else: i += 1
    return out

def gate(a, sr):
    mono = a.mean(1)
    e, hop = band_env(mono, sr); sp, ref = speech_mask(e)
    g = np.ones(len(a), np.float32); nf = int(sr * FADE); fade = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, nf))
    cnt = 0; sec = 0.0
    for i, j in runs(sp):
        if j - i < MIN_GAP: continue
        s0, s1 = i * hop, min(j * hop, len(a)) if j < len(e) else len(a)
        if s1 - s0 < 2 * nf: continue
        g[s0:s1] = 0.0
        if i > 0: g[s0:s0 + nf] = fade[::-1]        # 앞 말소리 꼬리에서 0으로
        if j < len(e): g[s1 - nf:s1] = fade         # 0에서 다음 말 앞머리로
        cnt += 1; sec += (s1 - s0) / sr
    y = np.round(a.astype(np.float32) * g[:, None]).astype(np.int16)
    return y, cnt, sec

def boundaries(tp):
    try: d = json.load(open(tp, encoding='utf-8'))
    except Exception: return []
    return [s['start'] for p in d.get('paras', []) for s in p.get('sents', []) if s['start'] > 0.5]

def check(a, sr, bs):
    mono = a.mean(1); e, hop = band_env(mono, sr); sp, ref = speech_mask(e)
    rs = runs(sp); bad = []; seen = 0
    for b in bs:
        k = int(b / SR_HOP)
        r = next(((i, j) for i, j in rs if i - 40 <= k <= j + 40 and j - i >= MIN_GAP), None)
        if r is None: continue
        seen += 1; i, j = r
        w3 = np.convolve(e[i:j] ** 2, np.ones(3) / 3, 'valid') ** 0.5   # 쉼 안쪽만, 30ms 창
        lvl = 20 * np.log10(w3.max() / ref + 1e-12)
        if lvl > RESID_DB: bad.append((b, round(lvl, 1)))
    return seen, bad, ref

def main():
    args = [x for x in sys.argv[1:] if not x.startswith('--')]; only = '--check' in sys.argv
    wav = args[0]; tp = args[1] if len(args) > 1 else wav.rsplit('.', 1)[0] + '_timing.json'
    a, sr = read(wav); n0 = len(a)
    if not only:
        y, cnt, sec = gate(a, sr); assert len(y) == n0
        with wave.open(wav, 'wb') as w:
            w.setnchannels(a.shape[1]); w.setsampwidth(2); w.setframerate(sr); w.writeframes(y.tobytes())
        print(f'debreath: 쉼 {cnt}곳 {sec:.1f}초 무음 처리, 길이 그대로 {n0 / sr:.3f}초')
        a = y
    seen, bad, ref = check(a, sr, boundaries(tp))
    frac = len(bad) / seen if seen else 0
    tag = 'DEBREATH_FAIL' if frac > FAIL_FRAC else 'DEBREATH_OK'
    print(f'{tag} 문장 경계 {seen}곳 중 잔여 숨(>{RESID_DB:.0f}dB) {len(bad)}곳 ({frac:.0%})' + (f' 예: {bad[:5]}' if bad else ''))
    sys.exit(1 if tag == 'DEBREATH_FAIL' else 0)

if __name__ == '__main__': main()
