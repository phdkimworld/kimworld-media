#!/usr/bin/env python3
"""시장·거시·정책 층 검사(운영자 2026-11-22 "시황이나 거시경제 지정학 등 관련된 모든 통찰을 다 포함해서 컨텐츠를 제작", SKILL 3.6·R0.1·V2.10·K8·K9).
data_as_of 2026-11-23 이후 리포트·그 회차 대본·쇼츠·Threads에만 적용한다(지난 회차 소급 금지). --force면 날짜와 상관없이 검사.

  python3 tools/macro_check.py report <리포트.md>                 # easy_check.py가 자동으로 부른다
  python3 tools/macro_check.py script <video 폴더> [쇼츠 폴더]     # pre_tts_check.sh가 자동으로 부른다
  python3 tools/macro_check.py queue <대기열 json>...             # queue_check.py가 자동으로 부른다(Threads 첫 글·둘째 글)

리포트: 부록 '### 시장·거시·정책 배경' 절, 본문 '평소 민감도로 예상 vs 실제' 문장, 업종·시장 비교 그림(캡션에 업종·시장·예상·민감도),
  다음 거시 일정(FOMC·CPI·고용·PCE + 날짜), '사기 전에 확인할 것'에 거시 조건, 배경 절에 다른 핵심 종목 리포트 링크(통섭),
  정책 줄(채택한 연결 또는 '직접 연결 확인 안 됨', 없으면 WARN), 거시 단어 + '때문' 단정(링크 없으면 WARN)
대본: research/macro.md 있음, 한 문단(또는 이어진 두 문단)에 '민감도' + 거시·정책 단어 + 다음 거시 일정과 날짜, 길이 30~45초(WARN)
쇼츠: 시장 동반 한 문장(민감도·시장·나스닥·업종 + 함께·만큼·따라)
Threads: 첫 글 또는 둘째 글에 시장·거시 한 줄
"""
import datetime as dt
import glob
import json
import os
import re
import sys

START = "2026-11-23"
FORCE = "--force" in sys.argv
args = [a for a in sys.argv[1:] if a != "--force"]
MACRO = r"금리|연준|FOMC|연방공개시장위원회|물가|CPI|PCE|개인소비지출|고용 보고서|고용 지표|달러|유가|WTI|관세|수출 통제|수출 규제|보조금|세액 공제|IRA|인플레이션 감축법|국방 예산|정책|지정학|중국|VIX|변동성 지수|경기"
EVENT = r"FOMC|연준(의)? (금리 )?(회의|결정)|연방공개시장위원회|소비자물가|CPI|고용 보고서|개인소비지출|PCE|개인소득|물가 지표|국내총생산|GDP"
DATE = r"\d{1,2}월 \d{1,2}일|[일이삼사오육유칠팔구십]{1,3}월 [일이삼사오육칠팔구십]{1,4}일"
bad, warns = [], []


def fm_date(txt):
    m = re.search(r"^data_as_of:\s*\"?(\d{4}-\d\d-\d\d)", txt, re.M)
    return m.group(1) if m else ""


def report(p):
    txt = open(p, encoding="utf-8").read()
    if not FORCE and fm_date(txt) < START:
        print(f"MACRO_SKIP 리포트 data_as_of {fm_date(txt) or '없음'} < {START}"); sys.exit(0)
    body = txt.split("\n---", 2)[-1] if txt.startswith("---") else txt
    tk = (re.search(r"^ticker:\s*\"?([A-Z0-9.]+)", txt, re.M) or [None, ""])[1]
    appx = re.split(r"^## 숫자로 다시 보기\s*$", body, maxsplit=1, flags=re.M)
    story = appx[0]
    m = re.search(r"^#{2,3} 시장·거시·정책 배경[^\n]*\n(.*?)(?=^#{2,3} |\Z)", body, re.M | re.S)
    if not m:
        bad.append("MACRO_SEC 부록에 '### 시장·거시·정책 배경' 절이 없음(tools/macro_ctx.py → research/macro.md의 숫자로 표·정책 줄·통섭 링크)")
        sec = ""
    else:
        sec = m.group(1)
    paras = [x for x in body.split("\n\n")]
    if not any(re.search(r"평소[^.\n]{0,12}민감도", x) and "예상" in x and "실제" in x for x in paras):
        bad.append("MACRO_MKT 본문에 '평소 민감도로 예상한 움직임 vs 실제' 문장이 없음(macro.md 3절 한 문장 초안)")
    if not re.search(rf"({EVENT})[^\n]{{0,40}}({DATE})|({DATE})[^\n]{{0,40}}({EVENT})", body):
        bad.append("MACRO_CAL 다음 거시 일정(FOMC·CPI·고용·PCE 중 하나 + 날짜)이 없음(macro.md 4절)")
    imgs = re.findall(r"^!\[([^\]]*)\]", story, re.M)
    if not any(re.search(r"업종|시장|예상|민감도|펀드|나스닥|QQQ|S&P|누적 등락", c) for c in imgs):
        bad.append("MACRO_FIG 본문 그림 중 업종·시장 비교(종목 vs 업종 vs 시장 누적 등락) 또는 예상 vs 실제 그림이 없음(캡션에 업종·시장·예상·민감도 중 하나)")
    ck = re.search(r"^#{2,3} [^\n]*(확인할 것|체크리스트)[^\n]*\n(.*?)(?=^#{2,3} |\Z)", body, re.M | re.S)
    if not ck or not re.search(MACRO + r"|시장|나스닥|업종", ck.group(2)):
        bad.append("MACRO_CHK '사기 전에 확인할 것'에 거시 조건 1~2개가 없음(예: 다음 FOMC 날짜, 금리 방향에 민감한지)")
    if sec:
        links = [x for x in re.findall(r"/r/([a-z0-9]+)-20\d\d-\d\d", sec) if x.upper() != tk]
        if not links:
            bad.append("MACRO_X 배경 절에 같은 거시 요인을 받는 다른 핵심 종목 리포트 링크(/r/<티커>-…/)와 기저율 한 문장이 없음(macro.md 6절)")
        if "직접 연결 확인 안 됨" not in sec and not re.search(r"(관세|수출|보조금|세액|정책|규제|예산|행정명령|Federal Register|10-K|규칙)[^\n]*(https?://|\d{4}-\d\d-\d\d|\d{1,2}월 \d{1,2}일)", sec):
            warns.append("MACRO_POL 배경 절에 정책 줄이 없음 — 채택한 연결(날짜·1차 출처·연결 고리) 또는 '직접 연결 확인 안 됨' 한 줄")
    for para in paras:
        for s in re.split(r"(?<=[.?!다])\s+", para):
            if "때문" in s and re.search(MACRO, s) and not re.search(r"\]\(|https?://", para) and not s.lstrip().startswith(("|", "#")):
                warns.append(f"MACRO_CAUSE 거시 요인 '때문' 단정 — 근거 자료가 없으면 '같은 날 ~도 움직였다'로: {s.strip()[:50]}…"); break


def paras_of(path):
    return [x.strip() for x in open(path, encoding="utf-8").read().split("\n\n") if x.strip()]


def script(v, sh=None):
    v = os.path.abspath(v)
    rep = (glob.glob(os.path.join(v, "..", "report", "*-20*.md")) or [None])[0]
    d = ""
    if rep:
        site = os.path.join("/home/user/kimworld-site/content/reports", os.path.basename(rep))
        d = fm_date(open(site if os.path.exists(site) else rep, encoding="utf-8").read())
    nar = os.path.join(v, "narration.txt")
    if not d and os.path.exists(nar):
        d = dt.date.fromtimestamp(os.path.getmtime(nar)).isoformat()
    if not FORCE and d and d < START:
        print(f"MACRO_SKIP 회차 기준 {d} < {START}"); sys.exit(0)
    if not os.path.exists(os.path.join(v, "..", "research", "macro.md")):
        bad.append("MACRO_FILE research/macro.md 없음 → python3 tools/macro_ctx.py <티커> --date <기준일> --work <작업 폴더>")
    if os.path.exists(nar):
        ps = paras_of(nar)
        idx = [i for i, p in enumerate(ps) if "민감도" in p]
        if not idx:
            bad.append("MACRO_MKT 대본에 시장 동반 분해 문장('평소 민감도로 예상한 움직임은 …, 실제는 …')이 없음")
        else:
            i = idx[0]
            blk = ps[i] + ("\n" + ps[i + 1] if i + 1 < len(ps) else "")
            if not re.search(MACRO, blk):
                bad.append("MACRO_LINK 민감도 문단(또는 바로 다음 문단)에 거시·지정학 연결 한 문장(금리·연준·달러·관세·보조금·정책 등)이 없음")
            if not (re.search(EVENT, blk) and re.search(DATE, blk)):
                bad.append("MACRO_CAL 민감도 문단(또는 바로 다음 문단)에 다음 거시 일정과 날짜(예: '십이월 구일 연준 회의')가 없음")
            n = len(re.sub(r"\s", "", ps[i]))
            if not 150 <= n <= 330:
                warns.append(f"MACRO_LEN 거시 문단 {n}자(공백 뺌) — 30~45초 ≈ 150~330자")
            if "때문" in blk:
                warns.append("MACRO_CAUSE 거시 문단의 '때문' — 근거 자료가 있을 때만, 아니면 '같은 날 ~도 움직였습니다'")
    if sh and os.path.exists(os.path.join(sh, "narration.txt")):
        t = open(os.path.join(sh, "narration.txt"), encoding="utf-8").read()
        if not re.search(r"[^.\n]*(민감도|시장|나스닥|업종)[^.\n]*(함께|같이|따라|만큼|비슷)[^.\n]*", t) and not re.search(r"(나스닥|시장|업종|펀드)[가-힣]*도 [^.\n]{0,20}(내렸|올랐|떨어|뛰)", t):
            bad.append("MACRO_SHORTS 쇼츠에 시장 동반 한 문장(예: '같은 세 거래일, 나스닥도 칠 퍼센트 내렸습니다')이 없음")


def queue(files):
    for f in files:
        b = os.path.basename(f)
        if re.search(r"-(th\d|reels|igreels|fb|ig|card)\w*\.json$", b):
            continue
        d = json.load(open(f, encoding="utf-8"))
        if "threads" not in (d.get("channels") or ["threads"]):
            continue
        if not FORCE and str(d.get("publish_at", ""))[:10] < START:
            continue
        texts = [d.get("text", "")]
        th2 = f[:-5] + "-th2.json"
        if os.path.exists(th2):
            texts.append(json.load(open(th2, encoding="utf-8")).get("text", ""))
        if not any(re.search(MACRO + r"|민감도|나스닥|QQQ|시장도|업종도", t) for t in texts):
            bad.append(f"MACRO_THREADS {b}: Threads 첫 글·둘째 글 어디에도 시장·거시 한 줄이 없음(예: '· 평소 시장 민감도로 예상 -11.7%, 실제 -13.5%')")


if not args:
    print(__doc__); sys.exit(1)
kind = args[0]
if kind == "report":
    report(args[1])
elif kind == "script":
    script(args[1], args[2] if len(args) > 2 else None)
elif kind == "queue":
    queue(args[1:])
else:
    print(__doc__); sys.exit(1)
for w in warns:
    print("WARN " + w)
print("\n".join(bad) if bad else "MACRO_OK")
sys.exit(1 if bad else 0)
