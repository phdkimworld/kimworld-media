import argparse, json, os, sys, time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

ap = argparse.ArgumentParser()
ap.add_argument("--check", action="store_true"); ap.add_argument("--meta"); ap.add_argument("--video")
ap.add_argument("--thumbnail"); ap.add_argument("--delete"); ap.add_argument("--comment-only")
ap.add_argument("--status", help="영상 ID의 공개 상태·예약 시각 확인")
ap.add_argument("--publish-now", help="예약(비공개+publishAt) 영상을 지금 바로 공개로 바꾼다")
ap.add_argument("--retag", help="이미 올린 영상의 설명란·채널 첫 댓글 링크에 UTM을 붙인다")
ap.add_argument("--fix-recent", type=int, help="최근 N개 업로드의 언어를 한국어로 맞추고 롱폼(3분 초과)을 재생목록에 넣는다")
ap.add_argument("--dry-run", action="store_true", help="--fix-recent에서 바꾸지 않고 대상 수만 센다")
ap.add_argument("--playlist-title", default="나스닥 내러티브 팟캐스트", help="롱폼을 넣을 재생목록 이름(운영자 지시 2026-10-15)")
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

# 운영자 지시(2026-10-15): 영상 언어는 항상 한국어, 롱폼만 '나스닥 내러티브 팟캐스트' 재생목록에 넣는다
def playlist_id():
    pt = None
    while True:
        r = yt.playlists().list(part="snippet", mine=True, maxResults=50, **({"pageToken": pt} if pt else {})).execute()
        for p in r.get("items", []):
            if p["snippet"]["title"].strip() == a.playlist_title: return p["id"]
        pt = r.get("nextPageToken")
        if not pt: return None

def playlist_videos(pid):
    ids, pt = set(), None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=pid, maxResults=50, **({"pageToken": pt} if pt else {})).execute()
        ids |= {i["contentDetails"]["videoId"] for i in r.get("items", [])}
        pt = r.get("nextPageToken")
        if not pt: return ids

def ensure_korean(vid):
    sn = yt.videos().list(part="snippet", id=vid).execute()["items"][0]["snippet"]
    if sn.get("defaultLanguage") == "ko" and sn.get("defaultAudioLanguage") == "ko": return "ko"
    yt.videos().update(part="snippet", body={"id": vid, "snippet": {"title": sn["title"], "description": sn["description"],
        "categoryId": sn["categoryId"], "tags": sn.get("tags", []), "defaultLanguage": "ko", "defaultAudioLanguage": "ko"}}).execute()
    return "ko (고침)"

def add_to_playlist(pid, vid):
    yt.playlistItems().insert(part="snippet", body={"snippet": {"playlistId": pid,
        "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()

if a.fix_recent:
    import re as _re
    def secs(d):
        mo = _re.match(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', d); dd, h, mi, se = (int(x or 0) for x in mo.groups())
        return dd * 86400 + h * 3600 + mi * 60 + se
    up = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, pt = [], None
    while len(ids) < a.fix_recent:
        r = yt.playlistItems().list(part="contentDetails", playlistId=up, maxResults=50, **({"pageToken": pt} if pt else {})).execute()
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]; pt = r.get("nextPageToken")
        if not pt: break
    ids = ids[:a.fix_recent]
    pid = playlist_id(); out["playlist"] = pid or f"'{a.playlist_title}' 없음"
    have = playlist_videos(pid) if pid else set()
    fixed_lang, added, longs, errs = 0, 0, 0, []
    for k in range(0, len(ids), 50):
        for v in yt.videos().list(part="snippet,contentDetails", id=",".join(ids[k:k + 50])).execute()["items"]:
            try:
                sn = v["snippet"]
                if not (sn.get("defaultLanguage") == "ko" and sn.get("defaultAudioLanguage") == "ko"):
                    a.dry_run or ensure_korean(v["id"]); fixed_lang += 1
                if secs(v["contentDetails"]["duration"]) > 180:
                    longs += 1
                    if pid and v["id"] not in have: a.dry_run or add_to_playlist(pid, v["id"]); added += 1
            except HttpError as e:
                errs.append(f"{v['id']}: {str(e)[:120]}")
                if "quota" in str(e).lower(): break
    out.update(dry_run=a.dry_run, checked=len(ids), language_fixed=fixed_lang, longform=longs, playlist_added=added, errors=errs[:5]); done()
if a.publish_now:
    v = yt.videos().list(part="status", id=a.publish_now).execute()["items"][0]
    st = v["status"]; st.pop("publishAt", None); st["privacyStatus"] = "public"
    yt.videos().update(part="status", body={"id": a.publish_now, "status": st}).execute()
    st = yt.videos().list(part="status", id=a.publish_now).execute()["items"][0]["status"]
    out.update(video_id=a.publish_now, privacy=st["privacyStatus"], publish_at=st.get("publishAt")); done()
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
    m["first_comment"] = utm(m["first_comment"], (m["utm_content"] + "_pinned") if m.get("utm_content") else "pinned")

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
try:
    out["language"] = ensure_korean(vid)
except HttpError as e:
    out["language"] = f"error: {e}"
# 롱폼만 재생목록에(쇼츠는 설명에 #Shorts가 있다). meta에 "playlist": false로 끌 수 있다
if m.get("playlist", True) and "#Shorts" not in m["description"]:
    try:
        pid = playlist_id()
        if pid: add_to_playlist(pid, vid); out["playlist"] = "ok"
        else: out["playlist"] = f"'{a.playlist_title}' 재생목록 없음"
    except HttpError as e:
        out["playlist"] = f"error: {e}"
done()
