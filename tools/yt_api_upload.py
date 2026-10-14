import argparse, json, os, sys, time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

ap = argparse.ArgumentParser()
ap.add_argument("--check", action="store_true"); ap.add_argument("--meta"); ap.add_argument("--video")
ap.add_argument("--thumbnail"); ap.add_argument("--delete"); ap.add_argument("--comment-only")
ap.add_argument("--status", help="영상 ID의 공개 상태·예약 시각 확인")
ap.add_argument("--retag", help="이미 올린 영상의 설명란·채널 첫 댓글 링크에 UTM을 붙인다")
a = ap.parse_args()
out = {}

def done(code=0):
    print(json.dumps(out, ensure_ascii=False)); sys.exit(code)

try:
    yt = build("youtube", "v3", cache_discovery=False, credentials=Credentials(None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"], client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"], token_uri="https://oauth2.googleapis.com/token"))
    out["channel"] = yt.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
except Exception as e:
    out["error"] = f"auth: {e}"; done(2)
if a.check:
    done()
if a.status:
    st = yt.videos().list(part="status", id=a.status).execute()["items"][0]["status"]
    out.update(video_id=a.status, privacy=st["privacyStatus"], publish_at=st.get("publishAt")); done()

# 사이트 링크에 유입 구분자(UTM)를 붙인다. 설명란=description, 첫 댓글=pinned (쇼츠는 meta에 utm_content='shorts')
import re
def utm(text, content):
    def f(mo):
        slug = mo.group(1)
        return (f"https://drkimworld.com/r/{slug}/?utm_source=youtube&utm_medium=video"
                f"&utm_campaign={slug}&utm_content={content}")
    return re.sub(r"https://drkimworld\.com/r/([a-z0-9-]+)/(?!\?)", f, text)

if a.retag:
    v = yt.videos().list(part="snippet", id=a.retag).execute()["items"][0]; sn = v["snippet"]
    nd = utm(sn["description"], "description"); out["video_id"] = a.retag
    if nd != sn["description"]:
        yt.videos().update(part="snippet", body={"id": a.retag, "snippet": {"title": sn["title"], "description": nd,
            "categoryId": sn["categoryId"], "tags": sn.get("tags", []), "defaultLanguage": sn.get("defaultLanguage", "ko")}}).execute()
        out["description"] = "tagged"
    me = yt.channels().list(part="id", mine=True).execute()["items"][0]["id"]
    for th in yt.commentThreads().list(part="snippet", videoId=a.retag, maxResults=50, order="time").execute()["items"]:
        c = th["snippet"]["topLevelComment"]; cs = c["snippet"]
        if cs.get("authorChannelId", {}).get("value") == me and "drkimworld.com/r/" in cs["textOriginal"]:
            nt = utm(cs["textOriginal"], "pinned")
            if nt != cs["textOriginal"]:
                yt.comments().update(part="snippet", body={"id": c["id"], "snippet": {"textOriginal": nt}}).execute()
                out["comment"] = "tagged"
    done()

if a.delete:
    yt.videos().delete(id=a.delete).execute(); out["deleted"] = a.delete; done()

m = json.load(open(a.meta, encoding="utf-8"))
m["description"] = utm(m["description"], m.get("utm_content", "description"))
if m.get("first_comment"):
    m["first_comment"] = utm(m["first_comment"], "pinned")

def comment(vid):
    for _ in range(3):
        try:
            c = yt.commentThreads().insert(part="snippet", body={"snippet": {"videoId": vid,
                "topLevelComment": {"snippet": {"textOriginal": m["first_comment"]}}}}).execute()
            out.update(comment="ok", comment_id=c["id"]); return
        except HttpError as e:
            out["comment"] = f"error: {e}"; time.sleep(20)

if a.comment_only:
    out["video_id"] = a.comment_only; comment(a.comment_only); done()

status = {"privacyStatus": m.get("privacy", "public"), "selfDeclaredMadeForKids": False}
# 예약 공개: meta의 publish_at(RFC3339, 예 2026-10-14T10:00:00-04:00)이 10분 이상 뒤면 비공개로 올리고 그 시각에 자동 공개.
# 이미 지났거나 10분 안이면 바로 공개. 예약 공개 영상의 첫 댓글은 공개 뒤 --comment-only로 단다.
if m.get("publish_at"):
    from datetime import datetime, timezone, timedelta
    pa = datetime.fromisoformat(m["publish_at"])
    if pa - datetime.now(timezone.utc) > timedelta(minutes=10):
        status.update(privacyStatus="private", publishAt=pa.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        out["scheduled"] = status["publishAt"]
if m.get("synthetic"):
    status["containsSyntheticMedia"] = True
body = {"snippet": {"title": m["title"][:100], "description": m["description"][:5000], "tags": m["tags"],
                    "categoryId": "27", "defaultLanguage": "ko", "defaultAudioLanguage": "ko"},
        "status": status}
try:
    req = yt.videos().insert(part="snippet,status", body=body, notifySubscribers=True,
        media_body=MediaFileUpload(a.video, chunksize=8 * 1024 * 1024, resumable=True, mimetype="video/mp4"))
    resp = None
    while resp is None:
        _, resp = req.next_chunk(num_retries=5)
except Exception as e:
    out["error"] = f"upload: {e}"; done(3)

vid = resp["id"]
out.update(video_id=vid, url=f"https://www.youtube.com/watch?v={vid}", privacy_requested=status["privacyStatus"])
if a.thumbnail:
    try:
        yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(a.thumbnail)).execute(); out["thumbnail"] = "ok"
    except HttpError as e:
        out["thumbnail"] = f"error: {e}"
time.sleep(15)
out["privacy_after"] = yt.videos().list(part="status", id=vid).execute()["items"][0]["status"]["privacyStatus"]
if out["privacy_after"] != out["privacy_requested"]:
    out["locked"] = True; done(4)
if out["privacy_after"] != "private" and m.get("first_comment"):
    comment(vid)
done()
