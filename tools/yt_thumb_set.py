"""이미 올린 영상의 썸네일만 바꾼다(YouTube Data API thumbnails.set, 50단위) — 2026-11-24 운영자 "왜 바뀐 게 하나도 없어" 소급 교체용.
사용: python3 tools/yt_thumb_set.py <videoId> <jpg>     → 바꾼 뒤 videos.list(1단위)로 확인해 JSON 한 줄 출력
      python3 tools/yt_thumb_set.py --info <id> [<id>…]  → 제목·공개 시각·길이·썸네일 주소만 출력(바꾸지 않음)
인증: yt_api_upload.py와 같은 YT_CLIENT_ID/YT_CLIENT_SECRET/YT_REFRESH_TOKEN(값은 출력하지 않는다).
되돌림: 교체 전 i.ytimg.com maxresdefault를 review/thumb_backup/<videoId>.jpg에 받아 두고 같은 명령으로 다시 올린다.
실패하면 다시 시도하지 않는다(할당량 보호) — 결과의 error를 보고한다."""
import json, os, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def yt():
    return build("youtube", "v3", cache_discovery=False, credentials=Credentials(None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"], client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"], token_uri="https://oauth2.googleapis.com/token"))

def info(api, ids):
    r = api.videos().list(part="snippet,contentDetails,status", id=",".join(ids), maxResults=50).execute()
    return [{"id": it["id"], "title": it["snippet"]["title"], "published": it["snippet"]["publishedAt"],
             "duration": it["contentDetails"]["duration"], "privacy": it["status"]["privacyStatus"],
             "thumb": (it["snippet"]["thumbnails"].get("maxres") or it["snippet"]["thumbnails"]["high"])["url"]}
            for it in r.get("items", [])]

def main(argv):
    if not argv:
        print(__doc__); return 2
    try:
        api = yt()
    except Exception as e:
        print(json.dumps({"error": f"auth: {type(e).__name__}"}, ensure_ascii=False)); return 2
    if argv[0] == "--info":
        print(json.dumps(info(api, argv[1:]), ensure_ascii=False)); return 0
    vid, jpg = argv[0], argv[1]
    out = {"video": vid, "file": jpg}
    if len(vid) != 11:
        out["error"] = "영상 ID는 11자"; print(json.dumps(out, ensure_ascii=False)); return 2
    head = open(jpg, "rb").read(3)
    size = os.path.getsize(jpg)
    if head != b"\xff\xd8\xff" or size > 2 * 1024 * 1024:
        out["error"] = f"jpg 2MB 이하만(지금 {size}바이트, jpg={head == b'\xff\xd8\xff'})"; print(json.dumps(out, ensure_ascii=False)); return 2
    try:
        api.thumbnails().set(videoId=vid, media_body=MediaFileUpload(jpg, mimetype="image/jpeg")).execute()
        out["set"] = "ok"
    except Exception as e:
        out["error"] = f"set: {str(e)[:300]}"; print(json.dumps(out, ensure_ascii=False)); return 3
    try:
        out["check"] = info(api, [vid])[0]
    except Exception as e:
        out["check_error"] = str(e)[:200]
    print(json.dumps(out, ensure_ascii=False)); return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
