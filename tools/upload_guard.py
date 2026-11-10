"""업로드 직전 중복 검사(72회차 LCID, 11-10 중복 업로드 4편 재발 방지).

사용: python3 tools/upload_guard.py <upload_meta.json> [--hours 48]
  채널 최근 업로드(업로드 재생목록 50개)에서 meta 제목과 같은 영상을 찾는다.
  - 같은 제목이 최근 N시간 안에 있으면 'DUP <영상ID>'를 찍고 종료 코드 1 → 재시도 루프는 업로드하지 않고 그 ID를 쓴다.
  - 없으면 'NO_DUP' 종료 코드 0. 인증·네트워크 오류는 'GUARD_ERR …' 종료 코드 2(루프는 업로드를 미룬다).
할당량은 호출당 약 2단위(channels.list + playlistItems.list).
"""
import datetime, json, os, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

meta = json.load(open(sys.argv[1], encoding="utf-8"))
hours = float(sys.argv[sys.argv.index("--hours") + 1]) if "--hours" in sys.argv else 48.0
norm = lambda s: " ".join(s.split())[:100]
try:
    yt = build("youtube", "v3", cache_discovery=False, credentials=Credentials(None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"], client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"], token_uri="https://oauth2.googleapis.com/token"))
    up = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    items = yt.playlistItems().list(part="snippet", playlistId=up, maxResults=50).execute().get("items", [])
except Exception as e:
    print(f"GUARD_ERR {e}"[:300]); sys.exit(2)
cut = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours)
want = norm(meta["title"])
for it in items:
    sn = it["snippet"]
    when = datetime.datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00"))
    if norm(sn["title"]) == want and when >= cut:
        print(f"DUP {sn['resourceId']['videoId']} {sn['publishedAt']}"); sys.exit(1)
print(f"NO_DUP 최근 {len(items)}개 확인")
