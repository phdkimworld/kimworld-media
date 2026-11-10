#!/usr/bin/env python3
"""실시간 인기 종목(StockTwits trending) — MSI 대체(운영자 지시 2026-11-10 "이걸로 대체하고. 요청 없을때 호출해서.
후보는 그때 그때 실시간 랭킹 가져와서 판단해").

요청 큐가 비었을 때 제작 점검이 요청 슬롯 후보를 고를 때만 부른다(매일 예약 실행 없음).
사용: python3 tools/trending.py [--top 30]
출력: 순위 | 티커 | 이름 | 점수 | 구분 | 사이트 리포트(최신 slug·기준일 또는 '없음')
구분: 주식 / 코인(.X) / ETF·펀드(제외 권장)
"""
import json, re, sys, glob, os, urllib.request
SITE = os.environ.get("KW_SITE", "/home/user/kimworld-site")
top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 30
d = json.load(urllib.request.urlopen(urllib.request.Request(
    "https://api.stocktwits.com/api/2/trending/symbols.json", headers={"User-Agent": "Mozilla/5.0 research"}), timeout=30))
reports = {}
for f in glob.glob(f"{SITE}/content/reports/*.md"):
    h = open(f, encoding="utf-8").read(1500)
    t = re.search(r"^ticker:\s*(\S+)", h, re.M); a = re.search(r"^data_as_of:\s*(\S+)", h, re.M)
    if t:
        k = t.group(1).upper()
        if k not in reports or (a and a.group(1) > reports[k][1]): reports[k] = (os.path.basename(f)[:-3], a.group(1) if a else "")
ETF = re.compile(r"\bETF\b|Fund|Trust|ProShares|iShares|Direxion|T-REX|2X|3X|Daily Target|Leveraged|Inverse", re.I)
print("순위 | 티커 | 이름 | 점수 | 구분 | 사이트 리포트")
for i, s in enumerate(d.get("symbols", [])[:top], 1):
    sym = s["symbol"]; title = (s.get("title") or "")[:34]
    kind = "코인" if sym.endswith(".X") or s.get("exchange") == "CRYPTO" else ("ETF·펀드(제외)" if ETF.search(title) or s.get("exchange") == "NYSEArca" else "주식")
    key = sym[:-2] if sym.endswith(".X") else sym
    r = reports.get(key.upper())
    print(f"{i} | {sym} | {title} | {s.get('trending_score', 0):.1f} | {kind} | {r[0] + ' (' + r[1] + ')' if r else '없음'}")
