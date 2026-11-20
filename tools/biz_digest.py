#!/usr/bin/env python3
"""사업 자산 요약 한 장(운영자 지시 2026-11-19 "일일 수익성 진단 및 개선의 대상을 사이트 뿐 아니라 유튜브를 포함한 모든 비지니스 자산으로 확대").

LLM·API 없이 저장소 파일만 읽는다. 매일 점검 세션이 사이트 요약(ops-data stats/digest.md)과 함께 이 한 장을 읽는다.
사용: python3 tools/biz_digest.py [사이트 저장소=/home/claude/kimworld-site] > review/biz_digest.md
담는 것
- 유튜브(stats_snapshots.jsonl, 3시간마다 hourly.py가 쌓음): 채널 전체 조회 24시간·7일 증가(전주 대비), 7일 새 영상 수,
  7일 조회 증가 상위 10편(티커·핵심 여부), 핵심 종목 vs 그 밖 비중, 새 영상 첫 24시간 조회 중앙값(핵심/그 밖), 옛 영상(30일+) 비중
- 구독 시험(review/sub_test.md), 예측 장부(review/predictions/ledger.jsonl), 전자책 진행(ebook/), 쿠팡 유튜브 카테고리(사이트 data/yt_shop.yaml·social/youtube/shop.json)
수익 숫자는 넣지 않는다(공개 저장소). 수익은 비공개 ops-data digest.md에서 본다.
"""
import datetime as dt
import json
import os
import re
import statistics
import sys
from pathlib import Path

MEDIA = Path(__file__).resolve().parent.parent
SITE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/home/claude/kimworld-site")


def snaps():
    out = []
    for line in (MEDIA / "stats_snapshots.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            d = json.loads(line)
            out.append((dt.datetime.fromisoformat(d["t"]), d["v"]))
    return out


def at(S, when):
    """when 이전 가장 가까운 스냅숏. 한 스냅숏에서 빠진 영상(2026-11-20 확인: 수집 때 수십 편씩 빠지는 날이 있음)은
    그 전 마지막 값으로 채운다 — 안 채우면 빠졌던 옛 영상의 누적 조회 전체가 '증가'로 잡힌다(11-20 7일 37,080 → 실제 26,414)."""
    best, filled = None, {}
    for t, v in S:
        if t <= when:
            filled.update(v)
            best = (t, dict(filled))
    return best


def id_map():
    """사이트 리포트 머리말 youtube_id → (티커, slug)."""
    m = {}
    for p in (SITE / "content" / "reports").glob("*.md"):
        head = p.read_text(encoding="utf-8")[:3000]
        y = re.search(r"(?m)^youtube_id:\s*\"?([\w-]{11})", head)
        t = re.search(r"(?m)^ticker:\s*\"?([A-Z0-9]+)", head)
        if y and t:
            m[y.group(1)] = (t.group(1), p.stem)
    return m


def core():
    p = MEDIA / "review" / "core_tickers.md"
    return set(re.findall(r"(?m)^\|\s*([A-Z0-9]{1,6})\s*\|", p.read_text(encoding="utf-8"))) - {"티커"} if p.exists() else set()


def first_seen(S):
    f = {}
    for t, v in S:
        for k in v:
            f.setdefault(k, t)
    return f


def gain(a, b):
    return {k: b[1][k] - a[1].get(k, 0) for k in b[1]} if a and b else {}


def main():
    S = snaps()
    now_t, now_v = S[-1]
    ids, cores, fs = id_map(), core(), first_seen(S)
    d1, d7, d14 = at(S, now_t - dt.timedelta(days=1)), at(S, now_t - dt.timedelta(days=7)), at(S, now_t - dt.timedelta(days=14))
    g1, g7, gp = gain(d1, S[-1]), gain(d7, S[-1]), gain(d14, d7)
    tot7, totp, tot1 = sum(g7.values()), sum(gp.values()), sum(g1.values())
    out = [f"# 사업 자산 요약 {now_t:%Y-%m-%d %H:%M}Z (유튜브 스냅숏 {len(S)}개, 영상 {len(now_v)}편)", "",
           "## 유튜브"]
    out.append(f"- 조회 증가: 24시간 {tot1:,} · 7일 {tot7:,}" + (f" (전주 {totp:,}, {(tot7 - totp) / totp * 100:+.0f}%)" if totp else ""))
    new7 = [k for k, t in fs.items() if t > now_t - dt.timedelta(days=7) and S[0][0] < now_t - dt.timedelta(days=8)]
    out.append(f"- 7일 새 영상 {len(new7)}편(쇼츠 포함)")
    tag = lambda k: (ids.get(k, ("?", ""))[0] + ("★" if ids.get(k, ("",))[0] in cores else ""))
    top = sorted(g7.items(), key=lambda kv: -kv[1])[:10]
    out.append("- 7일 조회 증가 상위 10: " + " · ".join(f"{tag(k)} {k} +{v}" for k, v in top))
    cg = sum(v for k, v in g7.items() if ids.get(k, ("",))[0] in cores)
    og = sum(v for k, v in g7.items() if fs.get(k, now_t) < now_t - dt.timedelta(days=30))
    unk = sum(v for k, v in g7.items() if k not in ids)
    if tot7:
        out.append(f"- 7일 증가 비중: 핵심 종목★ 롱폼 {cg / tot7 * 100:.0f}% · 30일 넘은 옛 영상 {og / tot7 * 100:.0f}% · 사이트 리포트와 안 이어진 영상(쇼츠·사이트 전 옛 영상) {unk / tot7 * 100:.0f}%")
    # 새 롱폼(리포트와 이어진 것) 첫 24시간 조회: 핵심 vs 그 밖
    f24 = {"핵심": [], "그 밖": []}
    for k, t in fs.items():
        if k in ids and t > now_t - dt.timedelta(days=14) and t > S[0][0] + dt.timedelta(hours=6):
            s24 = at(S, t + dt.timedelta(hours=24))
            if s24 and s24[0] >= t + dt.timedelta(hours=20):
                f24["핵심" if ids[k][0] in cores else "그 밖"].append(s24[1].get(k, 0))
    out.append("- 새 롱폼 첫 24시간 조회 중앙값(14일): " + " · ".join(f"{g} {statistics.median(v):.0f}회(n={len(v)})" for g, v in f24.items() if v))
    out.append(f"- 핵심 종목: {' '.join(sorted(cores)) or '없음'}")

    out += ["", "## 구독 시험(F9)"]
    st = MEDIA / "review" / "sub_test.md"
    if st.exists():
        rows = [l for l in st.read_text(encoding="utf-8").splitlines() if re.match(r"^\| (20\d\d-)?\d\d-\d\d \|", l)]  # 11-17 같은 짧은 날짜도
        a = sum(re.search(r"\| A \|", l) is not None for l in rows)
        out.append(f"- 기록 {len(rows)}편(A {a} · B {len(rows) - a}) · 판정 12-01 · 기준선 1,000회당 1.1명(vidIQ 채널 구독자로 확인)")
        for l in st.read_text(encoding="utf-8").splitlines():
            if l.startswith(("워터마크:", "영상별 구독 읽기", "A 합계:")):
                out.append("- " + l[:120])

    out += ["", "## 예측 장부·성적표·전자책"]
    lp = MEDIA / "review" / "predictions" / "ledger.jsonl"
    if lp.exists():
        L = [json.loads(x) for x in lp.read_text(encoding="utf-8").splitlines() if x.strip()]
        c = {}
        for r in L:
            c[r["status"]] = c.get(r["status"], 0) + 1
        due = sum(1 for r in L if r.get("status") == "대기" and (r.get("judge_date") or "9") <= (now_t.date() + dt.timedelta(days=7)).isoformat())
        out.append(f"- 예측 {len(L)} · " + " · ".join(f"{k} {v}" for k, v in sorted(c.items(), key=lambda kv: -kv[1])) + f" · 7일 안 판정일 {due}")
    eb = MEDIA / "ebook"
    if eb.exists():
        ch = list((eb / "chapters").glob("*.md")) if (eb / "chapters").exists() else []
        out.append(f"- 전자책: 원고 {len(ch)}장 · 장부 마감 2027-01-05 · 목차 ebook/TOC_DRAFT.md")

    out += ["", "## 유튜브 쿠팡 실험"]
    sj = SITE / "social" / "youtube" / "shop.json"
    if sj.exists():
        log = json.loads(sj.read_text(encoding="utf-8"))
        since = (now_t.date() - dt.timedelta(days=60)).isoformat()
        cnt = {}
        for e in log:
            if e.get("date", "") >= since:
                cnt[e["cat"]] = cnt.get(e["cat"], 0) + 1
        out.append("- 60일 영상 수: " + " · ".join(f"{k} {v}" for k, v in sorted(cnt.items())) + " · 클릭·수수료는 비공개 digest.md(유튜브 카테고리 줄)")
    print("\n".join(out))


if __name__ == "__main__":
    main()
