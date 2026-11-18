#!/usr/bin/env python3
"""3시간마다 제작 점검의 첫 단계(토큰 절약, 2026-11-10). 오늘 몫과 진행 중 제작을 장부로 세어 한 줄로 낸다.
첫 줄 "NOTHING ..."이면 세션은 그 줄만 보고하고 끝낸다. "ACTION ..."이면 예약 작업 지침 전체를 따른다.
판정: production/STATE.md 의 오늘(ET) 행 — '정규'·'요청'·'정규2' 트랙이 '완료'면 찬 것으로 센다('하나 더'는 몫 밖).
'진행' 이 들어 있고 '완료'가 없는 행이 있으면 ACTION(이어서 끝내야 함). 밀린 쇼츠 등 '대기' 행도 ACTION.
제작팀 권고안(11-16): 오늘 몫 롱폼 행 수를 세어 3 이상이면 '하루 상한' 경고(R2), 다음 요청 후보가 핵심 종목이면 ★(R1, review/core_tickers.md).
--cap-history: 과거 STATE 날짜별 롱폼 수와 상한 경고(오탐 확인용).
"""
import re, os, json, glob, subprocess, datetime, sys
from zoneinfo import ZoneInfo

# 컨테이너 재시작으로 작업 도구가 사라졌으면 저장소에서 다시 깐다(11-11)
if not os.path.exists("/home/claude/slidekit/make_slide_video.py"):
    subprocess.run(["bash", os.path.join(os.path.dirname(os.path.abspath(__file__)), "restore_workspace.sh")], capture_output=True)

M = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.environ.get("KW_SITE", "/home/user/kimworld-site")
NOW = datetime.datetime.now(ZoneInfo("America/New_York")); D = NOW.strftime("%m-%d")
subprocess.run(["git", "pull", "-q", "--rebase", "origin", "claude/kim-world-stock-studio-laes-ovy09b"], cwd=M, capture_output=True)
subprocess.run(["git", "pull", "-q", "--rebase", "origin", "main"], cwd=SITE, capture_output=True)
rows = [l for l in open(f"{M}/production/STATE.md") if l.startswith("| ")]
def cells(l): return [c.strip() for c in l.strip().strip("|").split("|")]
today = [cells(l) for l in rows if cells(l)[0] == D]
done = {c[1] for c in today if any(x.startswith("완료") for x in c[2:]) or "완료" in c[2]}  # 11-15: '합성 완료' 같은 단계 표기는 완료로 치지 않음  # 상태 칸이 뒤로 옮겨진 행(11-11~)도 센다
pending = [f"{c[0]} {c[1]}: {c[2][:40]}" for c in map(cells, rows)
           if len(c) > 2 and ((any(re.search(r"(^|[\s·(])(진행|대기)(?!열)", x) for x in c[2:]) and not any(x.startswith("완료") or x.startswith("정리") for x in c[1:])) or re.search(r"\|\s*대기\s*\|?\s*$", "|".join(c)))]
r = "정규" in done; q = "요청" in done; r2 = "정규2" in done
# 제작팀 권고안 R2(11-16): 롱폼 하루 3편 이하(권장 2). 그날 몫 행 가운데 롱폼 행(밀린 쇼츠·정리 제외)을 센다
LONG_CAP = 3
def long_rows(day): return [c for c in (cells(l) for l in rows) if c[0] == day and len(c) > 1 and not re.search(r"쇼츠|정리", c[1])]
n_long = len(long_rows(D))
sys.path.insert(0, os.path.join(M, "tools")); from core_tickers import load as _core
CORE = _core()
# R1 70/30: 지난 7일(몫 날짜) 롱폼 가운데 핵심 종목 비율. 종목 칸 첫 영문 대문자 낱말을 티커로 본다
_wk = {(NOW - datetime.timedelta(days=i)).strftime("%m-%d") for i in range(7)}
_wl = [c for d in _wk for c in long_rows(d)]
_wt = [(re.search(r"\b([A-Z]{2,5})\b", c[2]) or [None, ""])[1] for c in _wl]
core_wk = f"{sum(t in CORE for t in _wt)}/{len(_wt)}"
rank = subprocess.run([sys.executable, "tools/request_rank.py"], cwd=M, capture_output=True, text=True).stdout
tiers = {t: len(re.findall(rf"^\d+ \| {t} \|", rank, re.M)) for t in ("0순위", "1순위", "2순위")}
top = re.search(r"^1 \| \S+ \| (\S+)", rank, re.M)
top_tk = (top.group(1).rstrip("★") + ("★" if top.group(1).rstrip("★").upper() in CORE else "")) if top else None
cand = sum(tiers.values())
full = r and (q or r2 or (cand == 0 and False))
try:
    posted = json.load(open(f"{SITE}/social/blogger/posted.json")); pn = len(posted if isinstance(posted, list) else posted.get("posted", posted))
except Exception: pn = "?"
reports = len(glob.glob(f"{SITE}/content/reports/*.md"))
line = (f"제작 점검 {NOW:%m/%d %H:%M} ET: 정규 {int(r)} · 요청 {int(q)}{' · 정규2 1' if r2 else ''} / 2"
        f"(요청 후보 0순위 {tiers['0순위']} · 1순위 {tiers['1순위']} · 2순위 {tiers['2순위']}), "
        f"진행 중 {'; '.join(pending) if pending else '없음'}, 블로거 {pn}/{reports}, 다음 요청 후보 {top_tk or '없음'}, "
        f"7일 핵심 종목 ★{core_wk}(목표 90%·R1′ 핵심 종목 후속편만), 오늘 롱폼 {n_long}/{LONG_CAP}{(' — 하루 상한 초과 %d편(보고에 하루 상한 초과 한 줄)' % (n_long - LONG_CAP)) if n_long > LONG_CAP else (' — 하루 상한 도달: 더 만들면 운영자 하나 더 지시만, 보고에 하루 상한 초과 한 줄' if n_long == LONG_CAP else '')}")
print(("NOTHING " if full and not pending else "ACTION ") + line)
if "--cap-history" in sys.argv:  # 과거 STATE로 상한 경고 오탐 확인용
    for day in sorted({c[0] for c in map(cells, rows) if re.fullmatch(r"\d\d-\d\d", c[0])}):
        lr = long_rows(day); print(f"  {day} 롱폼 {len(lr)}{' ⚠ 하루 상한' + (' 초과' if len(lr) > LONG_CAP else ' 도달') if len(lr) >= LONG_CAP else ''}: " + ", ".join(c[1] for c in lr))

# 점검 중 바뀐 통계 스냅샷은 바로 커밋·푸시(세션 종료 때 '커밋 안 된 변경' 알림이 반복되지 않게, 11-12)
if subprocess.run(["git", "diff", "--quiet", "--", "stats_snapshots.jsonl"], cwd=M).returncode:
    subprocess.run(["git", "add", "stats_snapshots.jsonl"], cwd=M)
    subprocess.run(["git", "commit", "-qm", "통계 스냅샷 갱신\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01DaUBsG9X6bLavyZrFguf5X"], cwd=M, capture_output=True)
    for _ in range(3):
        if subprocess.run(["git", "push", "-q", "origin", "HEAD:claude/kim-world-stock-studio-laes-ovy09b"], cwd=M, capture_output=True).returncode == 0: break
        subprocess.run(["git", "pull", "-q", "--rebase", "--autostash", "origin", "claude/kim-world-stock-studio-laes-ovy09b"], cwd=M, capture_output=True)
