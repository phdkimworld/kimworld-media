"""figkit — 리포트 본문 그림(피겨) 여러 장을 JSON 명세 하나로 만든다(운영자 지시 2026-11-15 ET "리포트 줄글로 쓰는 대신 피겨를 더 넣어서 이해를 도와줘").

사용: python3 tools/figkit/make.py <figs.json> <out_dir> [--site <사이트 폴더>] [--png]
  → 그림마다 <out_dir>/<slug>-<n>.webp(정지 이미지: 다크 바탕, 가로 1200px, Noto Sans KR)와 <slug>-<n>.json(명세).
    --site 면 사이트 static/charts/(WebP)·static/figs/(명세)에 바로 복사, --png 면 예전 흰 바탕 PNG 도 낸다.
  한 명세, 세 출력(운영자 지시 2026-11-16 ET "애니메이션을 리포트에서 렌더링 되게"): 명세 = 그 그림 하나짜리 figkit 문서
    (시세는 쓰인 구간만 [[날짜, 종가]]로 안에 넣음) + 영상 anim 틀 {tpl, data} + 웹 그리기 목록 web(1200 기준 좌표, 움직임 묶음 g).
    리포트 웹 애니메이션(사이트 static/js/fig/fig.js)·영상 클립(slidekit anim.py fromfig <명세> <n>)·정지 이미지(명세를 이 도구에 다시 넣음).
  색은 chart_dark.INK 일곱 가지만(흰 판: 글자 #0E1A2B, 설명 #5E6B7D, 막대 #C9D1DB, 강조 #E0A21B, 강조 숫자 #B07B0C, 기준선 #4F7FB8, 주석 #7F8A99 / 다크 판은 그 오른쪽 색).
  원고에는 ![캡션 — 무엇을 보면 되는지](/static/charts/<slug>-<n>.webp). 그림 안 숫자는 리포트 본문·부록 숫자만(easy_check 가 명세와 대조).

명세:
{"slug": "smr-2026-11-2", "asof": "2026-11-13", "source": "나스닥 일별 종가",   # source·asof 는 그림마다 덮어쓸 수 있음
 "figs": [
  {"n": 1, "type": "compare", "title": ["제목 1~2줄"], "sub": "한 줄 설명(선택)",
   "items": [{"label": "뉴스케일", "sub": "11월 6일", "value": 16.2, "text": "+16.2%", "hi": true}], "unit": "%"},
  {"n": 2, "type": "price_events", "series": {"file": "SMR.json", "from": "2026-10-01", "to": "2026-11-13"} | [["2026-11-05", 4.37], ...],
   "events": [{"date": "2026-11-05", "label": "실적 발표일 4.37달러"}], "ref": {"v": 4.34, "label": "한 주당 현금 4.34달러"}, "unit": "달러"},
  {"n": 3, "type": "relative", "base": "2026-11-05", "to": "2026-11-13",
   "series": [{"name": "뉴스케일", "data": {"file": "SMR.json"}}, {"name": "오클로", "data": {"file": "OKLO.json"}}]},
  {"n": 4, "type": "record", "items": [{"label": "2024.10.28", "sub": "+19.5%", "value": 64.1, "hi": true}, {"label": "이번", "value": null, "text": "12월 4일 판정"}]},
  {"n": 5, "type": "scenarios", "decision": "판정: 12월 4일 종가 · 기준선 4.37달러",
   "items": [{"label": "업종 바람에 실린 버팀", "sub": "4.37달러 위 · 오클로보다 못함", "p": 40, "range": [35, 45], "hi": true}]},
  {"n": 6, "type": "trend", "items": [{"label": "1분기", "value": 120.5, "text": "1억 2,050만"}], "ref": {"v": 100, "label": "…"}}
 ]}
공통 선택 키: "note"(맨 아래 주석, 기준일 앞), "file"(출력 파일 이름), "decimals", "unit"("%"·"달러"·"원"·"" 등).
시계열 파일은 나스닥 JSON, {"d":[],"c":[]}, [{"d","c"}], {"날짜": 종가}, [[날짜, 종가]] 를 읽는다(명세 파일 기준 상대 경로 가능).
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

# chart_dark.INK 와 같은 색만(다크 변환이 이 색을 기준으로 진하기를 거꾸로 구한다)
TXT, SUB, BAR, HI, HIT, REF, NOTE = "#0E1A2B", "#5E6B7D", "#C9D1DB", "#E0A21B", "#B07B0C", "#4F7FB8", "#7F8A99"
BG, KNOCK = "#FFFFFF", "#FFFFFF"  # 바탕, 사건 번호 동그라미 안 숫자(흰 바탕 판에서는 바탕색)
# 다크 판(사이트 검은 바탕, chart_dark.INK 의 오른쪽 색과 같다): 정지 WebP·웹 애니메이션이 같은 색을 쓴다
LIGHT = dict(TXT="#0E1A2B", SUB="#5E6B7D", BAR="#C9D1DB", HI="#E0A21B", HIT="#B07B0C", REF="#4F7FB8", NOTE="#7F8A99", BG="#FFFFFF", KNOCK="#FFFFFF")
DARK = dict(TXT="#F2F4F7", SUB="#9AA5B4", BAR="#3B4554", HI="#F0B23A", HIT="#F5BC4A", REF="#7FA8DE", NOTE="#8C96A5", BG="#000000", KNOCK="#000000")


def set_palette(dark: bool) -> None:
    globals().update(DARK if dark else LIGHT)
W, S, PAD = 1200, 2, 56
FONT_DIRS = ["/usr/share/fonts/truetype/notokr/", "/usr/share/fonts/opentype/noto/"]


def _font(weight: str, size: int):
    names = {"bold": ["NotoSansKR_700Bold.ttf", "NotoSansCJK-Bold.ttc"], "reg": ["NotoSansKR_400Regular.ttf", "NotoSansCJK-Regular.ttc"]}[weight]
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size * S, index=1 if p.endswith(".ttc") else 0)
    raise SystemExit("Noto Sans KR 글꼴이 없습니다(apt-get install fonts-noto-cjk)")


_FC: dict = {}


def F(weight: str, size: int):
    k = (weight, size)
    if k not in _FC:
        _FC[k] = _font(weight, size)
        _FK[id(_FC[k])] = k
    return _FC[k]


_FK: dict = {}  # 글꼴 객체 → (굵기, 크기): 웹 그리기 목록에 적는다


class Canvas:
    """1200px 기준 좌표로 그리고 2배로 칠한 뒤 줄인다(글자·선 가장자리 매끈하게)."""

    def __init__(self, h: int):
        self.h = h
        self.img = Image.new("RGB", (W * S, h * S), BG)
        self.d = ImageDraw.Draw(self.img)
        # 웹 애니메이션용 그리기 목록(1200px 좌표). g = 움직임 묶음(None: 처음부터 보임, 정수: 항목 차례, "line"·"end"·"ref"·"e<k>": 선 그래프)
        self.ops: list = []
        self.g = None
        self.gx: dict = {}

    def _op(self, **o):
        if self.g is not None:
            o["g"] = self.g
        self.ops.append(o)

    def text(self, x, y, t, f, col=None, anchor="la"):
        col = col or TXT
        t = str(t)
        self.d.text((x * S, y * S), t, font=f, fill=col, anchor=anchor)
        if t.strip():
            # 웹은 글자 기준선(baseline)으로 옮긴다: 기준점 anchor 의 글자 위끝 = 기준선 기준 글자 위끝
            base = y + (f.getbbox(t, anchor=anchor)[1] - f.getbbox(t, anchor="ls")[1]) / S
            wt, sz = _FK.get(id(f), ("reg", round(f.size / S)))
            self._op(k="t", x=round(x, 1), y=round(base, 1), a={"l": "s", "m": "m", "r": "e"}[anchor[0]], b=1 if wt == "bold" else 0,
                     s=sz, c=col, t=t, w=round(self.tw(t, f), 1))

    def tw(self, t, f) -> float:
        return self.d.textlength(str(t), font=f) / S

    def line(self, pts, col, w=2, dash=0):
        self._op(k="l", p=[round(v, 1) for xy in pts for v in xy], c=col, w=w, **({"d": dash} if dash else {}))
        pts = [(x * S, y * S) for x, y in pts]
        if not dash:
            self.d.line(pts, fill=col, width=int(w * S), joint="curve")
            return
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            L = math.hypot(x1 - x0, y1 - y0)
            n = max(1, int(L / (dash * S * 2)))
            for i in range(n):
                a, b = i / n, (i + 0.5) / n
                self.d.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)], fill=col, width=int(w * S))

    def rect(self, x0, y0, x1, y1, col, r=6):
        # 웹: (x0, y0) 쪽이 막대의 뿌리(0 기준선) — 그 자리에서 (x1, y1) 쪽으로 자란다
        self._op(k="r", x0=round(x0, 1), y0=round(y0, 1), x1=round(x1, 1), y1=round(y1, 1), c=col, r=r)
        if x1 < x0:
            x0, x1 = x1, x0
        if y1 < y0:
            y0, y1 = y1, y0
        r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
        self.d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=max(0, r) * S, fill=col)

    def dot(self, x, y, r, col, outline=None, w=0):
        self._op(k="c", x=round(x, 1), y=round(y, 1), r=r, c=col)
        self.d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=col, outline=outline, width=int(w * S))

    def save(self, path):
        im = self.img.resize((W, self.h), Image.LANCZOS)
        if path.endswith(".webp"):
            im.save(path, "WEBP", quality=82, method=6)
        else:
            im.save(path, optimize=True)

    def web(self) -> dict:
        return {"w": W, "h": self.h, "ops": self.ops, **({"gx": self.gx} if self.gx else {})}


def wrap(c: Canvas, t: str, f, maxw: float) -> list[str]:
    """띄어쓰기 단위로 줄을 나눈다(한국어 문장은 어절 단위로)."""
    out, cur = [], ""
    for word in str(t).split(" "):
        nxt = (cur + " " + word).strip()
        if cur and c.tw(nxt, f) > maxw:
            out.append(cur)
            cur = word
        else:
            cur = nxt
    if cur:
        out.append(cur)
    return out or [""]


# ---------- 숫자 표기 ----------
def fmt(v, unit="", dec=None, sign=False) -> str:
    if v is None:
        return ""
    if dec is None:
        dec = 0 if abs(v) >= 1000 or (unit == "원" and abs(v) >= 100) else (2 if unit == "달러" else 1 if abs(v) >= 10 or unit == "%" else 2)
    s = f"{abs(v):,.{dec}f}"
    pre = ("+" if v > 0 else "-" if v < 0 else "") if sign else ("-" if v < 0 else "")
    return pre + s + unit


def nice_ticks(lo, hi, n=5):
    if hi <= lo:
        hi = lo + 1
    raw = (hi - lo) / n
    mag = 10 ** math.floor(math.log10(raw))
    step = min((m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw), default=10 * mag)
    a = math.floor(lo / step) * step
    ticks = []
    v = a
    while v <= hi + step * 0.001:
        ticks.append(round(v, 10))
        v += step
    if ticks[-1] < hi:
        ticks.append(ticks[-1] + step)
    return ticks, step


# ---------- 시계열 읽기 ----------
def _d(s: str) -> str:
    s = str(s)
    if "/" in s:
        m, d, y = s.split("/")
        return f"{y}-{int(m):02d}-{int(d):02d}"
    return s[:10]


def _num(v) -> float:
    return float(str(v).replace("$", "").replace(",", ""))


def load_series(spec, base_dir: str) -> list[tuple[str, float]]:
    """[[날짜, 값]] 목록 또는 {"file", "from", "to"} → 날짜순 [(YYYY-MM-DD, 값)]."""
    if isinstance(spec, list):
        rows = [(_d(a), float(b)) for a, b in spec]
        lo = hi = None
    else:
        p = spec["file"]
        p = p if os.path.isabs(p) else os.path.join(base_dir, p)
        raw = json.load(open(p, encoding="utf-8"))
        if isinstance(raw, dict) and "data" in raw:  # 나스닥
            rows = [(_d(r["date"]), _num(r["close"])) for r in raw["data"]["tradesTable"]["rows"] if r.get("close") not in (None, "", "N/A")]
        elif isinstance(raw, dict) and "d" in raw and "c" in raw:
            rows = [(_d(a), float(b)) for a, b in zip(raw["d"], raw["c"])]
        elif isinstance(raw, dict):
            rows = [(_d(a), _num(b)) for a, b in raw.items()]
        elif raw and isinstance(raw[0], dict):
            k = "c" if "c" in raw[0] else "close" if "close" in raw[0] else "trade_price"
            kd = "d" if "d" in raw[0] else "date" if "date" in raw[0] else "candle_date_time_kst"
            rows = [(_d(r[kd]), _num(r[k])) for r in raw]
        else:
            rows = [(_d(a), _num(b)) for a, b in raw]
        lo, hi = spec.get("from"), spec.get("to")
    rows = sorted(dict(rows).items())
    if lo:
        rows = [r for r in rows if r[0] >= lo]
    if hi:
        rows = [r for r in rows if r[0] <= hi]
    if not rows:
        raise SystemExit(f"시계열이 비었습니다: {spec}")
    return rows


# ---------- 공통 머리·꼬리 ----------
def header_h(c: Canvas, fig) -> int:
    y = 40
    for line in fig["title"][:2]:
        y += 58 * len(wrap(c, line, F("bold", 42), W - 2 * PAD))
    if fig.get("sub"):
        y += 44 * len(wrap(c, fig["sub"], F("reg", 29), W - 2 * PAD))
    if fig.get("decision"):
        y += 48
    return y + 20


def draw_header(c: Canvas, fig) -> None:
    y = 40
    for i, line in enumerate(fig["title"][:2]):
        for ln in wrap(c, line, F("bold", 42), W - 2 * PAD):
            c.text(PAD, y, ln, F("bold", 42), TXT)
            y += 58
    if fig.get("sub"):
        for ln in wrap(c, fig["sub"], F("reg", 29), W - 2 * PAD):
            c.text(PAD, y + 2, ln, F("reg", 29), SUB)
            y += 44
    if fig.get("decision"):
        c.rect(PAD, y + 8, PAD + 8, y + 40, REF, r=2)
        c.text(PAD + 22, y + 6, fig["decision"], F("bold", 29), REF)


def _foot_text(fig, doc) -> str:
    parts = [fig.get("note") or fig.get("source") or doc.get("source") or ""]
    asof = fig.get("asof") or doc.get("asof")
    if asof:
        parts.append(f"기준일 {asof}")
    return " · ".join(p for p in parts if p)


def foot_h(fig, doc) -> int:
    return 40 + 32 * len(wrap(Canvas(10), _foot_text(fig, doc), F("reg", 24), W - 2 * PAD)[:3])


def draw_footer(c: Canvas, fig, doc) -> None:
    fh = foot_h(fig, doc)
    c.line([(PAD, c.h - fh + 4), (W - PAD, c.h - fh + 4)], BAR, 2)
    for i, ln in enumerate(wrap(c, _foot_text(fig, doc), F("reg", 24), W - 2 * PAD)[:3]):
        c.text(PAD, c.h - fh + 18 + i * 32, ln, F("reg", 24), NOTE)


# ---------- 가로 막대(compare·record·scenarios 공용) ----------
def hbars(fig, doc, kind: str) -> Canvas:
    items = fig["items"]
    unit = fig.get("unit", "%" if kind != "compare" else "")
    dec = fig.get("decimals")
    probe = Canvas(10)
    fl, fs, fv = F("bold", 30 if kind != "record" else 28), F("reg", 25), F("bold", 32 if kind != "record" else 29)
    labw = min(W * 0.42, max(max(probe.tw(it["label"], fl) for it in items), max((probe.tw(it.get("sub", ""), fs) for it in items), default=0)) + 24)
    has_sub = any(it.get("sub") for it in items)
    rowh = fig.get("row_h") or ((92 if has_sub else 70) if kind != "record" else (74 if has_sub else 56))
    if kind == "scenarios":
        vals = [it["p"] for it in items]
        top_v = max(max(it.get("range", [0, it["p"]])[1] for it in items), 1)
        vmin, vmax = 0.0, top_v * 1.08
    else:
        vals = [it.get("value") for it in items if it.get("value") is not None]
        vmin, vmax = min(0.0, min(vals)), max(0.0, max(vals))
        if fig.get("clip"):  # 한 값이 너무 커서 나머지가 안 보이면 막대만 자르고 숫자는 그대로(끝에 // 표시)
            vmin, vmax = max(vmin, -fig["clip"]), min(vmax, fig["clip"])
        if vmax == vmin:
            vmax = vmin + 1
    texts = []
    for it in items:
        if kind == "scenarios":
            texts.append(it.get("text") or f"약 {it['p']:g}%")
        elif it.get("value") is None:
            texts.append(it.get("text", ""))
        else:
            texts.append(it.get("text") or fmt(it["value"], unit, dec, sign=(unit == "%")))
    def _tw(sign):
        return max([probe.tw(t, fv) for t, it in zip(texts, items)
                    if kind == "scenarios" or (it.get("value") is not None and (it["value"] < 0) == (sign < 0))] + [0]) + 18
    x0 = PAD + labw
    x1 = W - PAD
    neg = vmin < 0
    left_room = _tw(-1) if neg else 0
    right_room = _tw(1) if vmax > 0 else 0
    span = (x1 - right_room) - (x0 + left_room)
    zx = x0 + left_room + span * (-vmin) / (vmax - vmin)
    X = lambda v: zx + span * v / (vmax - vmin)
    hh = header_h(probe, fig)
    top = hh + 14
    c = Canvas(int(top + rowh * len(items) + 24 + foot_h(fig, doc) + (40 if fig.get("axis_note") else 0)))
    draw_header(c, fig)
    if neg or kind == "record":
        c.line([(zx, top - 6), (zx, top + rowh * len(items))], NOTE, 2)
    for i, (it, t) in enumerate(zip(items, texts)):
        c.g = i
        y = top + i * rowh
        hi = it.get("hi")
        cy = y + (rowh / 2 if not it.get("sub") else rowh / 2)
        # 라벨
        if it.get("sub") and not str(it["label"]).strip():  # 짝 줄(같은 기간 비교 등): 설명만 가운데에
            c.text(PAD, cy, it["sub"], fs, SUB, anchor="lm")
        elif it.get("sub"):
            c.text(PAD, cy - 4, it["label"], fl, TXT, anchor="ls")
            c.text(PAD, cy + 4, it["sub"], fs, SUB, anchor="lt")
        else:
            c.text(PAD, cy, it["label"], fl, TXT, anchor="lm")
        bh = min(40, rowh * 0.55)
        col = HI if hi else BAR
        if kind == "scenarios":
            p = it["p"]
            c.rect(X(0), cy - bh / 2, X(p), cy + bh / 2, col, r=6)
            if it.get("range"):
                a, b = it["range"]
                c.line([(X(a), cy), (X(b), cy)], TXT, 3)
                c.line([(X(a), cy - 12), (X(a), cy + 12)], TXT, 3)
                c.line([(X(b), cy - 12), (X(b), cy + 12)], TXT, 3)
            tx = max(X(p), X(it["range"][1]) if it.get("range") else 0) + 14
            c.text(tx, cy, t, fv, HIT if hi else TXT, anchor="lm")
            continue
        v = it.get("value")
        if v is None:
            fp = F("bold", 27)
            if zx + 14 + c.tw(t, fp) > W - PAD:
                c.text(zx - 14, cy, t, fp, NOTE, anchor="rm")
            else:
                c.text(zx + 14, cy, t, fp, NOTE, anchor="lm")
            continue
        vb = min(max(v, vmin), vmax)
        c.rect(zx, cy - bh / 2, X(vb), cy + bh / 2, col, r=6)
        if vb != v:  # 잘린 막대: 끝에 두 줄 빗금
            for dx in (-14, -4):
                xx = X(vb) + (dx if v > 0 else -dx)
                c.line([(xx - 5, cy + bh / 2 + 4), (xx + 5, cy - bh / 2 - 4)], KNOCK, 4)
        if v >= 0:
            c.text(X(vb) + 12, cy, t, fv, HIT if hi else TXT, anchor="lm")
        else:
            c.text(X(vb) - 12, cy, t, fv, HIT if hi else TXT, anchor="rm")
    c.g = None
    if fig.get("axis_note"):
        c.text(PAD, top + rowh * len(items) + 14, fig["axis_note"], F("reg", 25), SUB)
    draw_footer(c, fig, doc)
    return c


# ---------- 세로 막대 추이(trend) ----------
def trend(fig, doc) -> Canvas:
    items = fig["items"]
    unit, dec = fig.get("unit", ""), fig.get("decimals")
    probe = Canvas(10)
    hh = header_h(probe, fig)
    ph = fig.get("plot_h", 470)
    fl = F("bold", 27 if len(items) <= 6 else 23)
    lab_lines = max(len(wrap(probe, it["label"], fl, (W - 2 * PAD) / len(items) - 12)) for it in items)
    c = Canvas(int(hh + 60 + ph + 20 + 36 * lab_lines + 24 + foot_h(fig, doc)))
    draw_header(c, fig)
    vals = [it["value"] for it in items]
    ref = fig.get("ref")
    vmin, vmax = min(0, min(vals)), max(0, max(vals + ([ref["v"]] if ref else [])))
    top, bot = hh + 60, hh + 60 + ph
    Y = lambda v: bot - (bot - top) * (v - vmin) / ((vmax - vmin) or 1)
    n = len(items)
    cw = (W - 2 * PAD) / n
    bw = min(120, cw * 0.58)
    c.line([(PAD, Y(0)), (W - PAD, Y(0))], NOTE, 2)
    for i, it in enumerate(items):
        c.g = i
        cx = PAD + cw * (i + 0.5)
        v = it["value"]
        hi = it.get("hi")
        c.rect(cx - bw / 2, Y(0), cx + bw / 2, Y(v), HI if hi else BAR, r=6)
        t = it.get("text") or fmt(v, unit, dec)
        fv = F("bold", 29 if n <= 6 else 24)
        if v >= 0:
            c.text(cx, Y(v) - 10, t, fv, HIT if hi else TXT, anchor="ms")
        else:
            c.text(cx, Y(v) + 10, t, fv, HIT if hi else TXT, anchor="mt")
        for k, ln in enumerate(wrap(c, it["label"], fl, cw - 12)):
            c.text(cx, bot + 22 + k * 36 + (0 if vmin >= 0 else 0), ln, fl, TXT, anchor="mt")
    c.g = "ref"
    if ref:
        y = Y(ref["v"])
        c.line([(PAD, y), (W - PAD, y)], REF, 3, dash=8)
        c.text(W - PAD, y - 10, ref["label"], F("bold", 26), REF, anchor="rs")
    c.g = None
    draw_footer(c, fig, doc)
    return c


# ---------- 선 그래프 공용 ----------
def _date_ticks(dates: list[str], k=5) -> list[int]:
    n = len(dates)
    if n <= k:
        return list(range(n))
    return sorted(set(round(i * (n - 1) / (k - 1)) for i in range(k)))


def _dlabel(d: str, span_days: int) -> str:
    y, m, dd = d.split("-")
    return f"{y[2:]}.{m}" if span_days > 150 else f"{int(m)}.{int(dd)}"


def _axes(c, fig, lo, hi, x0, x1, top, bot, unit, dec, dates, fmt_tick=None):
    ticks, step = nice_ticks(lo, hi, fig.get("y_ticks", 5))
    lo, hi = ticks[0], ticks[-1]
    Y = lambda v: bot - (bot - top) * (v - lo) / ((hi - lo) or 1)
    for t in ticks:
        c.line([(x0, Y(t)), (x1, Y(t))], BAR, 1.5)
        td = 0
        while td < 6 and abs(step * 10 ** td - round(step * 10 ** td)) > 1e-6:
            td += 1
        lab = fmt_tick(t) if fmt_tick else fmt(t, "", td)
        c.text(x0 - 12, Y(t), lab, F("reg", 24), SUB, anchor="rm")
    n = len(dates)
    X = lambda i: x0 + (x1 - x0) * i / max(1, n - 1)
    span = (dt.date.fromisoformat(dates[-1]) - dt.date.fromisoformat(dates[0])).days
    for i in _date_ticks(dates, fig.get("x_ticks", 5)):
        c.text(X(i), bot + 14, _dlabel(dates[i], span), F("reg", 24), SUB, anchor="mt")
    return X, Y


def price_events(fig, doc, base_dir) -> Canvas:
    rows = load_series(fig["series"], base_dir)
    dates = [d for d, _ in rows]
    vals = [v for _, v in rows]
    unit, dec = fig.get("unit", "달러"), fig.get("decimals")
    events = fig.get("events", [])
    probe = Canvas(10)
    hh = header_h(probe, fig)
    fe = F("reg", 27)
    ev_lines = sum(len(wrap(probe, f"{e['label']}", fe, W - 2 * PAD - 60)) for e in events) + (1 if fig.get("ref") else 0)
    ph = fig.get("plot_h", 470)
    top = hh + 30
    bot = top + ph
    leg_top = bot + 64
    c = Canvas(int(leg_top + ev_lines * 40 + (16 if events else 0) + 10 + foot_h(fig, doc)))
    draw_header(c, fig)
    ref = fig.get("ref")
    lo, hi = min(vals + ([ref["v"]] if ref else [])), max(vals + ([ref["v"]] if ref else []))
    pad = (hi - lo) * 0.08 or 1
    x0 = PAD + max(probe.tw(fmt(hi, "", dec), F("reg", 24)), 40) + 18
    x1 = W - PAD - 120
    X, Y = _axes(c, fig, lo - pad, hi + pad, x0, x1, top, bot, unit, dec, dates)
    if ref:
        c.g = "ref"
        y = Y(ref["v"])
        c.line([(x0, y), (x1, y)], REF, 3, dash=8)
    idx = {d: i for i, d in enumerate(dates)}
    for k, e in enumerate(events, 1):  # 사건 세로 점선
        i = idx.get(e["date"])
        if i is None:
            continue
        c.g = f"e{k}"
        c.gx[c.g] = round(X(i), 1)
        c.line([(X(i), top), (X(i), bot)], NOTE, 1.5, dash=5)
    c.g = "line"
    c.line([(X(i), Y(v)) for i, v in enumerate(vals)], TXT, 4)
    # 마지막 값
    c.g = "end"
    c.dot(X(len(vals) - 1), Y(vals[-1]), 8, HI)
    c.text(X(len(vals) - 1) + 14, Y(vals[-1]), fmt(vals[-1], unit if fig.get("last_unit", True) else "", dec), F("bold", 28), HIT, anchor="lm")
    # 사건 번호 동그라미(겹치면 위로 비켜 그림)
    placed = []
    for k, e in enumerate(events, 1):
        i = idx.get(e["date"])
        if i is None:
            raise SystemExit(f"사건 날짜가 시계열에 없습니다: {e['date']}")
        x, y = X(i), Y(vals[i])
        c.g = f"e{k}"
        c.dot(x, y, 7, TXT)
        above = e.get("pos", "above") == "above"
        by = y - 40 if above else y + 40
        if above and by - 20 < top - 26:
            by = y + 40
        while any(abs(px - x) < 40 and abs(py - by) < 40 for px, py in placed):
            by += -42 if above else 42
        placed.append((x, by))
        c.line([(x, y), (x, by)], TXT, 2)
        c.dot(x, by, 19, HI)
        c.text(x, by, str(k), F("bold", 26), KNOCK, anchor="mm")
    # 아래 사건 목록(기준선 설명은 맨 위 한 줄: 선 위에 쓰면 가격선과 겹친다)
    y = leg_top
    if ref:
        c.g = "ref"
        c.line([(PAD + 2, y + 20), (PAD + 36, y + 20)], REF, 4, dash=5)
        c.text(PAD + 52, y + 2, ref["label"], F("bold", 27), REF)
        y += 40
    for k, e in enumerate(events, 1):
        c.g = f"e{k}"
        c.dot(PAD + 18, y + 19, 17, HI)
        c.text(PAD + 18, y + 19, str(k), F("bold", 23), KNOCK, anchor="mm")
        for j, ln in enumerate(wrap(c, e["label"], fe, W - 2 * PAD - 60)):
            c.text(PAD + 52, y + 2, ln, F("bold", 27) if j == 0 and False else fe, TXT)
            y += 40
    c.g = None
    draw_footer(c, fig, doc)
    return c


def relative(fig, doc, base_dir) -> Canvas:
    base = fig.get("base")
    ser = []
    for s in fig["series"]:
        spec = dict(s["data"]) if isinstance(s["data"], dict) else s["data"]
        if isinstance(spec, dict):
            spec.setdefault("from", base)
            spec.setdefault("to", fig.get("to"))
        rows = load_series(spec, base_dir)
        if base and rows[0][0] != base:
            raise SystemExit(f"{s['name']}: 기준일 {base} 값이 없습니다(첫 날짜 {rows[0][0]})")
        b = rows[0][1]
        ser.append((s, [(d, v / b * 100) for d, v in rows]))
    dates = sorted(set(d for _, r in ser for d, _ in r))
    probe = Canvas(10)
    hh = header_h(probe, fig)
    ph = fig.get("plot_h", 500)
    top, bot = hh + 30, hh + 30 + ph
    c = Canvas(int(bot + 60 + 10 + foot_h(fig, doc)))
    draw_header(c, fig)
    allv = [v for _, r in ser for _, v in r] + [100]
    lo, hi = min(allv), max(allv)
    pad = (hi - lo) * 0.06 or 1
    x0 = PAD + 62
    fe = F("bold", 26)
    endw = max(probe.tw(f"{s['name']} {fmt(r[-1][1] - 100, '%', 1, sign=True)}", fe) for s, r in ser) + 30
    x1 = W - PAD - endw
    X, Y = _axes(c, fig, lo - pad, hi + pad, x0, x1, top, bot, "", 0, dates)
    c.line([(x0, Y(100)), (x1, Y(100))], NOTE, 2.5, dash=7)
    c.text(x1, Y(100) + 10, fig.get("base_label") or f"{int(base[5:7])}월 {int(base[8:])}일 = 100", F("reg", 23), NOTE, anchor="rt")
    di = {d: i for i, d in enumerate(dates)}
    styles = [(HI, 6), (REF, 4), (SUB, 3.5), (NOTE, 3), (BAR, 3)]
    ends = []
    order = sorted(range(len(ser)), key=lambda k: -k)  # 강조선(첫 줄)을 맨 위에
    for k in order:
        c.g = "line"
        s, r = ser[k]
        col, w = styles[min(k, len(styles) - 1)] if not s.get("color") else ({"hi": HI, "ref": REF, "sub": SUB, "note": NOTE}[s["color"]], 4)
        c.line([(X(di[d]), Y(v)) for d, v in r], col, w)
        c.g = "end"
        c.dot(X(di[r[-1][0]]), Y(r[-1][1]), w + 2, col)
        ends.append([Y(r[-1][1]), s, r, col, k])
    ends.sort(key=lambda e: e[0])
    for j in range(1, len(ends)):  # 끝 라벨 겹침 풀기
        if ends[j][0] - ends[j - 1][0] < 34:
            ends[j][0] = ends[j - 1][0] + 34
    for y, s, r, col, k in ends:
        t = f"{s['name']} {fmt(r[-1][1] - 100, '%', 1, sign=True)}"
        c.text(x1 + 16, y, t, fe, HIT if col == HI else (TXT if col != REF else REF), anchor="lm")
    c.g = None
    draw_footer(c, fig, doc)
    return c


TYPES = {"compare", "record", "scenarios", "trend", "price_events", "relative"}


def render(fig, doc, base_dir) -> Canvas:
    t = fig["type"]
    if t not in TYPES:
        raise SystemExit(f"모르는 그림 유형 {t} (가능: {', '.join(sorted(TYPES))})")
    if t in ("compare", "record", "scenarios"):
        return hbars(fig, doc, t)
    if t == "trend":
        return trend(fig, doc)
    if t == "price_events":
        return price_events(fig, doc, base_dir)
    return relative(fig, doc, base_dir)


FIG2TPL = {"compare": "compare_bars", "relative": "relative_lines", "record": "record_bars", "scenarios": "scenario_bars", "trend": "trend_line", "price_events": "live_chart"}


def _md(s: str) -> str:
    return "%d.%d" % (int(s[5:7]), int(s[8:10])) if len(s) >= 10 and s[4] == "-" else s


def inline_fig(fig, base_dir) -> dict:
    """시세 파일을 읽어 그림에 쓰인 구간만 [[날짜, 종가]]로 넣는다(사이트에 올리는 명세가 혼자서 다시 그려지게)."""
    f = json.loads(json.dumps(fig))
    if f["type"] == "price_events":
        f["series"] = [[d, v] for d, v in load_series(fig["series"], base_dir)]
    elif f["type"] == "relative":
        for s in f["series"]:
            spec = dict(s["data"]) if isinstance(s["data"], dict) else s["data"]
            if isinstance(spec, dict):
                spec.setdefault("from", fig.get("base"))
                spec.setdefault("to", fig.get("to"))
            s["data"] = [[d, v] for d, v in load_series(spec, base_dir)]
    return f


def anim_data(fig, doc) -> tuple[str, dict]:
    """영상 anim 틀 입력 {tpl, data}(slidekit anim.py fromfig 와 같은 규칙). fig 는 inline_fig 결과."""
    t = fig["type"]
    asof = fig.get("asof", doc.get("asof"))
    src = " · ".join(x for x in [fig.get("source", doc.get("source")), ("기준 " + asof) if asof else ""] if x)
    out = {"title": " ".join(fig["title"]) if isinstance(fig.get("title"), list) else fig.get("title", ""), "source": src}
    for k in ("sub", "note", "unit", "decimals"):
        if k in fig:
            out[k] = fig[k]
    if t in ("compare", "record", "trend"):
        out["items"] = fig["items"]
    if t == "trend" and fig.get("ref"):
        out["ref"] = fig["ref"]
    if t == "scenarios":
        out["items"] = fig["items"]
        out["decision"] = fig.get("decision", "")
    if t == "relative":
        ser = []
        for s in fig["series"]:
            rows = [(d, v) for d, v in load_series(s["data"], "") if fig["base"] <= d <= fig.get("to", "9999")]
            ser.append({"name": s["name"], "points": [[_md(d), v] for d, v in rows], **({"hi": True} if s.get("hi") or not ser else {})})
        out["series"] = ser
        out["base_label"] = _md(fig["base"]) + " = 100"
    if t == "price_events":
        rows = dict(load_series(fig["series"], ""))
        pts = []
        for e in fig.get("events", [])[:8]:
            lab = e["label"]
            lab = lab.split(" ", 1)[1] if lab.split(" ", 1)[0].replace(".", "").isdigit() and " " in lab else lab
            pts.append([_md(e["date"]), rows[e["date"]], lab])
        out["points"] = pts
        out["unit"] = fig.get("unit", "달러")
        out.pop("decimals", None)
        if fig.get("ref"):
            out["base"] = {"value": fig["ref"]["v"], "label": fig["ref"].get("label", "")}
    return FIG2TPL[t], out


def main(argv):
    """그림마다 ① 정지 이미지 <slug>-<n>.webp(다크, 가로 1200) ② 명세 <slug>-<n>.json 을 낸다(--png 면 흰 바탕 PNG 도).
    명세 = 그 그림 하나짜리 figkit 문서(시세는 쓰인 구간만 안에 넣음) + 영상 틀 {tpl, data} + 웹 그리기 목록 web.
    그래서 같은 명세로 영상 클립(slidekit anim.py fromfig <명세> <n>)·리포트 웹 애니메이션·정지 이미지(이 도구에 명세를 다시 넣음)를 모두 만든다.
    --site <사이트 폴더>: static/charts/(WebP)·static/figs/(명세)에 바로 복사."""
    args = [a for a in argv[1:] if not a.startswith("--")]
    site = argv[argv.index("--site") + 1] if "--site" in argv else ""
    if site in args:
        args.remove(site)
    if len(args) < 2:
        print(__doc__)
        return 2
    spec_p, out = args[0], args[1]
    doc = json.load(open(spec_p, encoding="utf-8"))
    os.makedirs(out, exist_ok=True)
    base_dir = os.path.dirname(os.path.abspath(spec_p))
    made = []
    for i, fig in enumerate(doc["figs"], 1):
        n = fig.get("n", i)
        stem = (fig.get("file") or f"{doc['slug']}-{n}").rsplit(".", 1)[0]
        fig_in = inline_fig(fig, base_dir)
        if "--png" in argv:
            set_palette(False)
            render(fig_in, doc, base_dir).save(os.path.join(out, stem + ".png"))
        set_palette(True)
        c = render(fig_in, doc, base_dir)
        wp = os.path.join(out, stem + ".webp")
        c.save(wp)
        tpl, data = anim_data(fig_in, doc)
        one = {"slug": doc["slug"], "n": n, **{k: doc[k] for k in ("asof", "source") if k in doc}, "figs": [fig_in],
               "tpl": tpl, "data": data, "web": c.web()}
        jp = os.path.join(out, stem + ".json")
        with open(jp, "w", encoding="utf-8") as fh:
            json.dump(one, fh, ensure_ascii=False, separators=(",", ":"))
        made.append((wp, jp))
        print(f"saved {wp} {W}x{c.h} {os.path.getsize(wp) // 1024}KB · {jp} {os.path.getsize(jp) // 1024}KB ({tpl})")
        if site:
            import shutil
            for src, sub in ((wp, "charts"), (jp, "figs")):
                d = os.path.join(site, "static", sub)
                os.makedirs(d, exist_ok=True)
                shutil.copyfile(src, os.path.join(d, os.path.basename(src)))
    set_palette(False)
    print(f"FIGKIT_OK {len(made)}장" + (f" → {site}/static/charts·figs" if site else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
