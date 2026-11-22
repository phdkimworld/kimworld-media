#!/usr/bin/env python3
"""유튜브 한국어 자막(SRT) 만들기·올리기 (운영자 지시 2026-11-20: 스튜디오 28일 자료에서 시청의 25.6%가 한국어 자막을 켜고 봄, 지금은 자동 생성 자막뿐).

사용:
  python3 tools/yt_captions.py <video 폴더> [--shorts <shorts 폴더>] [--dry]
      video 폴더의 raw_timing.json(문장 시각)·video_id로 captions.ko.srt를 쓰고, --dry가 아니면 올린다.
      쇼츠 폴더(shorts_raw_timing.json·video_id)도 주면 같이 만든다(make_shorts.py가 문장을 0.05초 앞 + 0.15초 간격으로 다시 붙인 시간축을 따른다).
      <video 폴더> 자리에 쇼츠 폴더만 줘도 된다(shorts_raw_timing.json이 있으면 쇼츠로 본다).
  python3 tools/yt_captions.py <폴더> --vid <영상ID>   video_id 파일 대신 이 ID로(업로드 직후 yt_api_upload.py가 부른다)
  python3 tools/yt_captions.py --selftest      숫자 변환 단위 시험
결과: 영상마다 한 줄 'CAPTION <영상ID> <inserted|updated|dry> <자막ID|SRT 경로> cues=N num=변환/보류'. 실패는 'CAPTION_FAIL ...'(종료 코드 1).

규칙:
- 대본 text는 TTS용 한글 숫자다. 숫자 뒤에 단위(달러·퍼센트·년·월·일·분기·거래일 …)가 붙거나 '점'으로 이어질 때만 숫자로 되돌린다
  (일 점 일오 달러 → 1.15달러, 이천이십오년 유월 → 2025년 6월, 삼 퍼센트 → 3%). 일반 단어 속 '일·이·사'는 건드리지 않는다.
- 자체 검사: 변환한 값이 같은 회차 출처(research/hooks.md·report/*.md·slides.json·shorts.json)의 숫자 목록에 없으면 한글 그대로 둔다(틀린 숫자보다 낫다).
  '이'(이 분·이 주)처럼 뜻이 둘인 한 글자 숫자 + 한 글자 단위, 단위 뒤에 조사가 아닌 글자가 붙은 경우(이 회사)도 그대로 둔다.
- SRT: 한 자막 최대 2줄·줄당 약 18자, 긴 문장은 글자 수 비례로 시간 분할, 최소 1초, 자막 사이 빈틈 없음.
- 올리기: captions.list로 같은 언어(ko)·같은 이름('한국어') 자막이 있으면 captions.update로 교체(중복 금지), 없으면 captions.insert(400단위).
  googleapiclient(httplib2) 압축 버그(yt_subs.py 11-18)를 피해 requests로 직접 multipart. 인증 값은 환경 변수에서만 읽고 출력하지 않는다.
- 업로드 흐름(yt_api_upload.py 업로드 직후)에서 부르며, 실패해도 업로드는 막지 않는다.
"""
import argparse, glob, json, math, os, re, sys

NAME, LANG = "한국어", "ko"
MAXLINE, MAXCUE = 18, 34

# ───────────── 숫자 되돌리기 ─────────────
DIG = {"영": 0, "공": 0, "일": 1, "이": 2, "삼": 3, "사": 4, "오": 5, "육": 6, "칠": 7, "팔": 8, "구": 9}
D1 = "일이삼사오육칠팔구"
GRP = f"(?:[{D1}]?천)?(?:[{D1}]?백)?(?:[{D1}]?십)?[{D1}]?"
NUM = f"(?:{GRP}조\\s?)?(?:{GRP}억\\s?)?(?:{GRP}만\\s?)?{GRP}"
DEC = "[영공일이삼사오육칠팔구]+"
# 단위: 긴 것부터. strong = 뜻이 하나(숫자 뒤면 단위), weak = 한 글자라 단어와 헷갈릴 수 있음
STRONG = ["퍼센트 포인트", "퍼센트포인트", "퍼센트", "거래일", "영업일", "개월", "분기", "주년", "달러", "센트", "시간", "년", "월"]
WEAK = ["일", "주", "시", "분", "초", "번", "개", "배", "명", "원", "건", "위", "회", "차", "편"]
UNITS = sorted(STRONG + WEAK, key=len, reverse=True)
UNIT_OUT = {"퍼센트 포인트": "%p", "퍼센트포인트": "%p", "퍼센트": "%"}
I_OK = {"퍼센트 포인트", "퍼센트포인트", "퍼센트", "달러", "센트", "분기", "거래일", "영업일", "개월", "주년"}
PARTICLE = set("을를이가은는의에와과도만씩째당로으까부보동간짜치께며고면나라야인엔요다에서입였쯤정남넘밖뿐처마")
LEFT_OK = re.compile(r"(?:^|[\s,.(\"'“‘~·/\-])$")
MONTHS = {"일월": 1, "이월": 2, "삼월": 3, "사월": 4, "오월": 5, "유월": 6, "육월": 6, "칠월": 7, "팔월": 8, "구월": 9,
          "시월": 10, "십월": 10, "십일월": 11, "십이월": 12}

_U = '|'.join(map(re.escape, UNITS))
# 단위가 있는 꼴을 먼저(삼십일 → 30일로 되짚어 읽게), 없으면 '점'이 있는 꼴(일 점 일에서). 정수 자리 '영'은 '점' 앞에서만(영 점 구사 배)
TOK_U = re.compile(f"(?=[{D1}십백천만억조영])({NUM}|영)(?:( 점 )({DEC}))?(\\s?)({_U})")
TOK_D = re.compile(f"(?=[{D1}십백천만억조영])({NUM}|영)( 점 )({DEC})()()")


def grp_val(s):
    v, cur = 0, None
    for ch in s:
        if ch in DIG:
            cur = DIG[ch]
        else:
            v += (cur if cur is not None else 1) * {"십": 10, "백": 100, "천": 1000}[ch]; cur = None
    return v + (cur or 0)


def parse_int(s):
    s = s.replace(" ", "")
    if not s:
        return None
    total, rest = 0, s
    for big, mul in (("조", 10 ** 12), ("억", 10 ** 8), ("만", 10 ** 4)):
        if big in rest:
            a, rest = rest.split(big, 1)
            total += (grp_val(a) if a else 1) * mul
    return total + (grp_val(rest) if rest else 0)


def fmt_int(n, unit):
    if unit == "년" or n < 1000:
        return str(n)
    if n >= 10 ** 4 and n % 10 ** 4 == 0 or n >= 10 ** 8:
        parts = []
        for mul, nm in ((10 ** 12, "조"), (10 ** 8, "억"), (10 ** 4, "만")):
            q, n = divmod(n, mul)
            if q: parts.append(f"{q:,}{nm}")
        if n: parts.append(f"{n:,}")
        return " ".join(parts)
    return f"{n:,}"


def src_numbers(folders):
    """같은 회차 출처의 숫자 목록(float 집합)."""
    files = []
    for f in folders:
        base = os.path.dirname(os.path.abspath(f).rstrip("/"))
        files += glob.glob(os.path.join(base, "research", "hooks.md")) + glob.glob(os.path.join(base, "report", "*.md"))
        files += glob.glob(os.path.join(f, "slides.json")) + glob.glob(os.path.join(f, "shorts.json"))
    nums = set()
    for p in files:
        try:
            t = open(p, encoding="utf-8").read()
        except Exception:
            continue
        t = re.sub(r"(?<=\d),(?=\d{3})", "", t)
        for m in re.finditer(r"\d+(?:\.\d+)?", t):
            nums.add(float(m.group(0)))
            for part in m.group(0).split("."):
                nums.add(float(int(part)))
    return nums, files


def known(val, nums):
    if nums is None:
        return True
    if any(abs(val - n) < 1e-6 for n in nums):
        return True
    for sc in (1e4, 1e6, 1e8, 1e9, 1e12):  # 억·만 금액은 출처의 4.32억·$432M 같은 표기와도 맞춰 본다
        x = val / sc
        if x < 1:
            break
        if any(abs(round(x, d) - n) < 1e-6 for n in nums for d in (0, 1, 2)):
            return True
    return False


def convert(text, nums=None, stats=None):
    """한글 숫자 → 읽기 쉬운 숫자 표기. nums가 있으면 출처에 있는 값만 바꾼다."""
    st = stats if stats is not None else {"ok": 0, "keep": 0, "kept": []}
    # 1) 달(유월·시월·십일월 …): 앞이 경계이고 뒤가 경계·조사
    def mon(m):
        w = m.group(2); v = MONTHS[w]
        if not known(v, nums):
            st["keep"] += 1; st["kept"].append(w); return m.group(0)
        st["ok"] += 1; return f"{m.group(1)}{v}월"
    text = re.sub(r"(^|[\s,(\"'“‘~])(" + "|".join(sorted(MONTHS, key=len, reverse=True)) + r")(?=[\s,.)\"'”’~]|$|[" + "".join(PARTICLE) + "])", mon, text)
    out, i = [], 0
    # 앞이 경계(문장 처음·띄어쓰기·문장부호)인 자리에서만 숫자를 읽는다(통일·열일곱·주식이 속 글자는 건너뜀)
    def tok(p):
        for R in (TOK_U, TOK_D):
            m = R.match(text, p)
            if m and m.group(1).strip():
                return m
    starts = (tok(p) for p in range(len(text)) if p == 0 or LEFT_OK.search(text[:p]))
    for m in starts:
        if m is None or m.start() < i:
            continue
        whole, ip, dot, dec, sp, unit = m.group(0), m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        if not ip.strip():
            continue
        after = text[m.end():m.end() + 1]
        if not dot and not unit:
            continue
        hangul_after = bool(after) and re.match(r"[가-힣]", after) and after not in PARTICLE
        if hangul_after and not dot and (unit in WEAK or ip.replace(" ", "") == "이"):
            continue  # 이 회사·이 점 이해 → 그대로
        if ip == "영" and not dot:
            continue
        if unit == "주" and after in ("가", "식") and len(ip.replace(" ", "")) == 1:
            continue  # 이 주가·삼 주식
        ipc = ip.replace(" ", "")
        if ipc in ("만", "억", "조"):
            continue
        single = len(ipc) == 1
        month_day = unit == "일" and re.search(r"\d월 $", text[:m.start()])
        if single and ipc == "이" and not dot and unit not in I_OK and not month_day:
            continue  # 이 분·이 주·이 시간·이 년
        if single and not dot and not sp and (unit in WEAK or unit in ("년", "월")):
            # 붙은 한 글자(이번·오일·일년·삼월)는 그대로. 달은 위 달 표에서, '십이월 팔일'처럼 달 뒤의 날만 바꾼다
            if not (unit == "일" and (re.search(r"\d월 $", text[:m.start()]) or ip in "육칠팔구십")):
                continue
        val = parse_int(ip)
        if val is None:
            continue
        sval = str(val) if not dot else f"{val}.{''.join(str(DIG[c]) for c in dec)}"
        fval = float(sval)
        if not known(fval, nums) and not (unit == "센트" and known(fval / 100, nums)):
            st["keep"] += 1; st["kept"].append(whole); continue
        num = fmt_int(val, unit) if not dot else f"{fmt_int(val, unit)}.{sval.split('.')[1]}"
        u = UNIT_OUT.get(unit, unit or "")
        big = num.endswith(("억", "만", "조")) and u and u not in ("%", "%p")
        out.append(text[i:m.start()]); out.append(num + (" " if big else "") + u)
        i = m.end(); st["ok"] += 1
    out.append(text[i:])
    res = "".join(out)
    # 숫자 앞 '마이너스 ' → '-'
    res = re.sub(r"마이너스 (?=\d)", "-", res)
    return res


SELFTEST = [
    ("일 점 일오 달러", "1.15달러"), ("일 점 영삼 달러", "1.03달러"), ("이천이십오년 유월", "2025년 6월"),
    ("사 분기", "4분기"), ("십일월 십구일", "11월 19일"), ("삼 퍼센트", "3%"),
    ("장중 일 점 일오 달러까지 올랐던 주식이 일 점 영삼 달러로 마감했습니다.", "장중 1.15달러까지 올랐던 주식이 1.03달러로 마감했습니다."),
    ("삼 거래일 만에 십팔 점 칠 퍼센트가 빠졌다", "3거래일 만에 18.7%가 빠졌다"),
    ("일 달러 십일 센트 위라는 항목", "1달러 11센트 위라는 항목"),
    ("시가총액은 약 십사억 사천만 달러입니다.", "시가총액은 약 14억 4,000만 달러입니다."),
    ("구월 말 현금은 약 일억 삼천만 달러로", "9월 말 현금은 약 1억 3,000만 달러로"),
    ("이천이십년부터 일곱 번의 심포지엄", "2020년부터 일곱 번의 심포지엄"),
    ("보통 백팔십 일의 회복 기간", "보통 180일의 회복 기간"),
    ("이 회사의 심포지엄 날", "이 회사의 심포지엄 날"), ("이 분이 말했다", "이 분이 말했다"), ("이번 주가는", "이번 주가는"),
    ("이 주가 흐름", "이 주가 흐름"), ("동일 거래일", "동일 거래일"), ("일부 투자자", "일부 투자자"), ("통일 점수", "통일 점수"),
    ("십분 이해", "십분 이해"), ("사 주세요", "사 주세요"), ("오늘 사 분기", "오늘 4분기"),
    ("이 점 팔 퍼센트 높은", "2.8% 높은"), ("육십오 점 오 퍼센트만큼", "65.5%만큼"), ("이십 거래일째입니다", "20거래일째입니다"),
    ("십이월 팔일 종가", "12월 8일 종가"), ("일 년 전보다", "1년 전보다"), ("이 퍼센트 포인트", "2%p"),
    ("마이너스 삼 퍼센트", "-3%"), ("영 점 구사 배로", "0.94배로"), ("삼분기 매출", "3분기 매출"), ("삼십일 동안", "30일 동안"),
    ("이십일 점 육 퍼센트", "21.6%"), ("일 점 칠 배입니다", "1.7배입니다"), ("일 점 일에서 일 점 이 달러", "1.1에서 1.2달러"),
    ("이삼십 퍼센트", "이삼십 퍼센트"), ("이번 분기", "이번 분기"), ("이 시간", "이 시간"), ("천만 주를", "1,000만 주를"), ("오일 가격", "오일 가격"), ("일 달러선 바로 위", "1달러선 바로 위"), ("구일은", "9일은"), ("11월 이일 기준", "11월 2일 기준"), ("일일 거래량", "일일 거래량"),
]


def selftest():
    bad = 0
    for src, want in SELFTEST:
        got = convert(src)
        if got != want:
            bad += 1; print(f"✗ {src!r} → {got!r} (기대 {want!r})")
    # 출처 대조: 출처에 없는 값은 그대로
    st = {"ok": 0, "keep": 0, "kept": []}
    g = convert("일 점 일오 달러와 칠 점 칠 퍼센트", {1.15, 1.0, 15.0}, st)
    if g != "1.15달러와 칠 점 칠 퍼센트":
        bad += 1; print(f"✗ 출처 대조 → {g!r}")
    # SRT 자르기: 줄 18자 안팎·2줄·1초 이상·빈틈 없음
    cues = build_cues([{"start": 0.0, "end": 9.0, "text": "가" * 10 + " " + "나" * 10 + ", " + "다" * 12 + " " + "라" * 15 + " " + "마" * 8},
                       {"start": 9.6, "end": 10.2, "text": "짧은 문장"}], None, {"ok": 0, "keep": 0, "kept": []})
    for k, (a, b, t) in enumerate(cues):
        if b - a < 1.0 - 1e-6 and k < len(cues) - 1: bad += 1; print("✗ 1초 미만", a, b, t)
        if t.count("\n") > 1: bad += 1; print("✗ 3줄", t)
        if k and abs(cues[k - 1][1] - a) > 1e-6: bad += 1; print("✗ 빈틈", cues[k - 1][1], a)
    print(f"SELFTEST {'OK' if not bad else 'FAIL'} {len(SELFTEST) + 2 - bad}/{len(SELFTEST) + 2}")
    return 0 if not bad else 1


# ───────────── SRT ─────────────
PUNCT_BREAK = re.compile(r"[,.?!…]$")


def split_words(words, n):
    """단어 목록을 n덩어리로(글자 수 균형, 쉼표 뒤 선호)."""
    if n <= 1 or len(words) <= 1:
        return [words]
    L = [len(w) + 1 for w in words]; tot = sum(L); cut, acc, pos = [], 0, []
    for k, l in enumerate(L[:-1]):
        acc += l; pos.append((acc, k + 1, bool(PUNCT_BREAK.search(words[k]))))
    last = 0
    for j in range(1, n):
        tgt = tot * j / n
        cands = [p for p in pos if p[1] > last and p[1] < len(words) - (n - 1 - j)]
        if not cands: break
        best = min(cands, key=lambda p: abs(p[0] - tgt) - (5 if p[2] else 0))
        cut.append(best[1]); last = best[1]
    out, s = [], 0
    for c in cut + [len(words)]:
        out.append(words[s:c]); s = c
    return [o for o in out if o]


def two_lines(s):
    if len(s) <= MAXLINE + 1:
        return s
    a, b = split_words(s.split(" "), 2) if " " in s else ([s], [])
    return " ".join(a) + ("\n" + " ".join(b) if b else "")


def build_cues(sents, nums, st):
    cues = []
    for s in sents:
        t = convert(s["text"].strip(), nums, st)
        dur = s["end"] - s["start"]
        n = max(1, math.ceil(len(t) / MAXCUE))
        n = max(1, min(n, int(dur // 1.0)))
        chunks = [" ".join(c) for c in split_words(t.split(" "), n)]
        w = [max(1, len(c.replace(" ", ""))) for c in chunks]; tw = sum(w); a = s["start"]
        for c, wi in zip(chunks, w):
            b = a + dur * wi / tw
            cues.append([a, b, two_lines(c)]); a = b
        # 비례 분할로 1초 미만이 생기면 이웃과 합친다
        k = len(cues) - len(chunks)
        while True:
            short = [j for j in range(k, len(cues)) if cues[j][1] - cues[j][0] < 1.0 and len(cues) - k > 1]
            if not short: break
            j = short[0]; o = j + 1 if j + 1 < len(cues) else j - 1
            lo, hi = min(j, o), max(j, o)
            cues[lo:hi + 1] = [[cues[lo][0], cues[hi][1], two_lines((cues[lo][2] + " " + cues[hi][2]).replace("\n", " "))]]
    # 빈틈 없이: 앞 자막 끝 = 다음 자막 시작, 너무 짧은 문장은 다음 자막을 늦게 시작하지 않고 앞 자막 끝만 늘린다
    for k in range(len(cues) - 1):
        cues[k][1] = cues[k + 1][0]
    for k in range(len(cues) - 1):  # 최소 1초(짧은 문장): 다음 자막 시작을 미룬다(다음 자막도 1초 이상 남을 때만)
        if cues[k][1] - cues[k][0] < 1.0 and cues[k + 1][1] - (cues[k][0] + 1.0) >= 1.0:
            cues[k][1] = cues[k + 1][0] = cues[k][0] + 1.0
    if cues and cues[-1][1] - cues[-1][0] < 1.0:
        cues[-1][1] = cues[-1][0] + 1.0
    return cues


def ts(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def srt(cues):
    return "".join(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n" for i, (a, b, t) in enumerate(cues, 1))


def long_sents(folder):
    # 브랜드 인트로(2026-11-22, 사이트 slidekit/brand.py): 합성이 첫 훅 문단 뒤에 2.4초 스팅을 끼우면 뒤 문장이 그만큼 밀린다.
    # 그때 make_slide_video.py가 영상 시간축 문장 시각을 slides_out/timing_video.json에 남기므로 그것을 먼저 쓴다(없으면 raw_timing.json = 인트로 없음)
    tv = os.path.join(folder, "slides_out", "timing_video.json")
    src = tv if os.path.exists(tv) else os.path.join(folder, "raw_timing.json")
    tm = json.load(open(src, encoding="utf-8"))
    return [s for p in tm["paras"] for s in p["sents"]]


def shorts_sents(folder):
    """make_shorts.py 1)과 같은 시간축: LEAD 0.05초 뒤부터 문장(앞 0.02·뒤 0.05초 포함)을 0.15초 간격으로 붙인다."""
    tm = json.load(open(os.path.join(folder, "shorts_raw_timing.json"), encoding="utf-8"))
    GAP, LEAD = 0.15, 0.05; t = LEAD; out = []
    for s in [s for p in tm["paras"] for s in p["sents"]]:
        a0 = max(s["start"] - 0.02, 0); seg = (s["end"] + 0.05) - a0
        out.append({"start": round(t + (s["start"] - a0), 3), "end": round(t + (s["end"] - a0), 3), "text": s["text"]}); t += seg + GAP
    return out


def make(folder, shorts, nums):
    st = {"ok": 0, "keep": 0, "kept": []}
    sents = shorts_sents(folder) if shorts else long_sents(folder)
    cues = build_cues(sents, nums, st)
    if not shorts:  # 브랜드 인트로 스팅(목소리 없음) 동안은 앞 자막을 늘려 덮지 않는다 — 이 구간만 빈틈 허용
        try:
            bi = json.load(open(os.path.join(folder, "slides_out", "segments.json"), encoding="utf-8")).get("brand_intro")
        except (OSError, ValueError):
            bi = None
        if bi:
            for c in cues:
                if c[0] < bi[0] < c[1]: c[1] = max(bi[0], c[0] + 1.0)
    path = os.path.join(folder, "captions.ko.srt")
    open(path, "w", encoding="utf-8").write(srt(cues))
    return path, cues, st


# ───────────── 올리기 ─────────────
_tok = None


def token():
    global _tok
    if _tok is None:
        import requests
        r = requests.post("https://oauth2.googleapis.com/token", data={"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                                                                      "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"}, timeout=30)
        if r.status_code >= 300:
            raise RuntimeError(f"auth HTTP {r.status_code} {r.text[:120]}")
        _tok = r.json()["access_token"]
    return _tok


def api_err(r):
    try:
        j = r.json()["error"]; reason = ",".join(x.get("reason", "") for x in j.get("errors", [])) or j.get("message", "")
    except Exception:
        reason = r.text[:150]
    return f"HTTP {r.status_code} {reason}"


def upload(vid, path):
    import requests
    H = {"Authorization": f"Bearer {token()}"}
    r = requests.get("https://www.googleapis.com/youtube/v3/captions", params={"part": "snippet", "videoId": vid}, headers=H, timeout=30)
    if r.status_code >= 300:
        raise RuntimeError("list " + api_err(r))
    same = [c for c in r.json().get("items", []) if c["snippet"].get("language") == LANG and c["snippet"].get("name") == NAME
            and c["snippet"].get("trackKind", "standard") != "asr"]
    data = open(path, "rb").read()
    if same:
        meta = {"id": same[0]["id"], "snippet": {"isDraft": False}}
        r = requests.put("https://www.googleapis.com/upload/youtube/v3/captions", params={"part": "snippet", "uploadType": "multipart"}, headers=H,
                         files={"metadata": ("metadata", json.dumps(meta), "application/json; charset=UTF-8"),
                                "media": ("captions.ko.srt", data, "application/octet-stream")}, timeout=120)
        kind = "updated"
    else:
        meta = {"snippet": {"videoId": vid, "language": LANG, "name": NAME, "isDraft": False}}
        r = requests.post("https://www.googleapis.com/upload/youtube/v3/captions", params={"part": "snippet", "uploadType": "multipart"}, headers=H,
                          files={"metadata": ("metadata", json.dumps(meta), "application/json; charset=UTF-8"),
                                 "media": ("captions.ko.srt", data, "application/octet-stream")}, timeout=120)
        kind = "inserted"
    if r.status_code >= 300:
        raise RuntimeError(("update " if kind == "updated" else "insert ") + api_err(r))
    return kind, r.json()["id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", nargs="?"); ap.add_argument("--shorts"); ap.add_argument("--dry", action="store_true")
    ap.add_argument("--vid", help="첫 폴더의 영상 ID(video_id 파일이 아직 없을 때, yt_api_upload.py가 넘긴다)")
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--show-kept", action="store_true", help="출처에 없어 한글로 둔 구간 출력")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.folder:
        ap.error("video 폴더가 필요합니다")
    jobs = []
    for f in [a.folder] + ([a.shorts] if a.shorts else []):
        f = os.path.abspath(f)
        if os.path.exists(os.path.join(f, "shorts_raw_timing.json")):
            jobs.append((f, True))
        elif os.path.exists(os.path.join(f, "raw_timing.json")):
            jobs.append((f, False))
        else:
            print(f"CAPTION_FAIL {f} 타이밍 파일 없음"); sys.exit(1)
    nums, _ = src_numbers([f for f, _ in jobs])
    rc = 0
    for f, sh in jobs:
        try:
            path, cues, st = make(f, sh, nums or None)
            vid = open(os.path.join(f, "video_id")).read().strip() if os.path.exists(os.path.join(f, "video_id")) else ""
            if a.vid and f == jobs[0][0]:
                vid = a.vid
            if a.show_kept and st["kept"]:
                print("  한글로 둔 구간: " + " | ".join(st["kept"]))
            tail = f"cues={len(cues)} num={st['ok']}/{st['keep']}"
            if a.dry:
                print(f"CAPTION {vid or '-'} dry {path} {tail}"); continue
            if not re.fullmatch(r"[\w-]{11}", vid):
                raise RuntimeError("video_id 없음")
            kind, cid = upload(vid, path)
            print(f"CAPTION {vid} {kind} {cid} {tail}")
        except Exception as e:
            print(f"CAPTION_FAIL {os.path.basename(os.path.dirname(f))}/{os.path.basename(f)} {str(e)[:200]}"); rc = 1
    sys.exit(rc)


if __name__ == "__main__":
    main()
