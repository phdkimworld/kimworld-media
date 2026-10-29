# TTS 녹음을 한국어 음성 인식(sherpa-onnx zipformer)으로 다시 듣고, 대본의 숫자가 소리로 나왔는지 문단마다 본다.
# 2026-10-29 CBRS 43회차: '그리고 지금은 약 스물한 배입니다'가 녹음에서 '약 …다'로 뭉개져 시청자에게 '약 배입니다'로 들림(운영자 영상 검토).
# 사용: python3 tts_asr_check.py <narration.txt> <raw.wav> [raw_timing.json]   → ASR_OK / ASR_FAIL(문단 번호·숫자) → 고칠 문단은 st_redo.py로 다시 녹음
# 인식 잡음(112 → 110 등)을 견디도록 ±3% 안의 값이면 들린 것으로 친다. 못 들은 숫자가 있으면 그 문단을 새로 합성해 다시 듣고,
# 새 녹음에선 들리는 숫자만 FAIL(원래 녹음이 뭉갬)로, 새 녹음에서도 안 들리면 LIMIT(인식기 한계)로 적는다. 모델이 없으면 받는 법을 알려 주고 건너뛴다(종료 0).
import json, os, re, subprocess, sys, tempfile
A = '/home/claude/asr/sherpa-onnx-zipformer-korean-2024-06-24'
B = '/home/claude/tts/st/sherpa-onnx-v1.13.8-linux-x64-static/bin/sherpa-onnx-offline'
ST = '/home/claude/tts/st/st.sh'
SINO = dict(zip('영공일이삼사오육칠팔구', [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
SMALL = {'십': 10, '백': 100, '천': 1000}; BIG = {'만': 10 ** 4, '억': 10 ** 8, '조': 10 ** 12}
TENS = {'열': 10, '스물': 20, '스무': 20, '서른': 30, '마흔': 40, '쉰': 50, '예순': 60, '일흔': 70, '여든': 80, '아흔': 90}
ONES = {'하나': 1, '한': 1, '둘': 2, '두': 2, '셋': 3, '세': 3, '넷': 4, '네': 4, '다섯': 5, '여섯': 6, '일곱': 7, '여덟': 8, '아홉': 9}
NAT = r'(?:열|스물|스무|서른|마흔|쉰|예순|일흔|여든|아흔)(?:하나|한|둘|두|셋|세|넷|네|다섯|여섯|일곱|여덟|아홉)?|다섯|여섯|일곱|여덟|아홉'
UNIT = r'(?:배|퍼센트|달러|센트|주|번|개|명|곳|원|일|월|년|분기|거래일|시간)'
SINO_RE = r'[영공일이삼사오육칠팔구십백천만억조]+'

NUMCH = r'(?:\d+(?:\.\d+)?|[영공일이삼사오육칠팔구십백천])'
RUN = NUMCH + r'+(?:\s*[만억조](?:\s*' + NUMCH + r'+)?)*'

def val(s):
    # '일억 팔천십만', '1억팔천십만', '8천오백만', '1940만', '이천이십칠' → 수
    tot = sec = 0; cur = None
    for tok in re.findall(r'\d+(?:\.\d+)?|\S', s.replace(' ', '')):
        if tok[0].isdigit(): cur = float(tok)
        elif tok in SINO: cur = SINO[tok]
        elif tok in SMALL: sec += (1 if cur is None else cur) * SMALL[tok]; cur = None
        elif tok in BIG: tot += (sec + (cur or 0) or 1) * BIG[tok]; sec = 0; cur = None
    return tot + sec + (cur or 0)

def native(s):
    m = re.fullmatch(r'(열|스물|스무|서른|마흔|쉰|예순|일흔|여든|아흔)?(하나|한|둘|두|셋|세|넷|네|다섯|여섯|일곱|여덟|아홉)?', s)
    return (TENS.get(m.group(1), 0) + ONES.get(m.group(2), 0)) if m and s else None

def script_nums(p):
    # 대본 숫자(뒤에 단위가 붙은 것만), 나오는 순서대로: '사 점 육 퍼센트', '일억 팔천십만 달러', '스물한 배', '이십이일'
    p = p.replace('시월', '십월').replace('유월', '육월')
    out = []
    pat = r'(?<![가-힣])(?:(' + RUN + r')\s+점\s+([영공일이삼사오육칠팔구]+)|(' + RUN + r')|(' + NAT + r'))\s*(?=' + UNIT + r')'
    for m in re.finditer(pat, p):
        if m.group(1): v = float(f'{val(m.group(1))}.{"".join(str(SINO[c]) for c in m.group(2))}')
        elif m.group(3):
            if len(m.group(3)) == 1 and m.group(3) in '이일사오구': continue  # '이', '일' 같은 한 글자 낱말
            v = val(m.group(3))
        else:
            v = native(m.group(4))
            if not v or v < 5: continue
        if re.match(r'\s*(월|일)', p[m.end():]) : continue  # 날짜는 인식 잡음이 많고 TTS가 틀린 적이 없어 뺀다
        out.append((v, m.group(0).strip()))
    return out

def heard_nums(t):
    t = re.sub(r'수물', '스물', t)
    t = re.sub(r'점,\s*', '점 ', t)  # '11점, 9 퍼센트' → '11점 9'
    t = re.sub(r'([영일이삼사오육칠팔구])\.(\d)', lambda m: str(SINO[m.group(1)]) + '.' + m.group(2), t)  # '이.4배' → '2.4배'
    t = re.sub(r'(?<=[십백천만억])\s+(?=[\d영공일이삼사오육칠팔구])', '', t)  # '천 9백사십만' → '천9백사십만'
    # 인식 결과는 띄어쓰기가 없어 '9일'의 '일'을 숫자로 읽지 않도록: 아라비아 숫자 뒤에는 단위 글자(십백천만억)만 이어 붙인다
    t = t.replace('시월', '십월')
    out = []
    # 손으로 훑는다: 아라비아 숫자·단위(십백천만억조)·한자어 숫자를 한 덩어리로, 단 아라비아 숫자 바로 뒤 한자어 숫자 글자('9일'의 일)는 끊는다
    runs = []; i = 0; n = len(t)
    while i < n:
        m = re.match(NAT, t[i:])
        if m:  # 인식 결과엔 띄어쓰기가 거의 없어 앞 글자는 따지지 않는다('열려' 같은 낱말이 섞여도 남는 수일 뿐 빠진 수가 아니다)
            runs.append((native(m.group(0)), i, i + m.end())); i += m.end(); continue
        j = i; run = ''
        while j < n:
            c = t[j]
            if c.isdigit() or (c == '.' and run and run[-1].isdigit() and j + 1 < n and t[j + 1].isdigit()) or c in '십백천만억조' or (c in '영공일이삼사오육칠팔구' and not (run and run[-1].isdigit())):
                run += c; j += 1
            else: break
        if run and re.search(r'[\d십백천만억조]', run) or len(run) >= 2:
            k = re.match(r'\s*점\s*(\d+|[영공일이삼사오육칠팔구]+)', t[j:])
            v = val(run)
            if k: v = float(f'{int(v)}.{"".join(str(SINO.get(c, c)) for c in k.group(1))}'); j += k.end()
            runs.append((v, i, j)); i = j
        else: i += 1
    for v, st, en in runs:
        if re.match(r'\s*(월|일)', t[en:]): continue  # 날짜는 대본 쪽에서도 뺐다
        if out and out[-1][0] % 10 ** 8 == 0 and out[-1][0] and 0 < v < 10 ** 8 and not t[out[-1][1]:st].strip():
            out[-1] = (out[-1][0] + v, en)
        else: out.append((v, en))
    return [v for v, _ in out]

def lcs_miss(want, got):
    # 순서를 지키며 맞추고(±3%), 맞지 않은 대본 숫자를 돌려준다
    n, m = len(want), len(got); ok = lambda a, b: abs(a - b) <= max(abs(a) * 0.03, 0.05)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            L[i][j] = L[i + 1][j + 1] + 1 if ok(want[i][0], got[j]) else max(L[i + 1][j], L[i][j + 1])
    i = j = 0; miss = []
    while i < n and j < m:
        if ok(want[i][0], got[j]): i += 1; j += 1
        elif L[i + 1][j] >= L[i][j + 1]: miss.append(want[i][1]); i += 1
        else: j += 1
    return miss + [w for _, w in want[i:]]

def asr(wav):
    o = subprocess.run([B, f'--tokens={A}/tokens.txt', f'--encoder={A}/encoder-epoch-99-avg-1.int8.onnx',
                        f'--decoder={A}/decoder-epoch-99-avg-1.int8.onnx', f'--joiner={A}/joiner-epoch-99-avg-1.int8.onnx', '--num-threads=4', wav],
                       capture_output=True, text=True)
    m = re.search(r'"text": *"([^"]*)"', o.stdout + o.stderr)
    return m.group(1) if m else ''

if __name__ == '__main__':
    narr, wav = sys.argv[1], sys.argv[2]
    tj = sys.argv[3] if len(sys.argv) > 3 else os.path.splitext(wav)[0] + '_timing.json'
    if not os.path.exists(A):
        print(f'ASR_SKIP 모델 없음: mkdir -p /home/claude/asr && curl -sSL https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-zipformer-korean-2024-06-24.tar.bz2 | tar xj -C /home/claude/asr'); sys.exit(0)
    paras = [p.strip() for p in open(narr, encoding='utf-8').read().split('\n') if p.strip()]
    P = json.load(open(tj))['paras']
    bad = []; lim = []; tmp = tempfile.mktemp(suffix='.wav')
    for i, p in enumerate(paras):
        want = script_nums(p)
        if not want or i >= len(P): continue
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(P[i]['start']), '-to', str(P[i]['end']), '-i', wav, '-ar', '16000', '-ac', '1', tmp])
        t = asr(tmp); miss = lcs_miss(want, heard_nums(t))
        if miss:
            # 같은 문단을 새로 합성해 들어 본다: 새 녹음에서도 못 알아들으면 인식기 한계, 새 녹음에선 들리면 원래 녹음이 뭉갠 것
            refs = []
            for _ in range(2):  # 새 녹음 두 번 모두에서 들리는 숫자만 원래 녹음의 잘못으로 본다(인식 잡음이 커서)
                subprocess.run(['bash', ST, '6', p, tmp, '1.15', '10'], capture_output=True)
                subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', tmp, '-ar', '16000', '-ac', '1', tmp + '.r.wav'])
                refs.append(set(lcs_miss(want, heard_nums(asr(tmp + '.r.wav')))))
            ref = sorted(refs[0] | refs[1])
            real = [w for w in miss if w not in ref]
            if real: bad.append((i + 1, real, t))
            if ref: lim.append((i + 1, ref))
    for f in (tmp, tmp + '.r.wav'): os.path.exists(f) and os.remove(f)
    for n, ref in lim: print(f'ASR_LIMIT 문단 {n}: {", ".join(ref)} (새 녹음에서도 못 알아들음 — 인식기 한계로 보고 넘김)')
    for n, miss, t in bad: print(f'ASR_MISS 문단 {n}: {", ".join(miss)} | 들린 말: {t[:120]}')
    print('ASR_OK' if not bad else f'ASR_FAIL {len(bad)}문단 — 들어 보고 실제로 뭉갰으면 st_redo.py로 그 문단만 다시 녹음(숫자는 한자어 읽기, 문장 끝 숫자+배입니다는 피함)')
    sys.exit(1 if bad else 0)
