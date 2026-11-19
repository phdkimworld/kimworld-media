#!/usr/bin/env python3
"""예측 장부(운영자 지시 2026-11-18: "종목별로 예측 성과를 트랙킹하면서 더 나은 예측을 할 수 있도록 통찰을 기록해 나가").
장부: review/predictions/ledger.jsonl (한 줄 = 예측 하나, id = slug + 문장 해시 → 다시 돌려도 중복 없음)
사용:
  python3 tools/pred_ledger.py --extract            # 사이트 리포트 전체에서 시나리오(가능성 %)·핵심 확인 항목을 뽑아 장부에 더함(판정 기록은 보존)
  python3 tools/pred_ledger.py --judge [--quiet]    # 판정일이 지난 가격 조건을 나스닥 종가로, 조달 서류는 SEC EDGAR로 자동 판정
  python3 tools/pred_ledger.py --report [--ticker T]  # 적중률·브라이어·확률 구간 보정·유형별 성적(짧은 표)
  python3 tools/pred_ledger.py --pending [--ticker T] # 사람 판정이 필요한 항목 id 목록
  python3 tools/pred_ledger.py --set ID 1|0 "근거"   # 사람 판정(일어남 1 · 안 일어남 0). 'x'면 판정 불가
  python3 tools/pred_ledger.py --score SLUG         # 그 리포트보다 앞선 같은 종목 리포트의 예측 성적(후속편 '지난 예측 성적' 줄과 대조용)
  python3 tools/pred_ledger.py --daily              # prod_check용: 하루 첫 실행 때만 extract+judge, 새 판정이 있으면 한 줄
판정 규칙(README.md에 같은 설명):
  - 시나리오는 가격 부분(종가 비교)과 사건 부분(발표·계약·조달)으로 나눈다. 모든 부분이 참이면 일어남, 하나라도 거짓이면 안 일어남.
    가격 부분이 거짓이면 사건 부분을 몰라도 자동으로 '안 일어남'. 사건 부분이 남으면 '사람 판정 필요'.
  - 적중은 '콜' 단위: 합이 100%인 시나리오 묶음은 가장 높은 시나리오 하나가 일어났는지, 겹치는 시나리오는 50% 이상=일어난다·미만=안 일어난다.
  - 브라이어 점수와 보정은 확률이 있는 모든 시나리오로 계산. 확인 항목(확률 없음)은 기저율에만 쓴다.
"""
import os, re, sys, json, glob, hashlib, datetime, urllib.request, time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__)); MEDIA = os.path.dirname(HERE)
SITE = os.environ.get("KW_SITE", os.path.join(os.path.dirname(MEDIA), "kimworld-site"))
PD = os.path.join(MEDIA, "review", "predictions"); LEDGER = os.path.join(PD, "ledger.jsonl")
CACHE = os.path.expanduser("~/.cache/kimworld/pred"); os.makedirs(CACHE, exist_ok=True)
TODAY = datetime.datetime.now(ZoneInfo("America/New_York")).date()
UA_NQ = {"User-Agent": "Mozilla/5.0 research", "Accept": "application/json"}
UA_SEC = {"User-Agent": "kimworld-research admin@example.com"}

DATE = re.compile(r"(?:(\d{4})년\s*)?(\d{1,2})월\s*(\d{1,2})일")
PRICE = re.compile(r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*달러")
UP = r"위|넘|높|이상|회복|돌파|지키|지킴|유지|웃돌"; DN = r"아래|밑|낮|미만|이탈|깨|밑돌"
FIN = re.compile(r"증자|조달|주식 판매|새 주식|주식 공급|공모|전환사채|424B|S-3|F-3|S-1|F-1|ATM|시장 판매|발행|판매 재개|판매 멈|판매 확인|판매 공시|무발행|무증자")
NEG = re.compile(r"없음|없이|없다|무증자|무발행|멈춤|멈추|안 나|×")


def norm(s): return re.sub(r"\s+", " ", re.sub(r"<br>|\*\*|\[|\]", " ", s)).strip()


def kdate(m, base):
    y = int(m.group(1)) if m.group(1) else base.year
    mo, d = int(m.group(2)), int(m.group(3))
    if not m.group(1) and mo < base.month - 2: y += 1
    try: return datetime.date(y, mo, d)
    except ValueError: return None


def dates_in(s, base):
    s = re.sub(r"(?:(\d{4})년\s*)?(\d{1,2})월\s*(\d{1,2})일\s*[·~]\s*(\d{1,2})일", lambda m: f"{m.group(0)[:m.group(0).rfind(m.group(4))]}{m.group(2)}월 {m.group(4)}일", s)  # '11월 6일·19일' → '…·11월 19일'
    return [x for x in (kdate(m, base) for m in DATE.finditer(s)) if x]


def prob_of(s):
    m = re.search(r"약\s*(\d{1,3})\s*%", s)
    if m: return int(m.group(1))
    m = re.search(r"(\d{1,3})\s*~\s*(\d{1,3})\s*%", s)
    if m: return (int(m.group(1)) + int(m.group(2))) / 2
    m = re.search(r"(\d{1,3})\s*%", s)
    return int(m.group(1)) if m else None


def fm(txt, k):
    m = re.search(rf"^{k}:\s*['\"]?([^'\"\n]+)", txt, re.M); return m.group(1).strip() if m else ""


# ---------- 조건 해석 ----------
def price_comps(s, base, ipo=None):
    """문장에서 가격 조건들: [{lv, dir, ref?, mode, date?}]"""
    out = []; t = re.sub(r"\([^)]{0,12}\)", "", s)  # '1.03달러(계산) 아래' → 괄호 짧은 덧말 제거
    rg = re.search(r"(\d+(?:\.\d+)?)\s*~\s*(\d+(?:\.\d+)?)\s*달러", t)
    if rg and not re.search(r"달러\s*(?:" + UP + "|" + DN + ")", t[rg.end() - 2:rg.end() + 8]):  # '18.03~21.64달러(사이)'
        return [{"lv": float(rg.group(1)), "dir": "up", "mode": "close"}, {"lv": float(rg.group(2)), "dir": "dn", "mode": "close"}]
    for m in PRICE.finditer(t):
        tail = t[m.end():m.end() + 14]; head = t[max(0, m.start() - 30):m.start()]
        d = "up" if re.match(rf"\s*(?:보다\s*|를\s*|을\s*|선\s*|선을\s*)?(?:{UP})", tail) else "dn" if re.match(rf"\s*(?:보다\s*|를\s*|을\s*|선\s*|선을\s*)?(?:{DN})", tail) else None
        if not d: continue
        lv = float(m.group(1).replace(",", ""))
        dm = list(DATE.finditer(head)); jd = None
        if dm and "종가" in head[dm[-1].end():]: jd = kdate(dm[-1], base)
        if jd and jd <= base: jd = None  # '10월 16일 종가 0.5068달러'는 기준값 설명이지 판정일이 아님
        win = re.search(r"까지|한 번이라도|새 저점|새 최저|돌파|깨", head + tail)
        out.append({"lv": lv, "dir": d, "mode": "touch" if win and not jd else "close", **({"date": jd.isoformat()} if jd else {})})
    if not out:  # 'N월 D일 종가 아래로' 같은 날짜 종가 기준
        for m in re.finditer(r"(?:(\d{4})년\s*)?(\d{1,2})월\s*(\d{1,2})일\s*종가\s*(?:보다\s*)?(" + UP + "|" + DN + ")", t):
            rd = kdate(m, base)
            if rd and rd <= base: out.append({"ref": rd.isoformat(), "dir": "up" if re.match(UP, m.group(4)) else "dn", "mode": "close"})
        m = re.search(r"공모가\s*[:·]?\s*(위|유지|지킴|아래|이탈)", t)
        if m and ipo: out.append({"lv": ipo, "dir": "up" if m.group(1) in ("위", "유지", "지킴") else "dn", "mode": "close", "ref_name": "공모가"})
    return out


def comps_of(header_cells, cells, base, ipo):
    """표 행 → 부분 조건. 머리 '주문 · 종가' + 칸 '주문 공개 · 1.145달러 위'를 짝지어 나눈다."""
    parts = []
    for h, c in zip(header_cells, cells):
        hs = [x.strip() for x in re.split(r"\s*[·/]\s*", norm(h)) if x.strip()]
        cs = [x.strip() for x in re.split(r"\s*[·/]\s*", norm(c)) if x.strip()]
        if len(hs) == len(cs) and len(hs) > 1: parts += [f"{a} {b}" for a, b in zip(hs, cs)]
        elif len(cs) > 1: parts += cs  # 머리가 '판정 조건' 하나뿐이면 칸을 나눠 각각 조건으로
        else: parts.append(f"{norm(h)} {norm(c)}")
    return parts


def build(text, parts, base, ipo, strict=(), price_only=(), first=None):
    """parts 가운데 strict(표의 조건 칸 짝)는 해석 못 해도 사건 조건으로 남긴다(빠뜨리면 가격 부분만으로 '일어남' 오판). price_only는 가격만 본다."""
    comps = []
    for i, p in enumerate(parts):
        if re.match(r"\s*(업종|비트코인|QS|본드|아이온큐|오클로|네비우스|QQQ|ETF|지수|이더리움)", p) and i in strict:  # 다른 자산의 가격 축
            comps.append({"event": p[:60], "neg": False}); continue
        fd = re.match(r"(?:첫날|다음 날)\S*\s+(상승|하락|반등|오름|내림)", p)
        if fd and first: comps.append({"first_day": "up" if fd.group(1) in ("상승", "반등", "오름") else "dn", "date": first}); continue
        pc = price_comps(p, base, ipo)
        if pc:
            comps += [c for c in pc if c not in comps]; continue
        if i in price_only: continue
        core = re.sub(r"^(시나리오\s*\d+|\d)\s*·\s*", "", p).strip()
        if not core or not re.search(r"[가-힣A-Za-z]", core): continue
        if i in strict and not FIN.search(core) and not re.search(r"발표|공시|계약|주문|합작|승인|인수|수주|가이던스|전망|목표|서명|개시|인증|선정|허가|공개|발주|실적|보고서|매출|현금|유동성", core):
            comps.append({"event": core[:60], "neg": bool(NEG.search(core))}); continue
        if FIN.search(core):
            neg = bool(NEG.search(core)) ^ bool(re.search(r"무증자|무발행", core) and "×" in core)
            if re.search(r"무증자|무발행", core) and "○" in core: neg = True
            comps.append({"event": core[:60], "fin": True, "neg": neg})
        elif re.search(r"발표|공시|계약|주문|합작|승인|인수|수주|가이던스|전망|목표|서명|개시|인증|선정|허가|공개|발주|실적|보고서|매출|현금|유동성", core):
            comps.append({"event": core[:60], "neg": bool(NEG.search(core))})
    return comps


def kind_of(text, comps):
    """유형(하나). 종목 횡단 기저율의 단위라서 이름을 바꾸면 README 표도 같이 바꾼다."""
    t = text; ps = [c for c in comps if "dir" in c]
    if any("first_day" in c for c in comps) or re.search(r"첫날|다음 날", t): return "실적·사건 첫 반응"
    if FIN.search(t): return "자금 조달"
    if ps:
        cash = re.search(r"공모가|현금|유동성|주당", t) or any(c.get("ref_name") for c in ps)
        if ps[0]["dir"] == "dn": return "현금·공모가선 이탈" if cash else "판정선 이탈·추가 하락"
        if cash: return "현금·공모가선 위"
        if re.search(r"반등|되돌|회복|돌아", t): return "반등·회복"
        return "판정선 유지·위"
    if re.search(r"실적|보고서|분기|매출|가이던스|전망", t): return "실적·보고서 숫자"
    if re.search(r"계약|주문|합작|수주|승인|허가|인수|서명|발주|선정", t): return "계약·사업 발표"
    if re.search(r"업종|금리|시장|비트코인|오클로|네비우스|아이온큐", t): return "업종·시장 동조"
    return "기타"


# ---------- 추출 ----------
def extract_report(path):
    txt = open(path, encoding="utf-8").read(); slug = os.path.basename(path)[:-3]
    tk = fm(txt, "ticker").upper(); pub = fm(txt, "date"); aso = fm(txt, "data_as_of") or pub
    if not tk or not aso: return []
    base = datetime.date.fromisoformat(aso[:10])
    ipo_m = re.search(r"공모(?:가|는|가는)?\s*(?:가격\s*)?(\d+(?:\.\d+)?)\s*달러", txt); ipo = float(ipo_m.group(1)) if ipo_m else None
    out = []
    def add(kind, name, prob, text, jd, comps, grp=None):
        t = norm(text); h = hashlib.sha1(re.sub(r"\s", "", norm(name)).encode()).hexdigest()[:8]
        out.append({"id": f"{slug}#{h}", "ticker": tk, "slug": slug, "published": pub, "as_of": aso, "kind": kind,
                    "type": kind_of(t, comps), "text": norm(name)[:160], "prob": prob, "judge_date": jd.isoformat() if jd else None,
                    "cond": comps, "group": grp, "sector": bool(re.search(r"업종|동반|양자주|원전주|함께 (?:하락|내림|오름|반등)", t)), "status": "대기", "outcome": None, "note": ""})
    m = re.search(r"^### (?:5\.6|[^\n]*앞으로 일어날).*?(?=^##|\Z)", txt, re.S | re.M)
    if m:
        sec = m.group(0); paras = [p for p in sec.split("\n\n")[1:] if p.strip()]
        sdate = None
        for p in paras[:3]:
            if re.search(r"추정|가능성", p) and not p.startswith("|"):
                ds = dates_in(p.split(". ")[0] if "까지" not in p else p, base)
                if ds: sdate = max(ds) if "판정" in p else ds[0]; break
        # 표 형식
        for t in re.findall(r"(?:^\|.*\n?)+", sec, re.M):
            ln = [l for l in t.strip().split("\n")]
            hdr = [c.strip() for c in ln[0].strip().strip("|").split("|")]
            pi = next((i for i, c in enumerate(hdr) if "가능성" in c), None)
            if pi is None: continue
            hd = dates_in(" ".join(hdr), base); hdate = max(hd) if hd else sdate
            di = next((i for i, c in enumerate(hdr) if "판정 날짜" in c), None)
            for r in ln[2:]:
                cs = [c.strip() for c in r.strip().strip("|").split("|")]
                if len(cs) != len(hdr): continue
                pr = prob_of(cs[pi])
                if pr is None: continue
                rd = dates_in(cs[di], base) if di is not None else []
                idx = [i for i in range(len(cs)) if i not in (pi, di)]
                name = " · ".join(norm(cs[i]) for i in idx[:1]) + (" | " + " · ".join(norm(cs[i]) for i in idx[1:2]) if len(idx) > 1 else "")
                cp = comps_of([hdr[i] for i in idx[1:2]], [cs[i] for i in idx[1:2]], base, ipo) if len(idx) > 1 else []
                parts = [norm(cs[0])] + cp
                comps = build(name, parts, base, ipo, strict=range(1, len(parts)), price_only=(0,) if cp else (), first=min(hd).isoformat() if len(hd) >= 2 else None)
                jd = max(rd) if rd else hdate
                cd = [c.get("date") for c in comps if c.get("date") and "first_day" not in c]
                if cd: jd = max(datetime.date.fromisoformat(x) for x in cd)
                add("scenario", name, pr, name, jd, comps, slug)
        # 글머리 형식 '**시나리오 N · …**' + '가능성(추정): 약 N%'
        for b in re.split(r"\n(?=(?:- )?\*\*시나리오\s*\d)", sec)[1:]:
            pl = re.search(r"가능성[^\n%]*?\d+\s*%[^\n]*", b)
            if not pl: continue
            title = re.match(r"(?:- )?\*\*(시나리오[^*]+)\*\*", b)
            if not title: continue
            name = norm(title.group(1)); pr = prob_of(pl.group(0))
            crit = " ".join(l for l in b.split("\n") if re.match(r"-\s*(지켜볼|판정|확인)", l))
            if b.startswith("- "): crit = b.split("\n")[0][title.end():]  # 한 줄 글머리형(10월 초)
            pnote = (re.search(r"\(([^)]*달러[^)]*)\)", pl.group(0)) or [None, ""])[1]
            parts = [name, crit, pnote]
            comps = build(name, parts, base, ipo, price_only=(1, 2))
            tds = dates_in(name, base); cd = [c.get("date") for c in comps if c.get("date")]
            jd = max(datetime.date.fromisoformat(x) for x in cd) if cd else (max(tds) if tds and "까지" in name else sdate)
            add("scenario", name + (" | " + norm(crit)[:80] if crit else ""), pr, name, jd, comps, slug)
    # 핵심 확인 표
    m2 = re.search(r"^### [^\n]*핵심 확인.*?(?=^##|\Z)", txt, re.S | re.M)
    if m2:
        for r in re.findall(r"^\|(?!\s*-)(.*)\|\s*$", m2.group(0), re.M)[1:]:
            cs = [c.strip() for c in r.split("|")]
            if len(cs) < 2: continue
            what = norm(re.sub(r"^\*\*\d순위\*\*<br>", "", cs[0])); rd = dates_in(cs[-1], base)
            comps = build(what, [what], base, ipo)
            cd = [c.get("date") for c in comps if c.get("date")]
            jd = max(datetime.date.fromisoformat(x) for x in cd) if cd else (max(rd) if rd else None)
            add("check", what, None, what, jd, comps)
    # 묶음: 합이 100%(90~110)이고 3개 이상이면 서로 겹치지 않는 묶음
    sc = [x for x in out if x["kind"] == "scenario"]
    tot = sum(x["prob"] for x in sc)
    for x in sc: x["group"] = slug if len(sc) >= 3 and 90 <= tot <= 110 else None
    seen = set(); res = []
    for x in out:
        if x["id"] in seen: continue
        seen.add(x["id"]); res.append(x)
    return res


def load():
    if not os.path.exists(LEDGER): return []
    return [json.loads(l) for l in open(LEDGER, encoding="utf-8") if l.strip()]


def save(rows):
    os.makedirs(PD, exist_ok=True)
    rows.sort(key=lambda r: (r["as_of"], r["slug"], r["id"]))
    with open(LEDGER, "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")


KEEP = ("status", "outcome", "note", "judged", "by", "price")


def do_extract():
    old = {r["id"]: r for r in load()}; new = []; add = 0
    for p in sorted(glob.glob(os.path.join(SITE, "content/reports/*.md"))):
        if os.path.basename(p).startswith("_"): continue
        for r in extract_report(p):
            o = old.get(r["id"])
            if o:
                for k in KEEP:
                    if k in o: r[k] = o[k]
            else: add += 1
            new.append(r)
    ids = {r["id"] for r in new}
    new += [o for i, o in old.items() if i not in ids and o.get("by") == "사람"]  # 사람 판정은 리포트가 바뀌어도 남김
    save(new); return add, len(new)


# ---------- 시세 ----------
_px = {}
def closes(tk):
    if tk in _px: return _px[tk]
    cf = os.path.join(CACHE, f"{tk}.json")
    if os.path.exists(cf) and time.time() - os.path.getmtime(cf) < 6 * 3600:
        _px[tk] = json.load(open(cf)); return _px[tk]
    d = {}
    url = f"https://api.nasdaq.com/api/quote/{tk}/historical?assetclass=stocks&fromdate=2026-09-01&todate={TODAY.isoformat()}&limit=400"
    try:
        j = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA_NQ), timeout=20))
        for r in ((j.get("data") or {}).get("tradesTable") or {}).get("rows") or []:
            mm, dd, yy = r["date"].split("/"); d[f"{yy}-{mm}-{dd}"] = float(r["close"].replace("$", "").replace(",", ""))
    except Exception: d = {}
    if d: json.dump(d, open(cf, "w"))
    _px[tk] = d; return d


_sec = {}
def fin_filings(tk):
    """SEC EDGAR 제출 목록에서 조달 서류(424B·S-1/3·F-1/3) [(날짜, 양식)]. 실패하면 None."""
    if tk in _sec: return _sec[tk]
    try:
        cf = os.path.join(CACHE, "sec_tickers.json")
        if not os.path.exists(cf) or time.time() - os.path.getmtime(cf) > 7 * 86400:
            open(cf, "wb").write(urllib.request.urlopen(urllib.request.Request("https://www.sec.gov/files/company_tickers.json", headers=UA_SEC), timeout=20).read())
        cik = next((v["cik_str"] for v in json.load(open(cf)).values() if v["ticker"].upper() == tk), None)
        if not cik: _sec[tk] = None; return None
        j = json.load(urllib.request.urlopen(urllib.request.Request(f"https://data.sec.gov/submissions/CIK{cik:010d}.json", headers=UA_SEC), timeout=20))
        rc = j["filings"]["recent"]
        _sec[tk] = [(d, f) for d, f in zip(rc["filingDate"], rc["form"]) if re.match(r"424B|S-1|S-3|F-1|F-3", f)]
        time.sleep(0.15)
    except Exception: _sec[tk] = None
    return _sec[tk]


def judge_price(c, tk, aso, jd):
    px = closes(tk)
    if not px: return None, "시세 없음"
    lv = c.get("lv")
    if lv is None and c.get("ref"):
        lv = px.get(c["ref"])
        if lv is None: return None, f"기준일 {c['ref']} 종가 없음"
    days = sorted(d for d in px if aso < d <= jd)
    last = max(px)
    hit = (lambda v: v > lv) if c["dir"] == "up" else (lambda v: v < lv)
    if c["mode"] == "touch":
        for d in days:
            if hit(px[d]): return 1, f"{d} {px[d]:g}"
        if last < jd: return "wait", ""
        return 0, f"{aso}~{jd} 종가 {min(px[d] for d in days):g}~{max(px[d] for d in days):g}" if days else (None, "구간 시세 없음")
    if last < jd: return "wait", ""
    on = [d for d in px if d <= jd]
    if not on: return None, "시세 없음"
    d = max(on); return (1 if hit(px[d]) else 0), f"{d} {px[d]:g} vs {lv:g}"


def judge_row(r):
    jd = r.get("judge_date"); tk = r["ticker"]; cs = r.get("cond") or []
    if not cs: return ("사람 판정 필요" if jd and jd < TODAY.isoformat() else "대기"), None, "조건 해석 안 됨"
    res, notes, unknown = [], [], False
    for c in cs:
        if "first_day" in c:  # 기준일 다음 첫 거래일 종가가 기준일 종가보다 위/아래
            px = closes(tk)  # 머리의 첫 판정일 종가 vs 그 전 거래일 종가
            if not px: res.append(None); unknown = True; continue
            on = sorted(d for d in px if d >= c["date"]); pv = sorted(d for d in px if d < c["date"])
            if not on: res.append("wait"); continue
            if not pv: res.append(None); unknown = True; continue
            up = px[on[0]] > px[pv[-1]]; res.append(1 if up == (c["first_day"] == "up") else 0)
            notes.append(f"첫날 {on[0]} {px[on[0]]:g} vs {pv[-1]} {px[pv[-1]]:g}"); continue
        if "dir" in c:
            d = c.get("date") or jd
            if not d: res.append(None); unknown = True; continue
            v, n = judge_price(c, tk, r["as_of"], d)
            if v == "wait": res.append("wait"); continue
            if v is None: unknown = True
            res.append(v); notes.append(n)
        elif c.get("fin") and jd:
            fl = fin_filings(tk)
            if fl is None: res.append(None); continue
            shelf_ok = bool(re.search(r"S-3|F-3|등록|선반", c["event"]))  # S-3·F-3는 판매 한도 등록이라 실제 판매가 아님
            got = [f"{d} {f}" for d, f in fl if r["as_of"] < d <= jd and (re.match(r"424B|S-1|F-1", f) or shelf_ok)]
            if got: res.append(0 if c["neg"] else 1); notes.append("EDGAR " + ",".join(got[:2]))
            elif jd < TODAY.isoformat() and re.search(r"공시|서류|발표|424B|S-3|F-3|공모|전환사채|새 주식|무증자|무발행", c["event"]):
                res.append(1 if c["neg"] else 0); notes.append("EDGAR 조달 서류 없음")
            else: res.append("wait" if jd >= TODAY.isoformat() else None)
        else: res.append("wait" if jd and jd >= TODAY.isoformat() else None)
    if 0 in res: return "판정 끝", 0, "; ".join(n for n in notes if n)
    if all(v == 1 for v in res): return "판정 끝", 1, "; ".join(notes)
    if "wait" in res: return "대기", None, "; ".join(n for n in notes if n)
    if unknown and all(("dir" in c or "first_day" in c) for c in cs): return "판정 불가", None, "; ".join(n for n in notes if n)
    return "사람 판정 필요", None, "; ".join(n for n in notes if n)


def settle(rows):
    """outcome → 적중/빗나감 표기(콜 단위)."""
    groups = {}
    for r in rows:
        if r["kind"] == "scenario" and r.get("group"): groups.setdefault(r["group"], []).append(r)
    top = {g: max(v, key=lambda x: x["prob"])["id"] for g, v in groups.items()}
    for r in rows:
        if r["outcome"] is None or r["status"] in ("대기", "사람 판정 필요", "판정 불가"): continue
        if r["kind"] == "check": r["status"] = "일어남" if r["outcome"] else "안 일어남"
        elif r.get("group"):
            r["status"] = ("적중" if r["outcome"] else "빗나감") if r["id"] == top[r["group"]] else ("일어남(보조)" if r["outcome"] else "안 일어남(보조)")
        # 묶음 없는 시나리오: 50% 이상으로 둔 것만 '콜'(적중/빗나감). 50% 미만은 콜이 아니라 보조(11-18: 35%로 둔 SMR '증권사 하향 연쇄'가 실제로 일어났는데 빗나감으로 세던 오류)
        elif (r.get("prob") or 0) >= 50: r["status"] = "적중" if r["outcome"] == 1 else "빗나감"
        else: r["status"] = "일어남(보조)" if r["outcome"] else "안 일어남(보조)"


def do_judge(quiet=False):
    rows = load(); newly = {}
    for r in rows:
        if r.get("by") == "사람" or r["outcome"] is not None: continue
        if r["status"] == "판정 불가" and r.get("judged") == TODAY.isoformat(): continue
        st, oc, note = judge_row(r)
        if st == "판정 끝":
            r["outcome"], r["status"], r["note"], r["by"], r["judged"] = oc, st, note, "자동", TODAY.isoformat()
            newly.setdefault(r["ticker"], []).append(r)
        else:
            r["status"] = st; r["note"] = note or r.get("note", ""); r["judged"] = TODAY.isoformat()
    settle(rows); save(rows)
    if newly:
        s = " · ".join(f"{t} {len(v)}" for t, v in sorted(newly.items()))
        print(f"예측 장부: 새 판정 {sum(map(len, newly.values()))}건({s}) — 그 종목 후속편 때 review/predictions/<T>.md에 한 줄")
    elif not quiet: print("예측 장부: 새 판정 없음")
    return newly


# ---------- 성적 ----------
def stats(rows):
    sc = [r for r in rows if r["kind"] == "scenario" and r["outcome"] is not None]
    calls = [r for r in sc if r["status"] in ("적중", "빗나감")]
    hit = sum(r["status"] == "적중" for r in calls)
    br = sum((r["prob"] / 100 - r["outcome"]) ** 2 for r in sc) / len(sc) if sc else None
    return sc, calls, hit, br


def table(rows, title):
    sc, calls, hit, br = stats(rows)
    cnt = {}
    for r in rows: cnt[r["status"]] = cnt.get(r["status"], 0) + 1
    done = sum(v for k, v in cnt.items() if k not in ("대기", "사람 판정 필요", "판정 불가"))
    print(f"{title}: 예측 {len(rows)}(시나리오 {sum(r['kind']=='scenario' for r in rows)}·확인 {sum(r['kind']=='check' for r in rows)}) "
          f"판정 끝 {done} · 사람 판정 필요 {cnt.get('사람 판정 필요',0)} · 대기 {cnt.get('대기',0)} · 판정 불가 {cnt.get('판정 불가',0)}")
    if calls: print(f"적중(콜) {hit}/{len(calls)}={hit/len(calls):.0%} · 브라이어 {br:.3f}(n={len(sc)}, 모두 50%면 0.250)")
    if sc:
        print("| 구간 | 말한 평균 | 실제 | n |")
        for lo in range(0, 100, 20):
            b = [r for r in sc if lo <= r["prob"] < lo + 20 or (lo == 80 and r["prob"] == 100)]
            if b: print(f"| {lo}~{lo+20}% | {sum(r['prob'] for r in b)/len(b):.0f}% | {sum(r['outcome'] for r in b)/len(b):.0%} ({sum(r['outcome'] for r in b)}/{len(b)}) | {len(b)} |")
    j = [r for r in rows if r["outcome"] is not None]
    if j:
        print("| 유형 | 종목 | 판정 | 일어남(기저율) | 말한 평균 | 브라이어 |")
        groups = [(t, [r for r in j if r["type"] == t]) for t in sorted({r["type"] for r in j})]
        groups.append(("(태그) 업종 동반 언급", [r for r in j if r.get("sector")]))
        for t, b in groups:
            if not b: continue
            bp = [r for r in b if r["prob"] is not None]
            print(f"| {t} | {len({r['ticker'] for r in b})} | {len(b)} | {sum(r['outcome'] for r in b)}/{len(b)}={sum(r['outcome'] for r in b)/len(b):.0%} | "
                  + (f"{sum(r['prob'] for r in bp)/len(bp):.0f}% | {sum((r['prob']/100-r['outcome'])**2 for r in bp)/len(bp):.3f} |" if bp else "- | - |"))


def do_report(tk=None, sync=True):
    rows = load()
    if tk:
        rows = [r for r in rows if r["ticker"] == tk.upper()]; table(rows, f"{tk.upper()} 예측 장부")
        pend = [r for r in rows if r["status"] == "사람 판정 필요"]
        if pend: print(f"사람 판정 필요 {len(pend)}: " + "; ".join(f"{r['id']} {r['text'][:30]}" for r in pend[:6]) + (" …" if len(pend) > 6 else ""))
        nxt = sorted((r for r in rows if r["status"] == "대기" and r["judge_date"]), key=lambda r: r["judge_date"])[:3]
        if nxt: print("다음 판정: " + "; ".join(f"{r['judge_date'][5:]} {r['text'][:30]}" for r in nxt))
    else:
        table(rows, "전체(통합) 예측 장부")
        sc_all = [r for r in rows if r["kind"] == "scenario" and r["outcome"] is not None]
        gap = (sum(r["outcome"] for r in sc_all) / len(sc_all) - sum(r["prob"] for r in sc_all) / len(sc_all) / 100) if sc_all else 0
        print(f"| 종목 | 예측 | 판정 끝 | 적중(콜) | 브라이어 | 실제-말한(%p) | 전체({gap*100:+.0f}%p)와 |")
        for t in sorted({r["ticker"] for r in rows}):
            b = [r for r in rows if r["ticker"] == t]; sc, calls, hit, br = stats(b)
            nd = sum(r["outcome"] is not None for r in b)
            if not nd: continue
            g = (sum(r["outcome"] for r in sc) / len(sc) - sum(r["prob"] for r in sc) / len(sc) / 100) if sc else None
            flag = "" if g is None or len(sc) < 2 else ("어긋남(과소평가)" if g - gap > 0.15 else "어긋남(과대평가)" if g - gap < -0.15 else "비슷")
            print(f"| {t} | {len(b)} | {nd} | {hit}/{len(calls)} | " + (f"{br:.3f} | {g*100:+.0f} | {flag} |" if br is not None else "- | - | - |"))
    if sync: sync_auto(tk)


def sync_auto(tk=None):
    """통찰 파일의 '<!-- AUTO:장부 -->' ~ '<!-- /AUTO -->' 사이를 장부 표로 바꾼다(숫자를 장부와 맞추려고). 손으로 쓴 부분은 건드리지 않는다."""
    import io, contextlib
    f = os.path.join(PD, f"{tk.upper()}.md" if tk else "README.md")
    if not os.path.exists(f): return
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): do_report(tk, sync=False)
    t = open(f, encoding="utf-8").read()
    n = re.sub(r"(<!-- AUTO:장부 -->\n).*?(<!-- /AUTO -->)", lambda m: m.group(1) + f"({TODAY:%m-%d} `pred_ledger.py --report{' --ticker ' + tk.upper() if tk else ''}`가 쓴 칸)\n\n" + buf.getvalue() + m.group(2), t, flags=re.S)
    if n != t: open(f, "w", encoding="utf-8").write(n)


def do_score(slug):
    rows = load(); me = [r for r in rows if r["slug"] == slug]
    tk = me[0]["ticker"] if me else re.sub(r"-\d{4}-\d\d(-\d+)?$", "", slug).upper()
    aso = me[0]["as_of"] if me else TODAY.isoformat()
    prev = [r for r in rows if r["ticker"] == tk and r["as_of"] < aso and r["slug"] != slug]
    if not prev: print(f"SCORE {slug}: 앞선 예측 없음"); return None
    last = max(r["slug"] for r in prev if r["as_of"] == max(x["as_of"] for x in prev))
    b = [r for r in prev if r["slug"] == last]
    h = sum(r["status"] in ("적중", "일어남") for r in b); m = sum(r["status"] in ("빗나감", "안 일어남") for r in b)
    w = sum(r["status"] in ("대기", "사람 판정 필요") for r in b)
    print(f"SCORE {slug} ← {last}: 적중·일어남 {h} · 빗나감·안 일어남 {m} · 진행 중 {w} (보조 시나리오 제외, 판정 불가 {sum(r['status']=='판정 불가' for r in b)})")
    return h, m, w


def do_set(i, v, note):
    rows = load(); hit = [r for r in rows if r["id"] == i or r["id"].startswith(i)]
    if len(hit) != 1: print(f"id {i}: {len(hit)}개 일치"); sys.exit(1)
    r = hit[0]
    if v == "x": r.update(status="판정 불가", outcome=None)
    else: r.update(outcome=int(v), status="판정 끝")
    r.update(note=note, by="사람", judged=TODAY.isoformat()); settle(rows); save(rows)
    print(f"{r['id']} → {r['status']} ({note})")


if __name__ == "__main__":
    a = sys.argv[1:]
    tk = a[a.index("--ticker") + 1] if "--ticker" in a else None
    if "--daily" in a:
        st = os.path.join(CACHE, "daily_stamp")
        if os.path.exists(st) and open(st).read().strip() == TODAY.isoformat(): sys.exit(0)
        open(st, "w").write(TODAY.isoformat()); do_extract(); do_judge(quiet=True); sys.exit(0)
    if "--extract" in a:
        n, t = do_extract(); print(f"예측 장부 추출: 새 {n} · 전체 {t}")
    if "--set" in a:
        i = a.index("--set"); do_set(a[i + 1], a[i + 2], " ".join(a[i + 3:]))
    if "--judge" in a: do_judge("--quiet" in a)
    if "--report" in a: do_report(tk)
    if "--pending" in a:
        for r in load():
            if r["status"] == "사람 판정 필요" and (not tk or r["ticker"] == tk.upper()):
                print(f"{r['id']} | {r['judge_date']} | {r['prob'] if r['prob'] is not None else '-'} | {r['text'][:70]} | {r.get('note','')[:40]}")
    if "--score" in a: do_score(a[a.index("--score") + 1])
