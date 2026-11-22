#!/usr/bin/env python3
"""시장·거시·정책 배경 한 장(research/macro.md) — 운영자 2026-11-22 "종목 관련 정보 뿐만 아니라 시황이나 거시경제 지정학 등
관련된 모든 통찰을 다 포함해서 컨텐츠를 제작". 매 회차(롱폼·쇼츠·리포트·Threads)의 '시장·거시·정책 배경' 층의 숫자 원천이다.

사용: python3 tools/macro_ctx.py <TICKER> [--date YYYY-MM-DD] [--from YYYY-MM-DD] [--work <작업 폴더>] [--mkt QQQ] [--no-policy] [--no-peers]
  --date  기준일(그날 이하 마지막 확정 종가일). 없으면 오늘 이하 마지막 확정 종가일(미국 동부 16:30 전이면 오늘 봉은 버림)
  --from  사건 구간 시작(그날 종가 = 기준). 없으면 같은 티커 직전 리포트 data_as_of, 그것도 없으면 기준일 5거래일 전
  --work  작업 폴더(기본 /home/claude/<소문자 티커>) → <work>/research/macro.md, macro.json, macro_px/*.json(그림용 종가), macro_figs.json(figkit 초안)
  --mkt   시장 기준(기본 QQQ, 주간 결산 pattern-2026-11-22와 같음). 업종 기준은 review/sector_map.md 업종 ETF

담는 것(숫자마다 출처·기준일)
  1 시황: SPY(S&P 500)·QQQ·나스닥 종합·IWM(러셀 2000)·업종 ETF·비교 종목 1/5/20/252거래일 등락, VIX(Cboe)
  2 거시: 미 국채 10년·2년(재무부 일별 금리), 달러(연준 H.10 광의 달러지수 + UUP), WTI(EIA 일별 현물), 비트코인(코인 관련만, 크라켄)
  3 시장 동반 분해: 사건 구간 종목 수익률 = 베타 × 시장(업종) 수익률 + 고유 부분. 베타는 구간 시작 전 250거래일 하루 수익률 회귀.
    '평소 민감도로 예상한 움직임 vs 실제' 한 문장 초안 + 평소 흔들림(고유 부분 하루 표준편차 × √거래일) 안/밖 판정
  4 다음 거시 일정: FOMC(연준 공식 일정), GDP·개인소득·지출(PCE, BEA 공식 일정), CPI·고용(BLS 공식 일정 — 막히면 '확인 안 됨')
  5 지정학·정책: 최신 연차 보고서(10-K·20-F·40-F) 키워드 횟수와 첫 구절, Federal Register 최근 180일 규칙·대통령 문서 후보.
    결론 줄 기본값은 '직접 연결 확인 안 됨' — 에이전트가 10-K 위험 요인과 맞는 것만 한 줄로 채택(억지 연결 금지)
  6 통섭: 핵심 종목(review/core_tickers.md)의 같은 구간 '예상 vs 실제'와 기저율 한 문장, 리포트 링크
원천이 막히면 우회하지 않고 /home/claude/macro_ctx/NEED.txt에 필요한 명령을 적는다. 종목 시세가 막히면 exit 2.
User-Agent 'Mozilla/5.0 research', SEC는 'Mozilla/5.0 research admin@example.com'(개인 이메일 금지).
"""
from __future__ import annotations

import csv
import datetime as dt
import glob
import html
import io
import json
import math
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__)); MEDIA = os.path.dirname(HERE)
SITE = os.environ.get("KW_SITE", os.path.join(os.path.dirname(MEDIA), "kimworld-site"))
CACHE = os.path.expanduser("~/.cache/kimworld/macro"); os.makedirs(CACHE, exist_ok=True)
NEED = "/home/claude/macro_ctx/NEED.txt"
UA = {"User-Agent": "Mozilla/5.0 research", "Accept": "*/*"}
UA_SEC = {"User-Agent": "Mozilla/5.0 research admin@example.com"}
ETF_NAME = {"SPY": "S&P 500 펀드(SPY)", "QQQ": "나스닥 100 펀드(QQQ)", "COMP": "나스닥 종합지수", "IWM": "러셀 2000 소형주 펀드(IWM)",
            "QTUM": "양자 펀드(QTUM)", "HDRO": "수소 펀드(HDRO)", "ICLN": "청정에너지 펀드(ICLN)", "URA": "우라늄 펀드(URA)", "NLR": "원전 펀드(NLR)",
            "LIT": "배터리·리튬 펀드(LIT)", "ITA": "항공우주·방산 펀드(ITA)", "ARKQ": "자율기술 펀드(ARKQ)", "UFO": "우주 펀드(UFO)", "ARKX": "우주 탐사 펀드(ARKX)",
            "WGMI": "비트코인 채굴 펀드(WGMI)", "IBIT": "비트코인 현물 펀드(IBIT)", "SMH": "반도체 펀드(SMH)", "IGV": "소프트웨어 펀드(IGV)", "BOTZ": "로봇·AI 펀드(BOTZ)",
            "XBI": "바이오 펀드(XBI)", "DRIV": "전기차·자율주행 펀드(DRIV)", "TAN": "태양광 펀드(TAN)", "BLOK": "블록체인 펀드(BLOK)", "UUP": "달러 강세 펀드(UUP)"}
ETFS = set(ETF_NAME) - {"COMP"}
INDEX = {"COMP"}
SRC_NQ = "나스닥 API historical(확정 종가)"
sources: list[tuple[str, str]] = []
needs: list[str] = []


def need(what: str, cmd: str):
    needs.append(f"- {what}: {cmd}")


def get(url: str, hdr=None, timeout=25, cache_h=6.0, name=None) -> bytes | None:
    key = os.path.join(CACHE, name or re.sub(r"[^A-Za-z0-9]+", "_", url)[-150:])
    if os.path.exists(key) and time.time() - os.path.getmtime(key) < cache_h * 3600:
        return open(key, "rb").read()
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers=hdr or UA), timeout=timeout).read()
    except Exception as e:  # 막힘: 우회하지 않는다
        sys.stderr.write(f"[막힘] {url[:100]} {type(e).__name__}: {str(e)[:80]}\n")
        return None
    open(key, "wb").write(b)
    return b


# ---------- 날짜 ----------
sys.path.insert(0, HERE)
from tdays import is_td  # noqa: E402  (NYSE 휴장일 표)


def josa(w: str, a: str, b: str) -> str:
    """받침 있으면 a(은·이), 없으면 b(는·가). 한글이 아니면 숫자·영문 끝 발음으로 대략."""
    c = w.rstrip(")")[-1:] if w else ""
    if "가" <= c <= "힣":
        return w + (a if (ord(c) - 0xAC00) % 28 else b)
    return w + (a if c.upper() in "LMNR0136789" else b)


def kd(s: str) -> str:
    return f"{int(s[5:7])}월 {int(s[8:10])}일"


def et_now() -> dt.datetime:
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("America/New_York"))
    except Exception:
        return dt.datetime.utcnow() - dt.timedelta(hours=5)


def last_closed_day(want: str | None) -> str:
    n = et_now()
    d = dt.date.fromisoformat(want) if want else n.date()
    if not want and (n.hour, n.minute) < (16, 30):
        d -= dt.timedelta(days=1)
    if d >= n.date() and (n.hour, n.minute) < (16, 30):
        d = n.date() - dt.timedelta(days=1)
    while not is_td(d):
        d -= dt.timedelta(days=1)
    return d.isoformat()


# ---------- 시세 ----------
def nasdaq(sym: str, frm: str, asof: str) -> dict[str, float]:
    classes = ["etf"] if sym in ETFS else ["index"] if sym in INDEX else ["stocks", "etf"]
    for cls in classes:
        url = f"https://api.nasdaq.com/api/quote/{sym}/historical?assetclass={cls}&fromdate={frm}&todate={asof}&limit=9999"
        b = get(url, {"User-Agent": "Mozilla/5.0 research", "Accept": "application/json"})
        if b is None:
            need(f"{sym} 시세", f"curl -s -A 'Mozilla/5.0 research' '{url}'")
            return {}
        try:
            rows = ((json.loads(b).get("data") or {}).get("tradesTable") or {}).get("rows") or []
        except ValueError:
            rows = []
        out = {}
        for r in rows:
            try:
                m, d, y = r["date"].split("/")
                out[f"{y}-{m}-{d}"] = float(str(r["close"]).replace("$", "").replace(",", ""))
            except (ValueError, KeyError):
                pass
        if out:
            return {k: out[k] for k in sorted(out) if k <= asof}
    return {}


def ret(px: dict, asof: str, n: int):
    ds = [d for d in px if d <= asof]
    if len(ds) <= n or ds[-1] != asof:
        return None
    return px[ds[-1]] / px[ds[-1 - n]] - 1


def pct(x, d=1):
    return "—" if x is None else f"{x * 100:+.{d}f}%"


def daily(px: dict) -> dict[str, float]:
    ds = sorted(px)
    return {ds[i]: px[ds[i]] / px[ds[i - 1]] - 1 for i in range(1, len(ds))}


def ols(y: dict, x: dict, end: str, n=250):
    ds = [d for d in sorted(set(y) & set(x)) if d <= end][-n:]
    if len(ds) < 60:
        return None
    ys, xs = [y[d] for d in ds], [x[d] for d in ds]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    vx = sum((a - mx) ** 2 for a in xs)
    b = sum((a - mx) * (c - my) for a, c in zip(xs, ys)) / vx
    a = my - b * mx
    res = [c - a - b * e for e, c in zip(xs, ys)]
    sr = math.sqrt(sum(r * r for r in res) / (len(res) - 2))
    vy = sum((c - my) ** 2 for c in ys)
    return {"beta": b, "alpha": a, "resid_sd": sr, "r2": 1 - sum(r * r for r in res) / vy, "n": len(ds), "from": ds[0], "to": ds[-1]}


def decompose(px_s: dict, px_m: dict, base: str, asof: str, fit: dict):
    rs, rm = daily(px_s), daily(px_m)
    win = [d for d in sorted(set(rs) & set(rm)) if base < d <= asof]
    if not win or base not in px_s:
        return None
    exp = 1.0
    for d in win:
        exp *= 1 + fit["beta"] * rm[d]
    act = px_s[asof] / px_s[base] - 1
    mkt = px_m[asof] / px_m[base] - 1
    band = fit["resid_sd"] * math.sqrt(len(win))
    res = act - (exp - 1)
    z = res / band if band else 0
    return {"days": len(win), "actual": act, "market": mkt, "expected": exp - 1, "resid": res, "band": band, "z": z,
            "verdict": "시장 동반 쪽(차이가 평소 흔들림 안)" if abs(z) <= 1 else "일부 고유 움직임(평소 흔들림의 1~2배)" if abs(z) <= 2 else "회사 고유 움직임이 큼(평소 흔들림의 2배 밖 — 회사 사건 확인)"}


# ---------- 거시 ----------
def treasury(asof: str):
    rows = []
    for y in sorted({int(asof[:4]) - 1, int(asof[:4])}):
        url = f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{y}/all?type=daily_treasury_yield_curve&field_tdr_date_value={y}&page&_format=csv"
        b = get(url)
        if b is None:
            need(f"미 국채 금리 {y}", f"curl -s -A 'Mozilla/5.0 research' '{url}'")
            continue
        for r in csv.DictReader(io.StringIO(b.decode("utf-8", "replace"))):
            try:
                m, d, yy = r["Date"].split("/")
                rows.append((f"{yy}-{m}-{d}", float(r["10 Yr"]), float(r["2 Yr"])))
            except (ValueError, KeyError):
                pass
    if rows:
        sources.append(("미 재무부 일별 국채 수익률 곡선(Daily Treasury Par Yield Curve Rates)", "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve"))
    rows = sorted(r for r in rows if r[0] <= asof)
    return rows


def h10(asof: str):
    url = "https://www.federalreserve.gov/datadownload/Output.aspx?rel=H10&series=122e3bcb627e8e53f1bf72a1a09cfb81&lastobs=60&from=&to=&filetype=csv&label=include&layout=seriescolumn"
    b = get(url)
    if b is None:
        need("연준 H.10 달러지수", f"curl -s -A 'Mozilla/5.0 research' '{url}'")
        return []
    out = []
    for line in b.decode("utf-8", "replace").splitlines():
        m = re.match(r"(\d{4}-\d\d-\d\d),([\d.]+)", line)
        if m and m.group(1) <= asof:
            out.append((m.group(1), float(m.group(2))))
    if out:
        sources.append(("연준 H.10 광의 달러지수(Nominal Broad Dollar Index, 1997년 1월=100, 주간 공표라 며칠 늦음)", "https://www.federalreserve.gov/releases/h10/"))
    return out


def wti(asof: str):
    url = "https://www.eia.gov/dnav/pet/hist_xls/RWTCd.xls"
    b = get(url, cache_h=12, name="RWTCd.xls")
    if b is None:
        need("EIA WTI 현물", f"curl -s -A 'Mozilla/5.0 research' '{url}'")
        return []
    try:
        import xlrd
    except ImportError:
        need("WTI 엑셀 읽기", "pip install xlrd")
        return []
    bk = xlrd.open_workbook(file_contents=b)
    sh = bk.sheet_by_name("Data 1")
    out = []
    for i in range(3, sh.nrows):
        r = sh.row_values(i)
        try:
            d = xlrd.xldate_as_datetime(r[0], bk.datemode).date().isoformat()
            if d <= asof and r[1] != "":
                out.append((d, float(r[1])))
        except (TypeError, ValueError):
            pass
    if out:
        sources.append(("EIA 서부텍사스유(WTI) 쿠싱 현물 일별(공표가 며칠 늦음)", "https://www.eia.gov/dnav/pet/hist/RWTCD.htm"))
    return out


def vix(asof: str):
    url = "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"
    b = get(url)
    if b is None:
        need("Cboe VIX", f"curl -sL -A 'Mozilla/5.0 research' '{url}'")
        return []
    out = []
    for line in b.decode("utf-8", "replace").splitlines()[1:]:
        p = line.split(",")
        try:
            m, d, y = p[0].split("/")
            k = f"{y}-{m}-{d}"
            if k <= asof:
                out.append((k, float(p[4])))
        except (ValueError, IndexError):
            pass
    if out:
        sources.append(("Cboe VIX 일별 종가(VIX_History.csv)", "https://www.cboe.com/tradable_products/vix/vix_historical_data/"))
    return out


def btc(asof: str):
    url = "https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=1440"
    b = get(url)
    if b is None:
        need("크라켄 비트코인", f"curl -s -A 'Mozilla/5.0 research' '{url}'")
        return []
    try:
        rows = list(json.loads(b)["result"].values())[0]
    except (ValueError, KeyError, IndexError):
        return []
    out = [(dt.datetime.utcfromtimestamp(r[0]).date().isoformat(), float(r[4])) for r in rows]
    out = [r for r in out if r[0] <= asof]
    if out:
        sources.append(("크라켄 XBT/USD 일봉(UTC 0시 마감)", "https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=1440"))
    return out


def chg(rows, n):
    if len(rows) <= n:
        return None
    return rows[-1][1] - rows[-1 - n][1], rows[-1 - n][0]


# ---------- 일정 ----------
MON = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], 1)}
MON3 = {k[:3]: v for k, v in MON.items()}


def fomc(asof: str):
    url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
    b = get(url, cache_h=24)
    if b is None:
        need("FOMC 일정", f"curl -s -A 'Mozilla/5.0 research' '{url}'")
        return []
    t = b.decode("utf-8", "replace")
    parts = re.split(r'<h4><a id="\d+">(\d{4}) FOMC Meetings</a></h4>', t)
    out = []
    for y, seg in zip(parts[1::2], parts[2::2]):
        for mo, dd in re.findall(r'fomc-meeting__month[^>]*>\s*<strong>([^<]+)</strong>.*?fomc-meeting__date[^>]*>([^<]+)<', seg, re.S):
            if "notation" in dd or "unscheduled" in dd.lower():
                continue
            mos = mo.split("/")
            m2 = re.match(r"(\d+)(?:-(\d+))?", dd.strip())
            if not m2 or mos[-1][:3] not in MON3:
                continue
            end = int(m2.group(2) or m2.group(1))
            mm = MON3[mos[-1][:3]]
            try:
                out.append((dt.date(int(y), mm, end).isoformat(), f"FOMC(연준 금리 회의) {mo} {dd.strip()} — 결정 발표는 마지막 날" + (" · 경제전망(점도표) 회의" if "*" in dd else "")))
            except ValueError:
                pass
    if out:
        sources.append(("연준 FOMC 회의 일정(공식)", url))
    return sorted(o for o in out if o[0] > asof)


def bea(asof: str):
    url = "https://www.bea.gov/news/schedule"
    b = get(url, cache_h=24)
    if b is None:
        need("BEA 일정", f"curl -s -A 'Mozilla/5.0 research' '{url}'")
        return []
    t = b.decode("utf-8", "replace")
    yr = re.search(r"Year (\d{4}) Release", re.sub(r"<[^>]+>", " ", t))
    y = int(yr.group(1)) if yr else int(asof[:4])
    out = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S):
        s = re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", " ", r))).strip()
        m = re.match(r"([A-Z][a-z]+) (\d{1,2}) .*?(GDP \([^)]*\)[^,]*|Personal Income and Outlays[^<]*)$", s)
        if m and m.group(1) in MON:
            d = dt.date(y, MON[m.group(1)], int(m.group(2))).isoformat()
            name = m.group(3).strip()
            ko = "개인소득·지출(PCE 물가 포함) " if name.startswith("Personal") else "국내총생산(GDP) "
            out.append((d, ko + name))
    if out:
        sources.append(("미 경제분석국(BEA) 발표 일정(공식)", url))
    return sorted(o for o in out if o[0] > asof)


def bls(asof: str):
    out = []
    for code, ko in (("cpi", "소비자물가(CPI)"), ("empsit", "고용 보고서(비농업 고용)")):
        url = f"https://www.bls.gov/schedule/news_release/{code}.htm"
        b = get(url, cache_h=24)
        if b is None:
            need(f"BLS {ko} 일정(403이면 운영자가 공식 페이지 날짜를 review/macro_calendar.md에 적거나 접근 허용)", f"curl -s -A 'Mozilla/5.0 research' '{url}'")
            out.append((None, f"{ko}: 확인 안 됨(BLS 공식 일정 페이지 접근 막힘)"))
            continue
        t = re.sub(r"<[^>]+>", " ", b.decode("utf-8", "replace"))
        got = []
        for mo, dd, yy in re.findall(r"([A-Z][a-z]{2})\.? (\d{1,2}), (\d{4})", t):
            if mo in MON3:
                d = dt.date(int(yy), MON3[mo], int(dd)).isoformat()
                if d > asof:
                    got.append(d)
        if got:
            out.append((min(got), ko))
            sources.append((f"BLS {ko} 발표 일정(공식)", url))
    # 운영자가 공식 페이지에서 옮겨 적은 일정(있으면) — review/macro_calendar.md '| YYYY-MM-DD | 이름 | 출처 URL |'
    cal = os.path.join(MEDIA, "review", "macro_calendar.md")
    if os.path.exists(cal):
        for d, nm, u in re.findall(r"^\|\s*(\d{4}-\d\d-\d\d)\s*\|\s*([^|]+?)\s*\|\s*(https?://\S+?)\s*\|", open(cal, encoding="utf-8").read(), re.M):
            if d > asof:
                out = [o for o in out if not (o[0] is None and nm.split("(")[0] in o[1])]
                out.append((d, f"{nm} (수기 표, 출처 {u})"))
    return out


# ---------- 정책 ----------
def sector_row(tk: str):
    p = os.path.join(MEDIA, "review", "sector_map.md")
    on = False
    for l in open(p, encoding="utf-8"):
        if l.startswith("## "):
            on = l.strip() == "## 표"; continue
        if on and l.startswith("|"):
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            if c and c[0] == tk and len(c) >= 8:
                sp = lambda s, sep: [x.strip() for x in s.split(sep) if x.strip() and x.strip() != "-"]
                return {"name": c[1], "sector": c[2], "etfs": sp(c[3], ","), "peers": sp(c[4], ","), "coin": c[5] if c[5] != "-" else "",
                        "fr": sp(c[6], ";"), "kw": sp(c[7], ";"), "note": c[8] if len(c) > 8 else ""}
    return None


def sec_annual(tk: str, kws: list[str]):
    b = get("https://www.sec.gov/files/company_tickers.json", UA_SEC, cache_h=168, name="sec_company_tickers.json")
    if b is None:
        need("SEC 티커 목록", "curl -s -A 'Mozilla/5.0 research admin@example.com' https://www.sec.gov/files/company_tickers.json")
        return None
    cik = next((v["cik_str"] for v in json.loads(b).values() if v["ticker"].upper() == tk), None)
    if not cik:
        return None
    s = get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json", UA_SEC, cache_h=12)
    if s is None:
        need("SEC 제출 목록", f"curl -s -A 'Mozilla/5.0 research admin@example.com' https://data.sec.gov/submissions/CIK{cik:010d}.json")
        return None
    rc = json.loads(s)["filings"]["recent"]
    hit = next(((f, d, a, p) for f, d, a, p in zip(rc["form"], rc["filingDate"], rc["accessionNumber"], rc["primaryDocument"]) if f in ("10-K", "20-F", "40-F")), None)
    if not hit:
        return {"form": None}
    f, d, acc, prim = hit
    url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{prim}"
    time.sleep(0.2)
    doc = get(url, UA_SEC, cache_h=168, timeout=60)
    if doc is None:
        need("SEC 연차 보고서", f"curl -s -A 'Mozilla/5.0 research admin@example.com' '{url}'")
        return {"form": f, "date": d, "url": url, "hits": None}
    txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", doc.decode("utf-8", "replace"))))
    # 위험 요인 구간(Item 1A ~ Item 1B/2)만 — 못 찾으면 전체
    starts = [m.start() for m in re.finditer(r"Item\s*1A\.?\s*Risk\s*Factors", txt, re.I)]
    if not starts:  # 20-F·40-F: 'Risk Factors' 제목 중 가장 긴 구간
        starts = [m.start() for m in re.finditer(r"Risk\s*Factors", txt)]
    seg = txt
    best = ""
    for st in starts:  # 목차·상호 참조가 아니라 실제 절 = 다음 Item 제목까지 가장 긴 구간
        en = re.search(r"Item\s*(1B|1C|2|4)\.?\s", txt[st + 50:], re.I)
        cand = txt[st: st + 50 + en.start()] if en else txt[st: st + 400000]
        if len(cand) > len(best):
            best = cand
    if len(best) > 5000:
        seg = best
    hits = []
    for k in kws:
        ms = list(re.finditer(re.escape(k), seg, re.I))
        if ms:
            i = ms[0].start()
            words = seg[max(0, i - 60): i + 80].split()[1:-1][:12]
            hits.append((k, len(ms), " ".join(words)))
        else:
            hits.append((k, 0, ""))
    sources.append((f"{tk} {f}(제출 {d}) 위험 요인", url))
    return {"form": f, "date": d, "url": url, "hits": hits, "risk_section": bool(starts)}


def fedreg(terms: list[str], asof: str):
    since = (dt.date.fromisoformat(asof) - dt.timedelta(days=180)).isoformat()
    out, seen = [], set()
    for t in terms:
        q = urllib.request.quote(f'"{t}"')
        url = (f"https://www.federalregister.gov/api/v1/documents.json?per_page=20&order=newest&conditions[term]={q}"
               f"&conditions[publication_date][gte]={since}&conditions[publication_date][lte]={asof}"
               "&conditions[type][]=RULE&conditions[type][]=PRORULE&conditions[type][]=PRESDOCU"
               "&fields[]=title&fields[]=publication_date&fields[]=html_url&fields[]=type&fields[]=agencies")
        b = get(url, cache_h=12)
        if b is None:
            need("Federal Register 검색", f"curl -s -g -A 'Mozilla/5.0 research' '{url}'")
            continue
        try:
            res = json.loads(b).get("results") or []
        except ValueError:
            res = []
        words = [w for w in re.findall(r"[A-Za-z0-9]+", t.lower()) if len(w) > 2]
        for r in res:
            if r["html_url"] in seen or not all(w in r["title"].lower() for w in words):  # 제목에 검색어가 다 있는 것만(본문 우연 일치 제외)
                continue
            seen.add(r["html_url"])
            ag = ", ".join(a.get("name") or a.get("raw_name", "") for a in (r.get("agencies") or [])[:2])
            out.append((r["publication_date"], r["type"], r["title"][:110], ag, r["html_url"], t))
    if out:
        sources.append(("Federal Register API(최근 180일 규칙·규칙안·대통령 문서)", "https://www.federalregister.gov/developers/documentation/api/v1"))
    return sorted(out, reverse=True)


# ---------- 기타 ----------
def prev_report(tk: str, asof: str):
    best = None
    for f in glob.glob(os.path.join(SITE, "content/reports/*.md")):
        t = open(f, encoding="utf-8").read(3000)
        if not re.search(rf"^ticker:\s*\"?{re.escape(tk)}\"?\s*$", t, re.M):
            continue
        m = re.search(r"^data_as_of:\s*\"?(\d{4}-\d\d-\d\d)", t, re.M)
        if m and m.group(1) < asof and (best is None or m.group(1) > best[0]):
            best = (m.group(1), os.path.basename(f)[:-3])
    return best


def core_list():
    try:
        from core_tickers import load
        return load()
    except Exception:
        return {}


def main():
    a = sys.argv[1:]
    if not a or a[0].startswith("-"):
        print(__doc__); sys.exit(1)
    tk = a[0].upper()
    opt = lambda k, dflt=None: a[a.index(k) + 1] if k in a else dflt
    asof = last_closed_day(opt("--date"))
    work = opt("--work", f"/home/claude/{tk.lower()}")
    mkt = opt("--mkt", "QQQ").upper()
    rdir = os.path.join(work, "research"); pdir = os.path.join(rdir, "macro_px")
    os.makedirs(pdir, exist_ok=True)
    row = sector_row(tk)
    warn = []
    if not row:
        warn.append(f"review/sector_map.md에 {tk} 없음 → 업종 ETF 대신 IWM, 정책 검색 생략. 표에 한 줄 추가할 것")
        row = {"name": tk, "sector": "미지정", "etfs": ["IWM"], "peers": [], "coin": "", "fr": [], "kw": ["tariff", "export control", "China"], "note": ""}
    frm = (dt.date.fromisoformat(asof) - dt.timedelta(days=430)).isoformat()
    PX = {}

    def load(sym):
        if sym not in PX:
            PX[sym] = nasdaq(sym, frm, asof)
            if PX[sym]:
                json.dump(PX[sym], open(os.path.join(pdir, f"{sym}.json"), "w"))
        return PX[sym]

    s = load(tk)
    if not s or max(s) != asof:
        last = max(s) if s else "없음"
        need(f"{tk} 기준일 {asof} 확정 종가(받은 마지막 날 {last})", f"curl -s -A 'Mozilla/5.0 research' 'https://api.nasdaq.com/api/quote/{tk}/historical?assetclass=stocks&fromdate={frm}&todate={asof}&limit=9999'")
        flush_need(tk)
        print(f"MACRO_STOP {tk} 시세 없음/기준일 불일치 → {NEED}"); sys.exit(2)
    sources.append((f"{SRC_NQ} — {tk}·ETF·비교 종목", f"https://api.nasdaq.com/api/quote/{tk}/historical?assetclass=stocks"))
    sec_etf = next((e for e in row["etfs"] if load(e) and max(PX[e]) == asof), None)
    if sec_etf is None:
        warn.append(f"업종 ETF {row['etfs']} 시세 없음 → IWM으로 대신")
        sec_etf = "IWM"; load("IWM")
    skipped = [e for e in row["etfs"][:row["etfs"].index(sec_etf)]] if sec_etf in row["etfs"] else []
    for e in skipped:
        warn.append(f"{e} 나스닥 API 시세 없음 → {sec_etf} 사용")
    # 사건 구간
    base = opt("--from")
    pr = prev_report(tk, asof)
    why = "--from 지정"
    sd = sorted(s)
    if not base:
        if pr and pr[0] in s and pr[0] < asof:
            base, why = pr[0], f"직전 리포트 {pr[1]} data_as_of"
        else:
            base, why = sd[-6], "직전 리포트 없음 → 5거래일"
    if base not in s:
        base = max(d for d in sd if d <= base)
    # 1 시황
    mk = ["SPY", "QQQ", "COMP", "IWM"]
    lines_mkt = []
    for sym in [tk] + mk + [sec_etf] + row["peers"]:
        p = load(sym)
        if not p:
            lines_mkt.append(f"| {ETF_NAME.get(sym, sym)} | 시세 없음 | | | | | |"); continue
        lab = ETF_NAME.get(sym, sym) + (" ← 업종 기준" if sym == sec_etf else " ← 이번 종목" if sym == tk else "")
        cl = p.get(asof)
        lines_mkt.append(f"| {lab} | {cl:,.2f} | {pct(ret(p, asof, 1))} | {pct(ret(p, asof, 5))} | {pct(ret(p, asof, 20))} | {pct(ret(p, asof, 252))} | {pct(p[asof] / p[base] - 1) if base in p and cl else '—'} |" if cl else f"| {lab} | 기준일 값 없음 | | | | | |")
    V = vix(asof)
    # 2 거시
    T = treasury(asof)
    D = h10(asof)
    W = wti(asof)
    B = btc(asof) if row["coin"] == "BTC" else []
    if row["coin"] == "BTC":
        load("IBIT")
    uup = load("UUP")
    # 3 분해
    rs = daily(s)
    fits, decs = {}, {}
    for ref in [mkt, sec_etf] + (["IBIT"] if row["coin"] == "BTC" and PX.get("IBIT") else []):
        p = load(ref)
        f = ols(rs, daily(p), base)
        if f:
            fits[ref] = f
            decs[ref] = decompose(s, p, base, asof, f)
    last_prev = sd[-2]
    lastday = {ref: decompose(s, PX[ref], last_prev, asof, f) for ref, f in fits.items()} if last_prev != base else {}
    # 4 일정
    cal = fomc(asof)[:2] + bea(asof)[:3]
    blsr = bls(asof)
    # 5 정책
    secr = None if "--no-policy" in a else sec_annual(tk, row["kw"])
    frr = [] if "--no-policy" in a else fedreg(row["fr"], asof)
    # 6 통섭
    peers_tab = []
    if "--no-peers" not in a:
        core = core_list()
        for c in core:
            if c == tk:
                continue
            p = load(c)
            if not p or asof not in p or base not in p:
                continue
            f = ols(daily(p), daily(PX[mkt]), base)
            if not f:
                continue
            dc = decompose(p, PX[mkt], base, asof, f)
            if dc:
                rp = prev_report(c, "9999-99-99")
                peers_tab.append((c, core[c], f["beta"], dc, rp[1] if rp else ""))
    # ----- 쓰기 -----
    nm = row["name"]
    o = [f"# {tk}({nm}) 시장·거시·정책 배경 — 기준일 {asof}({kd(asof)}) 확정 종가",
         f"만든 때 {dt.datetime.now().strftime('%Y-%m-%d %H:%M')} · 다시: `python3 tools/macro_ctx.py {tk} --date {asof} --from {base} --work {work}`",
         "", "> 쓰는 규칙(SKILL 3.6): 숫자는 이 파일·리포트에 있는 값만. 인과 단정('때문에')은 근거 자료가 있을 때만, 아니면 '같은 날 ~도 움직였다'. "
         "정책 연결은 아래 5절에서 채택한 것만. 투자 권유·전망 단정 금지.", ""]
    if warn:
        o += ["**경고**: " + " / ".join(warn), ""]
    o += [f"## 1. 시황 (종가 {kd(asof)} 기준, 출처 {SRC_NQ})", "",
          f"업종: {row['sector']} · 업종 기준 {ETF_NAME.get(sec_etf, sec_etf)}" + (f" · 비고 {row['note']}" if row["note"] else ""), "",
          f"| 대상 | 종가 | 1일 | 5일 | 20일 | 1년(252거래일) | 사건 구간 {kd(base)}→{kd(asof)} |", "|---|---|---|---|---|---|---|"] + lines_mkt
    if V:
        c5, c20 = chg(V, 5), chg(V, 20)
        o += ["", f"- VIX(변동성 지수) {V[-1][1]:.2f} ({kd(V[-1][0])}, Cboe) · 5거래일 전 대비 {c5[0]:+.2f}p · 20거래일 전 대비 {c20[0]:+.2f}p" if c5 and c20 else f"- VIX {V[-1][1]:.2f} ({V[-1][0]})"]
    else:
        o += ["", "- VIX: 확인 안 됨(원천 막힘)"]
    o += ["", "## 2. 거시", "", "| 지표 | 값(날짜) | 5회 전 대비 | 20회 전 대비 | 출처 |", "|---|---|---|---|---|"]
    if T:
        t10 = [(d, x) for d, x, _ in T]; t2 = [(d, y) for d, _, y in T]
        for lab, r in (("미 국채 10년 금리", t10), ("미 국채 2년 금리", t2)):
            c5, c20 = chg(r, 5), chg(r, 20)
            o.append(f"| {lab} | {r[-1][1]:.2f}% ({kd(r[-1][0])}) | {c5[0] * 100:+.0f}bp | {c20[0] * 100:+.0f}bp | 미 재무부 |")
        o.append(f"| 10년-2년 차이 | {(T[-1][1] - T[-1][2]) * 100:+.0f}bp ({kd(T[-1][0])}) | | | 계산 |")
    else:
        o.append("| 미 국채 금리 | 확인 안 됨 | | | 원천 막힘 |")
    if D:
        c5, c20 = chg(D, 5), chg(D, 20)
        o.append(f"| 광의 달러지수 | {D[-1][1]:.2f} ({kd(D[-1][0])}) | {c5[0] / D[-6][1] * 100:+.1f}% | {c20[0] / D[-21][1] * 100:+.1f}% | 연준 H.10(주간 공표, 늦음) |" if c5 and c20 else f"| 광의 달러지수 | {D[-1][1]:.2f} ({D[-1][0]}) | | | 연준 H.10 |")
    if uup and asof in uup:
        o.append(f"| 달러 강세 펀드(UUP) | {uup[asof]:.2f} ({kd(asof)}) | {pct(ret(uup, asof, 5))} | {pct(ret(uup, asof, 20))} | {SRC_NQ} |")
    if W:
        c5, c20 = chg(W, 5), chg(W, 20)
        o.append(f"| WTI 현물(배럴당) | {W[-1][1]:.2f}달러 ({kd(W[-1][0])}) | {c5[0] / W[-6][1] * 100:+.1f}% | {c20[0] / W[-21][1] * 100:+.1f}% | EIA(공표 늦음) |" if c5 and c20 else f"| WTI | {W[-1][1]} ({W[-1][0]}) | | | EIA |")
    else:
        o.append("| WTI | 확인 안 됨 | | | NEED.txt |")
    if B:
        c5, c20, c365 = chg(B, 5), chg(B, 20), chg(B, 365)
        o.append(f"| 비트코인(달러) | {B[-1][1]:,.0f} ({kd(B[-1][0])} UTC 일봉) | {c5[0] / B[-6][1] * 100:+.1f}%(5일) | {c20[0] / B[-21][1] * 100:+.1f}%(20일) | 크라켄 |" if c5 and c20 else "")
        if c365:
            o.append(f"| 비트코인 1년 | | | {c365[0] / B[-366][1] * 100:+.1f}%(365일) | 크라켄 |")
    o += ["", f"## 3. 시장 동반 분해 (사건 구간 {kd(base)} 종가 → {kd(asof)} 종가, 구간 근거: {why})", "",
          "베타(평소 민감도) = 구간 시작 전 250거래일 하루 수익률 회귀. 예상 = 날마다 베타 × 기준 수익률을 이어 붙임(절편 제외). "
          "평소 흔들림 = 회귀 나머지의 하루 표준편차 × √거래일.", "",
          "| 기준 | 베타 | 설명력 R² | 구간 기준 등락 | 예상 | 실제 | 차이(고유) | 평소 흔들림 | 판정 |", "|---|---|---|---|---|---|---|---|---|"]
    for ref, dc in decs.items():
        f = fits[ref]
        if dc:
            o.append(f"| {ETF_NAME.get(ref, ref)} | {f['beta']:.2f} | {f['r2']:.2f} | {pct(dc['market'])} | {pct(dc['expected'])} | {pct(dc['actual'])} | {dc['resid'] * 100:+.1f}%p | ±{dc['band'] * 100:.1f}%p | {dc['verdict']} |")
    for ref, dc in lastday.items():
        if dc:
            o.append(f"| {ETF_NAME.get(ref, ref)} · 마지막 하루 {kd(asof)} | {fits[ref]['beta']:.2f} | | {pct(dc['market'])} | {pct(dc['expected'])} | {pct(dc['actual'])} | {dc['resid'] * 100:+.1f}%p | ±{dc['band'] * 100:.1f}%p | {dc['verdict']} |")
    dm = decs.get(mkt)
    sent = ""
    if dm:
        f = fits[mkt]
        sent = (f"{kd(base)} 종가부터 {kd(asof)} 종가까지 {dm['days']}거래일 동안 {josa(nm, '은', '는')} {dm['actual'] * 100:+.1f}%였습니다. "
                f"같은 기간 {josa(ETF_NAME.get(mkt, mkt), '은', '는')} {dm['market'] * 100:+.1f}%였고, 평소 민감도(약 {f['beta']:.1f}배)로 예상한 움직임은 {dm['expected'] * 100:+.1f}%였습니다. "
                f"차이는 {dm['resid'] * 100:+.1f}%p로, 평소 {dm['days']}거래일 흔들림(±{dm['band'] * 100:.1f}%p) {'안' if abs(dm['z']) <= 1 else '밖'}입니다.")
        o += ["", "**한 문장 초안(리포트·대본, 숫자는 위 표 그대로)**: " + sent]
        ds = decs.get(sec_etf)
        if ds and sec_etf != mkt:
            o.append(f"- 업종 기준: 같은 구간 {ETF_NAME.get(sec_etf, sec_etf)} {ds['market'] * 100:+.1f}%, 업종 민감도 약 {fits[sec_etf]['beta']:.1f}배로 예상 {ds['expected'] * 100:+.1f}% → 차이 {ds['resid'] * 100:+.1f}%p({ds['verdict']}).")
    o += ["", "## 4. 다음 거시 일정 (공식 일정 페이지 날짜만)", "", "| 날짜 | 일정 |", "|---|---|"]
    for d, n_ in sorted([c for c in cal] + [b for b in blsr if b[0]]):
        o.append(f"| {d}({kd(d)}) | {n_} |")
    for d, n_ in blsr:
        if d is None:
            o.append(f"| 확인 안 됨 | {n_} |")
    o += ["", "## 5. 지정학·정책 (사업과 직접 연결되는 것만)", ""]
    if secr and secr.get("hits") is not None:
        o += [f"최신 연차 보고서: {secr['form']} 제출 {secr['date']} ({'위험 요인 절' if secr.get('risk_section') else '본문 전체(위험 요인 절 못 찾음)'}) {secr['url']}", "",
              "| 키워드 | 횟수 | 첫 구절(12단어 이하) |", "|---|---|---|"]
        for k, n_, sn in secr["hits"]:
            o.append(f"| {k} | {n_} | {sn.replace('|', '/')} |")
    elif secr and secr.get("form") is None:
        o.append("연차 보고서(10-K·20-F·40-F) 없음 — 회사 위험 요인 대조 불가")
    elif "--no-policy" not in a:
        o.append("연차 보고서: 확인 안 됨(원천 막힘, NEED.txt)")
    if not frr and "--no-policy" not in a:
        o += ["", f"Federal Register: 최근 180일 제목에 검색어({'; '.join(row['fr'])})가 든 규칙·규칙안·대통령 문서 없음"]
    if frr:
        o += ["", "Federal Register 후보(최근 180일 규칙·규칙안·대통령 문서, 검색어 일치일 뿐 — 채택 전 10-K 위험 요인과 대조):", "",
              "| 게재일 | 종류 | 제목 | 기관 | 검색어 |", "|---|---|---|---|---|"]
        for d, ty, ti, ag, u, t in frr[:10]:
            o.append(f"| {d} | {ty} | [{ti.replace('|', '/')}]({u}) | {ag} | {t} |")
    o += ["", "**채택(에이전트가 채우거나 그대로 둔다)**: 직접 연결 확인 안 됨",
          "- 채택 형식: `YYYY-MM-DD · 무엇(1차 출처 URL) · 연결 고리: 회사 10-K '…' 항목/매출 비중` 한 줄. 연결 근거가 없으면 위 줄을 그대로 둔다(억지 연결 금지)."]
    o += ["", f"## 6. 통섭: 같은 구간 핵심 종목 (시장 기준 {ETF_NAME.get(mkt, mkt)}, {kd(base)}→{kd(asof)})", ""]
    if peers_tab:
        inb = sum(1 for p in peers_tab if abs(p[3]["z"]) <= 1)
        o += ["| 종목 | 베타 | 실제 | 예상 | 차이 | 판정 | 최근 리포트 |", "|---|---|---|---|---|---|---|"]
        for c, n_, b_, dc, sl in peers_tab:
            o.append(f"| {n_}({c}) | {b_:.2f} | {pct(dc['actual'])} | {pct(dc['expected'])} | {dc['resid'] * 100:+.1f}%p | {dc['verdict'].split('(')[0]} | {('/r/' + sl + '/') if sl else ''} |")
        o += ["", f"**기저율 한 문장 초안**: 같은 {decs[mkt]['days'] if dm else ''}거래일 동안 핵심 종목 {len(peers_tab)}개 가운데 {inb}개는 평소 시장 민감도로 예상한 범위 안에서 움직였습니다."]
    else:
        o.append("핵심 종목 비교 없음(--no-peers 또는 시세 없음)")
    # 그림 초안
    figs = {"slug": "<slug>", "asof": asof, "source": "나스닥 일별 종가", "figs": [
        {"n": 3, "type": "relative", "base": base, "to": asof,
         "title": [f"{nm}·업종·시장, {kd(base)} 종가 = 100"], "sub": "같은 기간 함께 움직였는지 보세요",
         "series": [{"name": nm, "data": {"file": f"../research/macro_px/{tk}.json"}},
                    {"name": ETF_NAME.get(sec_etf, sec_etf).split("(")[0], "data": {"file": f"../research/macro_px/{sec_etf}.json"}},
                    {"name": ETF_NAME.get(mkt, mkt).split("(")[0], "data": {"file": f"../research/macro_px/{mkt}.json"}}]}]}
    if dm:
        items = [{"label": nm, "sub": "평소 민감도로 예상", "value": round(dm["expected"] * 100, 1), "text": f"{dm['expected'] * 100:+.1f}%"},
                 {"label": nm, "sub": "실제", "value": round(dm["actual"] * 100, 1), "text": f"{dm['actual'] * 100:+.1f}%", "hi": True}]
        figs["figs"].append({"n": 4, "type": "compare", "title": ["평소 민감도로 예상한 움직임과 실제"], "sub": f"{kd(base)} → {kd(asof)}, 기준 {ETF_NAME.get(mkt, mkt)}", "items": items, "unit": "%"})
    json.dump(figs, open(os.path.join(rdir, "macro_figs.json"), "w"), ensure_ascii=False, indent=1)
    o += ["", "## 7. 그림 초안", "", f"`{rdir}/macro_figs.json` — figkit 형식(relative: 종목·업종·시장 누적 등락, compare: 예상 vs 실제). "
          "번호(n)·slug를 리포트에 맞게 고치고 figs.json에 합친다. 그림 숫자는 리포트 본문·부록에 먼저 넣는다(easy_check 대조)."]
    o += ["", "## 출처(접속 " + dt.date.today().isoformat() + ")", ""] + [f"- {t} | {u}" for t, u in dict.fromkeys(sources)]
    if needs:
        o += ["", "## 막힌 원천(NEED.txt)", ""] + needs
    open(os.path.join(rdir, "macro.md"), "w", encoding="utf-8").write("\n".join(x for x in o if x is not None) + "\n")
    js = {"ticker": tk, "asof": asof, "base": base, "base_why": why, "mkt": mkt, "sector_etf": sec_etf,
          "fits": fits, "decomp": decs, "lastday": lastday, "sentence": sent,
          "rates": {"t10": T[-1][1] if T else None, "t2": T[-1][2] if T else None, "date": T[-1][0] if T else None},
          "vix": V[-1] if V else None, "dollar_h10": D[-1] if D else None, "wti": W[-1] if W else None, "btc": B[-1] if B else None,
          "calendar": sorted([c for c in cal] + [b for b in blsr if b[0]]), "needs": needs}
    json.dump(js, open(os.path.join(rdir, "macro.json"), "w"), ensure_ascii=False, indent=1)
    flush_need(tk)
    print(f"MACRO_OK {tk} 기준일 {asof} 구간 {base}→{asof} → {rdir}/macro.md" + (f" (막힘 {len(needs)}건 → {NEED})" if needs else ""))
    if sent:
        print(sent)


def flush_need(tk):
    if not needs:
        return
    os.makedirs(os.path.dirname(NEED), exist_ok=True)
    have = open(NEED, encoding="utf-8").read() if os.path.exists(NEED) else ""
    new = [n for n in needs if n not in have]  # 같은 막힘은 한 번만
    if new:
        with open(NEED, "a", encoding="utf-8") as f:
            f.write(f"\n# {dt.datetime.now().strftime('%Y-%m-%d %H:%M')} macro_ctx.py {tk} — 막힌 원천(우회하지 않음). 열리면 아래 명령으로 확인 후 다시 실행\n" + "\n".join(new) + "\n")


if __name__ == "__main__":
    main()
