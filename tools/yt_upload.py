# 유튜브 자동 업로드: <티커>/upload.json 이 있고 <티커>/upload_result.json 이 없는 폴더를 올린다.
# upload.json 예시:
# {"title":"...", "description":"...", "tags":["..."], "categoryId":"27", "privacy":"public",
#  "video":"serv_slide_video.mp4", "thumbnail":"serv_thumbnail.jpg", "first_comment":"...",
#  "madeForKids":false, "publishAt":""}   # publishAt(UTC ISO8601)를 넣으면 private 예약 공개
# 영상 하나 바로 올리기: python tools/yt_upload.py --video a.mp4 --title "제목" [--description ... --tags a,b
#   --privacy private|unlisted|public --thumbnail t.jpg --comment "첫 댓글"]
import argparse, glob, json, os, sys, time, datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

need = ["YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"]
missing = [k for k in need if not os.environ.get(k)]
ap = argparse.ArgumentParser()
ap.add_argument("--video"); ap.add_argument("--title"); ap.add_argument("--description", default="")
ap.add_argument("--tags", default=""); ap.add_argument("--privacy", default="private",
                                                       choices=["private", "unlisted", "public"])
ap.add_argument("--category", default="27"); ap.add_argument("--thumbnail"); ap.add_argument("--comment")
args = ap.parse_args()
if missing:  # 설정 전에는 조용히 끝낸다(예약 실행이 매번 실패 메일을 보내지 않게)
    print("깃허브 Secrets가 아직 없습니다: " + ", ".join(missing)); sys.exit(1 if args.video else 0)

creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"],
                    client_id=os.environ["YT_CLIENT_ID"], client_secret=os.environ["YT_CLIENT_SECRET"],
                    token_uri="https://oauth2.googleapis.com/token",
                    scopes=["https://www.googleapis.com/auth/youtube.upload",
                            "https://www.googleapis.com/auth/youtube.force-ssl"])
yt = build("youtube", "v3", credentials=creds, cache_discovery=False)

def upload(folder, m):
    res = {"started": datetime.datetime.utcnow().isoformat() + "Z"}
    status = {"privacyStatus": m.get("privacy", "public"),
              "selfDeclaredMadeForKids": bool(m.get("madeForKids", False))}
    if m.get("publishAt"):
        status.update(privacyStatus="private", publishAt=m["publishAt"])
    body = {"snippet": {"title": m["title"][:100], "description": m.get("description", "")[:5000],
                        "tags": m.get("tags", []), "categoryId": str(m.get("categoryId", "27")),
                        "defaultLanguage": "ko", "defaultAudioLanguage": "ko"},
            "status": status}
    media = MediaFileUpload(os.path.join(folder, m["video"]), chunksize=8 * 1024 * 1024, resumable=True, mimetype="video/mp4")
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media, notifySubscribers=True)
    resp = None
    while resp is None:
        st, resp = req.next_chunk(num_retries=5)
        if st: print(f"{folder}: {int(st.progress() * 100)}%", flush=True)
    vid = resp["id"]
    res.update(video_id=vid, url=f"https://www.youtube.com/watch?v={vid}",
               privacy=resp.get("status", {}).get("privacyStatus"))
    print(folder, "uploaded", res["url"], res["privacy"], flush=True)
    if m.get("thumbnail"):
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(os.path.join(folder, m["thumbnail"]))).execute()
            res["thumbnail"] = "ok"
        except HttpError as e:
            res["thumbnail"] = f"error: {e}"
    if m.get("first_comment"):
        for attempt in range(3):
            try:
                c = yt.commentThreads().insert(part="snippet", body={"snippet": {"videoId": vid,
                        "topLevelComment": {"snippet": {"textOriginal": m["first_comment"]}}}}).execute()
                res["comment_id"] = c["id"]; res["comment"] = "ok"; break
            except HttpError as e:
                res["comment"] = f"error: {e}"; time.sleep(20)
    res["finished"] = datetime.datetime.utcnow().isoformat() + "Z"
    return res

if args.video:
    if not args.title: sys.exit("--title 이 필요합니다")
    m = {"video": args.video, "title": args.title, "description": args.description,
         "tags": [t.strip() for t in args.tags.split(",") if t.strip()], "categoryId": args.category,
         "privacy": args.privacy, "thumbnail": args.thumbnail, "first_comment": args.comment}
    print(json.dumps(upload(".", m), ensure_ascii=False, indent=1))
    sys.exit(0)

failed = False
for mf in sorted(glob.glob("*/upload.json")):
    folder = os.path.dirname(mf)
    out = os.path.join(folder, "upload_result.json")
    if os.path.exists(out):
        continue
    m = json.load(open(mf, encoding="utf-8"))
    err = os.path.join(folder, "upload_error.json")
    if os.path.exists(err) and time.time() - os.path.getmtime(err) < 3600 and os.environ.get("GITHUB_EVENT_NAME") == "schedule":
        continue  # 최근 1시간 안에 실패했으면 예약 실행에서는 건너뛴다
    try:
        r = upload(folder, m)
    except Exception as e:  # 실패하면 오류 파일을 남기고 다음 실행에서 다시 시도한다
        failed = True
        print(folder, "FAILED", e, flush=True)
        json.dump({"error": str(e), "at": datetime.datetime.utcnow().isoformat() + "Z"},
                  open(err, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        continue
    if os.path.exists(err): os.remove(err)
    json.dump(r, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
sys.exit(1 if failed else 0)
