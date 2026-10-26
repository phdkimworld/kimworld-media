# 고친 문단만 다시 녹음해 raw.wav·시각표를 다시 만든다(2026-10-26 BTBT 35회차: 녹음 중 대본 한 문장을 고쳐야 했음).
# 사용: python3 st_redo.py 나레이션.txt 출력.wav <st_tts 임시 폴더> 문단번호(1부터, 쉼표) [화자=6] [속도=1.15] [스텝=10]
import sys, subprocess, wave, json, os, importlib.util
src, dst, tmp, redo = sys.argv[1], sys.argv[2], sys.argv[3], [int(x) - 1 for x in sys.argv[4].split(',')]
sid, speed, steps = (sys.argv[5:] + ['6', '1.15', '10'][len(sys.argv[5:]):])[:3]
import numpy as np, re
paras = [p.strip() for p in open(src, encoding='utf-8').read().split('\n') if p.strip()]
split = lambda p: [s for s in re.split(r'(?<=[.?!])\s+', p) if s.strip()]
code = open('/home/claude/tts/st/st_tts.py', encoding='utf-8').read()
ns = {'np': np, 're': re}; exec(code[code.index('def gaps_of'):code.index('sr = None')], ns)
for i in redo:
    subprocess.run(['/home/claude/tts/st/st.sh', sid, paras[i], f'{tmp}/p{i}.wav', speed, steps], capture_output=True)
    print('redo', i + 1, flush=True)
GAP = 0.6; out = []; t = 0.0; timing = []
for i, p in enumerate(paras):
    w = wave.open(f'{tmp}/p{i}.wav'); sr = w.getframerate()
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16)
    sents = split(p); b = ns['align'](sents, a, sr)
    timing.append({"start": round(t, 3), "end": round(t + len(a) / sr, 3),
                   "sents": [{"start": round(t + b[k], 3), "end": round(t + b[k + 1], 3), "text": s} for k, s in enumerate(sents)]})
    out += [a, np.zeros(int(sr * GAP), np.int16)]; t += len(a) / sr + GAP
with wave.open(dst, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(np.concatenate(out).tobytes())
json.dump({"duration": round(t, 3), "paras": timing}, open(os.path.splitext(dst)[0] + '_timing.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('done', dst)
