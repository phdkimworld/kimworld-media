#!/usr/bin/env python3
"""3시간마다 제작 점검의 첫 단계(토큰 절약, 2026-11-10). 오늘 몫과 진행 중 제작을 장부로 세어 한 줄로 낸다.
첫 줄 "NOTHING ..."이면 세션은 그 줄만 보고하고 끝낸다. "ACTION ..."이면 예약 작업 지침 전체를 따른다.
판정: production/STATE.md 의 오늘(ET) 행 — '정규'·'요청'·'정규2' 트랙이 '완료'면 찬 것으로 센다('하나 더'는 몫 밖).
'진행' 이 들어 있고 '완료'가 없는 행이 있으면 ACTION(이어서 끝내야 함). 밀린 쇼츠 등 '대기' 행도 ACTION.
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
done = {c[1] for c in today if "완료" in c[2]}
pending = [f"{c[0]} {c[1]}: {c[2][:40]}" for c in map(cells, rows)
           if len(c) > 2 and ((any(re.search(r"(^|[\s·(])(진행|대기)(?!열)", x) for x in c[2:]) and not any("완료" in x or "정리" in x for x in c[2:])) or re.search(r"\|\s*대기\s*\|?\s*$", "|".join(c)))]
r = "정규" in done; q = "요청" in done; r2 = "정규2" in done
rank = subprocess.run([sys.executable, "tools/request_rank.py"], cwd=M, capture_output=True, text=True).stdout
tiers = {t: len(re.findall(rf"^\d+ \| {t} \|", rank, re.M)) for t in ("0순위", "1순위", "2순위")}
top = re.search(r"^1 \| \S+ \| (\S+)", rank, re.M)
cand = sum(tiers.values())
full = r and (q or r2 or (cand == 0 and False))
try:
    posted = json.load(open(f"{SITE}/social/blogger/posted.json")); pn = len(posted if isinstance(posted, list) else posted.get("posted", posted))
except Exception: pn = "?"
reports = len(glob.glob(f"{SITE}/content/reports/*.md"))
line = (f"제작 점검 {NOW:%m/%d %H:%M} ET: 정규 {int(r)} · 요청 {int(q)}{' · 정규2 1' if r2 else ''} / 2"
        f"(요청 후보 0순위 {tiers['0순위']} · 1순위 {tiers['1순위']} · 2순위 {tiers['2순위']}), "
        f"진행 중 {'; '.join(pending) if pending else '없음'}, 블로거 {pn}/{reports}, 다음 요청 후보 {top.group(1) if top else '없음'}")
print(("NOTHING " if full and not pending else "ACTION ") + line)
