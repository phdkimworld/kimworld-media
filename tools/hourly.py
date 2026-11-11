#!/usr/bin/env python3
"""매시간 댓글 점검을 스크립트로 처리한다(토큰 절약, 운영자 지시 2026-11-10 "다른 방식으로 최대한 토큰을 절약").

스크립트가 끝내는 것(틀 문장, 링크·숫자·질문 없음):
  - 유튜브·사이트·SNS의 짧은 감사·칭찬·인사 → THANKS 문장
  - 유튜브·SNS의 이모지만·한두 글자 → SMALL 문장(사이트는 규칙대로 건너뜀)
  - ET 시각이 3의 배수면 yt_stats.py 실행 후 stats_snapshots.jsonl 커밋
세션(모델)에 넘기는 것: 질문·의견·투표·종목 요청·대댓글·AI 여부·홍보 의심·새 사이트 요청
AI 답글(사이트 comment-ai.yml, 매시 15분, 2026-11-11): 사이트 social/llm/comments/state.json 장부가 살아 있으면(status ok, 4시간 안)
  유튜브·Threads·페이스북 첫 댓글 질문·의견 가운데 posted 는 건너뛰고, left 는 사유와 함께 넘기고, 아직 시도 전(2시간 안)인 것은 기다린다.
  키가 없거나 크레딧·예산이 없으면 장부가 ok 가 아니므로 지금 동작 그대로다.
출력 첫 줄: "NOTHING <요약>"(세션은 이 줄만 보고하고 끝) 또는 "ACTION <요약>" 다음 줄부터 넘길 항목 JSON.
사용: python3 tools/hourly.py [--dry]
"""
import json, os, re, subprocess, sys, time, hashlib, datetime, glob, urllib.request
from zoneinfo import ZoneInfo

# 컨테이너 재시작으로 작업 도구가 사라졌으면 저장소에서 다시 깐다(11-11)
if not os.path.exists("/home/claude/slidekit/make_slide_video.py"):
    subprocess.run(["bash", os.path.join(os.path.dirname(os.path.abspath(__file__)), "restore_workspace.sh")], capture_output=True)


MEDIA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.environ.get("KW_SITE", "/home/user/kimworld-site")
BR = "claude/kim-world-stock-studio-laes-ovy09b"
DRY = "--dry" in sys.argv
UA = {"User-Agent": "Mozilla/5.0 research"}
ET = ZoneInfo("America/New_York")
NOW = datetime.datetime.now(ET)
LIMIT = 40

THANKS = ["좋게 봐 주셔서 감사합니다. 남은 하루도 편안히 보내세요.",
          "따뜻한 말씀 감사합니다. 다음 영상도 꼼꼼히 준비하겠습니다.",
          "응원 감사합니다. 덕분에 힘이 납니다.",
          "시청해 주셔서 고맙습니다. 좋은 시간 보내세요.",
          "댓글 남겨 주셔서 감사합니다. 늘 건강하세요.",
          "끝까지 봐 주셔서 감사합니다. 편안한 하루 되세요.",
          "격려 말씀 고맙습니다. 더 알찬 내용으로 찾아뵙겠습니다.",
          "관심 가져 주셔서 감사합니다. 좋은 한 주 보내세요."]
SMALL = ["댓글 남겨 주셔서 감사합니다. 좋은 하루 보내세요.",
         "들러 주셔서 고맙습니다. 편안한 하루 되세요.",
         "남겨 주신 표시 감사합니다. 건강한 한 주 보내세요.",
         "반가운 흔적 감사합니다. 좋은 시간 되세요.",
         "찾아 주셔서 감사합니다. 남은 하루도 평안하세요.",
         "시청 감사합니다. 늘 좋은 일만 있으시길 바랍니다."]
THX_RE = re.compile(r"감사|고맙|잘\s*봤|잘\s*보고|잘\s*들었|응원|수고|좋은\s*(영상|정보|분석|내용|자료)|유익|최고|구독\s*(했|하고|누르)|화이팅|파이팅|좋아요")
ASK_RE = re.compile(r"\?|？|해\s*주|다뤄|부탁|요청|왜|어떻|언제|얼마|어디|무엇|뭐|궁금|알려|분석\s*좀|어때|일까|인가요|나요|까요|ㅠ|ㅜ|근데|하지만|그런데|반대|틀렸|아닌")
AI_RE = re.compile(r"(?<![A-Za-z])AI(?![A-Za-z])|인공지능|에이아이|GPT|자동\s*답글|봇(이|인가|이세요|이냐|같)|로봇|기계", re.I)
SPAM_RE = re.compile(r"https?://|t\.me/|텔레그램|카톡|카카오톡|오픈채팅|오픈톡|리딩|유료방|매매방|수익\s*(률)?\s*\d+\s*%|수익\s*보장|문의|추천방|무료\s*종목", re.I)
HANGUL = re.compile(r"[가-힣A-Za-z0-9]")

def classify(text, followup=False):
    t = (text or "").strip()
    if followup: return "escalate", "대댓글"
    if AI_RE.search(t): return "escalate", "AI여부"
    if SPAM_RE.search(t): return "escalate", "홍보의심"
    if re.fullmatch(r"[\d\s,번.과와및\-]+", t) and re.search(r"\d", t): return "escalate", "투표"
    if len(HANGUL.findall(t)) <= 2: return "small", "의미없음"
    if THX_RE.search(t) and not ASK_RE.search(t) and len(t) <= 80: return "thanks", "감사"
    return "escalate", "질문·의견·요청"

def pick(pool, key): return pool[int(hashlib.md5(key.encode()).hexdigest(), 16) % len(pool)]
def run(*a, cwd=MEDIA, timeout=600): return subprocess.run(a, cwd=cwd, capture_output=True, text=True, timeout=timeout)

def commit_push(repo, branch, paths, msg):
    run("git", "add", *paths, cwd=repo)
    if run("git", "diff", "--cached", "--quiet", cwd=repo).returncode == 0: return True
    run("git", "commit", "-qm", msg + "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01DaUBsG9X6bLavyZrFguf5X", cwd=repo)
    for i in range(4):
        if run("git", "push", "-q", "origin", f"HEAD:{branch}", cwd=repo).returncode == 0: return True
        run("git", "pull", "-q", "--rebase", "origin", branch, cwd=repo); time.sleep(2 ** (i + 1))
    return False

R = {"auto": [], "escalate": [], "notes": []}

def ai_state():
    try: st = json.load(open(f"{SITE}/social/llm/comments/state.json"))
    except Exception: return None
    try: last = datetime.datetime.fromisoformat(st.get("last_run", "").replace("Z", "+00:00"))
    except ValueError: return None
    if st.get("status") != "ok" or (datetime.datetime.now(datetime.timezone.utc) - last).total_seconds() > 4 * 3600: return None
    return st
AI = None

def ai_gate(key, base, published):
    """질문·의견 첫 댓글을 AI 답글 장부와 맞춘다. True 면 이번에는 넘기지 않는다."""
    if AI is None: return False
    it = (AI.get("items") or {}).get(key)
    if it and it.get("status") == "posted": R["notes"].append("AI 답글 완료 1건 건너뜀") if not any("AI 답글 완료" in n for n in R["notes"]) else None; return True
    if it and it.get("status") == "left": base["ai"] = "AI 넘김: " + str(it.get("reason", ""))[:80]; return False
    try: age = (datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(str(published).replace("Z", "+00:00"))).total_seconds() / 3600
    except ValueError: return False
    if age < float(AI.get("hold_hours", 2)):
        R["hold"] = R.get("hold", 0) + 1; return True
    return False

def youtube():
    if not os.environ.get("YT_REFRESH_TOKEN"): R["notes"].append("유튜브 인증값 없음"); return
    p = run(sys.executable, "tools/yt_reply.py", "--list")
    try: d = json.loads(p.stdout)
    except Exception: R["notes"].append("유튜브 목록 실패: " + (p.stdout + p.stderr)[-150:]); return
    used = d.get("my_replies_today_et", 0)
    for o in d.get("open", []):
        act, kind = classify(o.get("text", ""), o.get("kind") == "followup")
        base = {"ch": "youtube", "kind": kind, "threadId": o["threadId"], "videoId": o.get("videoId"),
                "author": o.get("author"), "text": (o.get("text") or "")[:200], "video": (o.get("videoTitle") or "")[:50]}
        if o.get("kind") == "followup": base["context"] = o.get("context") or o.get("followups")
        if act == "escalate" and kind == "질문·의견·요청" and o.get("kind") != "followup" and ai_gate(f"youtube:{o['threadId']}", base, o.get("publishedAt")):
            continue
        if act in ("thanks", "small") and used < LIMIT:
            body = pick(THANKS if act == "thanks" else SMALL, o["threadId"])
            f = "/tmp/kw_hourly_reply.txt"; open(f, "w").write(body)
            ok = True
            if not DRY:
                q = run(sys.executable, "tools/yt_reply.py", "--reply", o["threadId"], "--text-file", f, "--kind", "top")
                ok = q.returncode == 0; time.sleep(25)
            used += ok
            R["auto"].append({**base, "reply": body, "ok": ok})
        else:
            R["escalate"].append(base)
    R["notes"].append(f"유튜브 오늘 {used}/{LIMIT}")

def site():
    p = run(sys.executable, "tools/site_comments.py", "--site", SITE)
    try: d = json.loads(p.stdout)
    except Exception: R["notes"].append("사이트 댓글 실패"); return
    reps = []
    for o in d.get("open", []):
        act, kind = classify(o.get("body", ""), bool(o.get("parent")))
        base = {"ch": "site", "kind": kind, "id": o["id"], "slug": o["slug"], "parent": o.get("parent"),
                "nick": o.get("nick"), "text": (o.get("body") or "")[:200]}
        if act == "thanks":
            body = pick(THANKS, str(o["id"])); reps.append({"parent": o["id"], "slug": o["slug"], "body": body})
            R["auto"].append({**base, "reply": body, "ok": True})
        elif act == "small": R["auto"].append({**base, "skip": "의미 없는 글자(사이트 규칙)"})
        else: R["escalate"].append(base)
    if reps and not DRY:
        fn = f"social/site_replies/{NOW:%Y%m%d-%H%M}-auto.json"
        os.makedirs(f"{SITE}/social/site_replies", exist_ok=True)
        json.dump({"replies": reps}, open(f"{SITE}/{fn}", "w"), ensure_ascii=False, indent=1)
        commit_push(SITE, "main", [fn], f"사이트 댓글 감사 답글 {len(reps)}건(hourly.py)")

def sns():
    f = f"{SITE}/social/open/latest.json"
    if not os.path.exists(f): R["notes"].append("SNS 목록 파일 아직 없음(매시 12분 워크플로)"); return
    d = json.load(open(f))
    age = (datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.strptime(d.get("saved_utc", "2000-01-01T00:00Z"), "%Y-%m-%dT%H:%MZ").replace(tzinfo=datetime.timezone.utc)).total_seconds() / 3600
    if age > 3: R["notes"].append(f"SNS 목록이 {age:.0f}시간 전 것")
    done = set()
    for g in glob.glob(f"{SITE}/social/replies/*.json") + glob.glob(f"{SITE}/social/replies/done/*.json"):
        try:
            x = json.load(open(g))
            for it in x.get("replies", []) + x.get("results", []): done.add(str(it.get("to")))
        except Exception: pass
    reps = []
    items = list(d.get("open", []))
    for pl, v in (d.get("platforms") or {}).items():      # 워크플로는 채널별 open 에 담는다(11-10 누락 수정)
        if isinstance(v, dict):
            for o in v.get("open", []): items.append({**o, "platform": o.get("platform") or pl})
    seen = set()
    for o in items:
        if str(o.get("replyTo")) in done or str(o.get("replyTo")) in seen: continue
        # 인스타 댓글은 인스타팀 담당(skill/instagram/INSTAGRAM.md 7장, 11-11). 20시간 안 된 것은 넘기고, 그때까지 답이 없으면 여기서 받는다(누락 방지)
        if o.get("platform") == "instagram":
            try:
                age = (datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.strptime(o.get("publishedAt", ""), "%Y-%m-%dT%H:%M:%S%z")).total_seconds() / 3600
                if age < 20: R["notes"].append("인스타 댓글 1건 인스타팀 몫(20시간 대기)") if not any("인스타팀" in n for n in R["notes"]) else None; continue
            except Exception: pass
        seen.add(str(o.get("replyTo")))
        act, kind = classify(o.get("text", ""), o.get("kind") == "followup")
        base = {"ch": o.get("platform"), "kind": kind, "replyTo": o.get("replyTo"), "author": o.get("author"),
                "text": (o.get("text") or "")[:200], "slug": o.get("slug"), "post": (o.get("postText") or "")[:60]}
        if act == "escalate" and kind == "질문·의견·요청" and o.get("kind") != "followup" and o.get("platform") in ("threads", "facebook") \
                and ai_gate(f"{o.get('platform')}:{o.get('replyTo')}", base, o.get("publishedAt")):
            continue
        if act in ("thanks", "small"):
            body = pick(THANKS if act == "thanks" else SMALL, str(o.get("replyTo")))
            reps.append({"platform": o["platform"], "to": o["replyTo"], "text": body, "kind": "top"})
            R["auto"].append({**base, "reply": body, "ok": True})
        else: R["escalate"].append(base)
    for k, v in (d.get("platforms") or {}).items():
        if isinstance(v, dict) and v.get("ok") is False: R["notes"].append(f"{k} 읽기 실패")
    if reps and not DRY:
        fn = f"social/replies/{NOW:%Y%m%d-%H%M}-auto.json"
        json.dump({"replies": reps}, open(f"{SITE}/{fn}", "w"), ensure_ascii=False, indent=1)
        commit_push(SITE, "main", [fn], f"SNS 감사 답글 {len(reps)}건(hourly.py)")

def site_requests():
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(
            f"https://api.drkimworld.com/v1/requests/top?x={int(time.time())}", headers=UA), timeout=30))
    except Exception as e: R["notes"].append(f"사이트 요청 조회 실패 {type(e).__name__}"); return
    items = d.get("items", [])
    R["notes"].append("사이트 요청 " + (", ".join(f"{i['t']} {i['n']}명" for i in items) or "없음"))
    req = open(f"{MEDIA}/requests.md").read()
    for i in items:
        t = i["t"].upper()
        if re.search(rf"\|\s*대기[^|]*\|\s*{re.escape(t)}\s*\|", req): continue      # 이미 대기 행
        recent = False
        for f in glob.glob(f"{SITE}/content/reports/*.md"):
            h = open(f).read(1500)
            if re.search(rf"^ticker:\s*{re.escape(t)}\s*$", h, re.M):
                m = re.search(r"^data_as_of:\s*(\d{4}-\d{2}-\d{2})", h, re.M)
                if m and (NOW.date() - datetime.date.fromisoformat(m.group(1))).days <= 7: recent = True
        if not recent: R["escalate"].append({"ch": "site_request", "kind": "웹 요청", "ticker": t, "n": i["n"]})

def stats():
    if NOW.hour % 3 or not os.environ.get("YT_REFRESH_TOKEN"): return
    p = run(sys.executable, "tools/yt_stats.py", timeout=900)
    if p.returncode: R["notes"].append("통계 실패"); return
    if not DRY: commit_push(MEDIA, BR, ["stats_snapshots.jsonl"], "통계 스냅샷 갱신")
    R["notes"].append("통계 스냅샷 갱신")

if __name__ == "__main__":
    run("git", "pull", "-q", "--rebase", "origin", BR)
    run("git", "pull", "-q", "--rebase", "origin", "main", cwd=SITE)
    AI = ai_state()
    for fn in (youtube, site, sns, site_requests, stats):
        try: fn()
        except Exception as e: R["notes"].append(f"{fn.__name__} 오류 {type(e).__name__}: {str(e)[:100]}")
    if R.get("hold"): R["notes"].append(f"AI 답글 대기 {R['hold']}")
    auto_n = sum(1 for a in R["auto"] if a.get("reply"))
    head = f"{NOW:%m/%d %H:%M} ET · 자동 답글 {auto_n} · " + " · ".join(R["notes"])
    if not R["escalate"]:
        print("NOTHING " + head)
        for a in R["auto"]: print(f"  자동 {a['ch']} {a['kind']}: {a['text'][:25]} → {(a.get('reply') or a.get('skip',''))[:30]} {'' if a.get('ok', True) else '실패'}")
    else:
        print(f"ACTION 넘김 {len(R['escalate'])} · " + head)
        for a in R["auto"]: print(f"  자동 {a['ch']} {a['kind']}: {a['text'][:25]} → {(a.get('reply') or a.get('skip',''))[:30]}")
        print(json.dumps(R["escalate"], ensure_ascii=False))
