#!/usr/bin/env python3
"""이북 재료 쌓기(운영자 2026-11-18 "집필은 다른 데서 할 건데 재료는 니가 관리 … 제작 시 이북 재료들도 계속 쌓아 나가, 주기적으로 업데이트해서 출판").

사용:
  python3 tools/ebook_materials.py --sync           # 장부에서 새로 판정된 예측을 ebook/materials/judged.md에 붙임(중복 없음)
  python3 tools/ebook_materials.py --add <파일> --slug <slug> --text "..."   # 회차 재료 한 줄 추가
        파일: insights(통찰·통섭, 3부) | wrong(아픈 오답 후보, 5장) | filings(공시 사례, 부록 A) | questions(시청자 질문 원문, FAQ) | lens(다른 분야 비유 후보)
  python3 tools/ebook_materials.py --edition        # 이번 달 판(ebook/editions/YYYY-MM.md): 장부 숫자·재료 수·지난 판 뒤 새로 쌓인 것 요약
  python3 tools/ebook_materials.py --status         # 한 줄 요약(제작 점검·복기용)
숫자는 장부·리포트에 있는 것만. 판정 끝난 지난 예측만 '책에 실을 재료'로 표시하고, 대기 예측은 싣지 않는다(WRITING_GUIDE 0장).
"""
import argparse, datetime, json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "ebook", "materials"); E = os.path.join(ROOT, "ebook", "editions")
LEDGER = os.path.join(ROOT, "review", "predictions", "ledger.jsonl")
FILES = {"judged": "판정 끝난 예측(2부 성적표·5장 오답 재료, 장부에서 자동)", "insights": "통찰·통섭(3부 6~12장)",
         "wrong": "가장 아팠던 오답 후보(5장)", "filings": "공시 사례(부록 A 공시 도구상자)",
         "questions": "시청자 질문 원문(FAQ·들어가며)", "lens": "다른 분야 비유 후보(통섭 렌즈, 출처 필수)"}
DONE = ("일어남", "빗나감", "안 일어남", "적중")

def path(k): return os.path.join(M, f"{k}.md")
def ensure(k):
    os.makedirs(M, exist_ok=True)
    if not os.path.exists(path(k)):
        open(path(k), "w").write(f"# {FILES[k]}\n\n| 날짜 | 종목·slug | 내용 | 장 |\n|---|---|---|---|\n")
def has(k, key): return key in open(path(k)).read()
def today(): return datetime.date.today().isoformat()

def sync():
    ensure("judged"); n = 0
    for l in open(LEDGER):
        r = json.loads(l)
        if not any(str(r.get("status", "")).startswith(d) for d in DONE): continue
        if has("judged", r["id"]): continue
        ch = "5장 후보" if str(r["status"]).startswith(("빗나감", "안 일어남")) and (r.get("prob") or 0) >= 40 else "2부"
        txt = re.sub(r"\s+", " ", str(r.get("text", "")))[:140].replace("|", "/")
        line = f"| {r.get('judged') or today()} | {r['ticker']} · {r['slug']} | {txt} — 가능성 {r.get('prob')}% → {r['status']} (근거: {str(r.get('note',''))[:80].replace('|','/')}) `{r['id']}` | {ch} |\n"
        open(path("judged"), "a").write(line); n += 1
    return n

def add(k, slug, text):
    ensure(k); text = text.replace("|", "/").strip()
    open(path(k), "a").write(f"| {today()} | {slug} | {text} | |\n")

def counts():
    c = {}
    for k in FILES:
        c[k] = sum(1 for x in open(path(k)) if x.startswith("| 20")) if os.path.exists(path(k)) else 0
    return c

def edition():
    os.makedirs(E, exist_ok=True); ym = datetime.date.today().strftime("%Y-%m")
    rows = [json.loads(l) for l in open(LEDGER)]
    from collections import Counter
    st = Counter(str(r.get("status")) for r in rows); c = counts()
    body = [f"# 이북 재료 판 {ym} (작성 {today()})\n", f"- 장부 예측 {len(rows)}개: " + ", ".join(f"{k} {v}" for k, v in st.most_common()),
            "- 재료 수: " + ", ".join(f"{FILES[k].split('(')[0]} {v}" for k, v in c.items()),
            "- 다음 판에서 바뀔 숫자는 2027-01-05 장부 마감 전까지 '잠정'. 집필팀은 이 판의 숫자만 인용한다.",
            "- 재료 파일: ebook/materials/*.md · 자산 목록 ebook/ASSETS.md · 지침 ebook/WRITING_GUIDE.md"]
    open(os.path.join(E, f"{ym}.md"), "w").write("\n".join(body) + "\n"); return os.path.join(E, f"{ym}.md")

ap = argparse.ArgumentParser(); ap.add_argument("--sync", action="store_true"); ap.add_argument("--add")
ap.add_argument("--slug", default=""); ap.add_argument("--text", default=""); ap.add_argument("--edition", action="store_true")
ap.add_argument("--status", action="store_true"); a = ap.parse_args()
for k in FILES: ensure(k)
if a.sync: print(f"EBOOK_SYNC 새 판정 {sync()}건")
if a.add:
    assert a.add in FILES, f"파일은 {list(FILES)} 중 하나"; add(a.add, a.slug, a.text); print("EBOOK_ADD", a.add)
if a.edition: print("EBOOK_EDITION", edition())
if a.status or not (a.sync or a.add or a.edition):
    print("EBOOK " + " · ".join(f"{k} {v}" for k, v in counts().items()))
