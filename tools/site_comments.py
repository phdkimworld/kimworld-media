"""사이트(리포트 옆 종토방 b-<티커>·b-talk) 댓글 가운데 운영자('김박사 월드') 답글이 아직 없는 글을 보여 준다.

사용: python3 tools/site_comments.py [--site /home/user/kimworld-site]
답글은 사이트 저장소 social/site_replies/<YYYYMMDD-HHMM>.json {"replies":[{"parent":id,"slug":"b-xxx","body":"..."}]}로
main에 올리면 deploy.yml(푸시 때와 매시 5분)이 넣는다. 같은 부모·같은 본문은 한 번만 들어간다.
"""
import argparse, datetime as dt, json, urllib.request
from pathlib import Path
import yaml

ap = argparse.ArgumentParser(); ap.add_argument("--site", default="/home/user/kimworld-site"); a = ap.parse_args()
site = Path(a.site)
tk = yaml.safe_load((site / "data/tickers.yaml").read_text(encoding="utf-8")) or {}
slugs = ["b-" + t.lower() for t in tk if all(ch.isalnum() for ch in t)] + ["b-talk"]
queued = set()
for f in (site / "social/site_replies").glob("*.json"):
    for r in json.loads(f.read_text(encoding="utf-8")).get("replies", []):
        queued.add(int(r["parent"]))
H = {"User-Agent": "Mozilla/5.0 research"}
out = []
for s in slugs:
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(f"https://api.drkimworld.com/v1/comments?slug={s}", headers=H), timeout=20))
    except Exception:
        continue
    cs = d.get("comments", [])
    answered = {c.get("parent") for c in cs if c["nick"] == "김박사 월드"}
    for c in cs:
        if c["nick"] == "김박사 월드" or c["id"] in answered or c["id"] in queued:
            continue
        out.append({"id": c["id"], "slug": s, "parent": c.get("parent"), "nick": c["nick"],
                    "created": dt.datetime.fromtimestamp(c["created"] / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M"),
                    "body": c["body"][:300], "quote": c.get("quote")})
print(json.dumps({"open": out}, ensure_ascii=False, indent=1))
