#!/usr/bin/env python3
"""핵심 종목 표(review/core_tickers.md, 제작팀 권고안 R1·R4 2026-11-16)를 읽는 공용 도구.
사용:
  python3 tools/core_tickers.py              # 핵심 종목과 시리즈 이름
  python3 tools/core_tickers.py --prev LAES  # 그 종목 지난 편(사이트 리포트 youtube_id) — 설명란 첫머리 '지난 편' 링크용(R4)
모듈: from core_tickers import load, mark, series_title, prev_episode
"""
import os, re, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__)); MEDIA = os.path.dirname(HERE)
SITE = os.environ.get("KW_SITE", os.path.join(os.path.dirname(MEDIA), "kimworld-site"))
PATH = os.path.join(MEDIA, "review", "core_tickers.md")


def load(path=PATH):
    """{티커: 시리즈 이름}. '## 목록' 아래 첫 표만 읽는다."""
    out, on = {}, False
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
    except OSError:
        return out
    for l in lines:
        if l.startswith("## "):
            if on: break
            on = l.strip() == "## 목록"; continue
        if not on or not l.startswith("|"): continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) >= 2 and re.fullmatch(r"[A-Z0-9.]{1,8}", c[0]): out[c[0]] = c[1]
    return out


def mark(tk, core=None):
    core = load() if core is None else core
    return "★" if str(tk).upper() in core else ""


def series_title(tk, core=None):
    core = load() if core is None else core
    n = core.get(str(tk).upper())
    return f"{n} 미스터리 추적" if n else None


def ticker_from_title(title):
    m = re.search(r"\(([A-Z][A-Z0-9.]{0,7})\)", title or "")
    return m.group(1) if m else None


def prev_episode(tk):
    """그 종목 사이트 리포트 가운데 youtube_id가 있는 가장 최근 것: (slug, data_as_of, youtube_id) 또는 None."""
    best = None
    for f in glob.glob(os.path.join(SITE, "content/reports/*.md")):
        t = open(f, encoding="utf-8").read(4000)
        k = re.search(r"^ticker:\s*['\"]?([^'\"\s]+)", t, re.M)
        if not k or k.group(1).upper() != tk.upper(): continue
        y = re.search(r"^youtube_id:\s*['\"]?([\w-]{6,})", t, re.M)
        d = re.search(r"^data_as_of:\s*['\"]?(\d{4}-\d\d-\d\d)", t, re.M)
        if not y: continue
        row = (d.group(1) if d else "", os.path.basename(f)[:-3], y.group(1))
        if best is None or row > best: best = row
    return (best[1], best[0], best[2]) if best else None


if __name__ == "__main__":
    core = load()
    if "--prev" in sys.argv:
        tk = sys.argv[sys.argv.index("--prev") + 1].upper()
        p = prev_episode(tk)
        print(f"{tk}{mark(tk, core)} 지난 편: " + (f"{p[1]} {p[0]} https://youtu.be/{p[2]}" if p else "없음")
              + (f" · 재생목록 '{series_title(tk, core)}'" if tk in core else " · 핵심 종목 아님(재생목록 없음)"))
    else:
        print("핵심 종목: " + " · ".join(f"{k}({v})" for k, v in core.items()))
