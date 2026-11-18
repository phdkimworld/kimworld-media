"""구독 전환 시험 도구(운영자 지시 2026-11-17 "1 3만 수행" — 1번: 구독 전환 올리기).

사용 (yt_api_upload.py와 같은 YT_REFRESH_TOKEN·YT_CLIENT_ID·YT_CLIENT_SECRET 환경 변수):
  python3 tools/yt_subs.py --report 7            최근 7일 영상별 조회·구독 증가(YouTube Analytics). 권한이 없으면 채널 전체 구독자 수만
  python3 tools/yt_subs.py --watermark            모든 영상 오른쪽 아래 '구독' 워터마크(브랜딩) 설정 — 한 번만
  python3 tools/yt_subs.py --watermark --dry-run  워터마크 이미지만 만들어 경로 출력

결과는 JSON 한 줄. --report 결과는 review/sub_test.md 판정(12-01)에 쓴다.
"""
import argparse, datetime as dt, json, os, sys

ap = argparse.ArgumentParser()
ap.add_argument("--report", type=int, metavar="DAYS")
ap.add_argument("--watermark", action="store_true")
ap.add_argument("--dry-run", action="store_true")
a = ap.parse_args()
out = {}


def done(code=0):
    print(json.dumps(out, ensure_ascii=False)); sys.exit(code)


def mark_png(path):
    from PIL import Image, ImageDraw, ImageFont
    S = 300; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=64, fill=(204, 0, 0, 255))
    f = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc", 104, index=1)
    w = d.textlength("구독", font=f); d.text(((S - w) / 2, 84), "구독", font=f, fill=(255, 255, 255, 255))
    im.save(path); return path


if a.watermark and a.dry_run:
    out["png"] = mark_png(os.path.abspath("subscribe_mark.png")); done()

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    cred = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], client_id=os.environ["YT_CLIENT_ID"],
                       client_secret=os.environ["YT_CLIENT_SECRET"], token_uri="https://oauth2.googleapis.com/token")
    yt = build("youtube", "v3", cache_discovery=False, credentials=cred)
    ch = yt.channels().list(part="statistics", mine=True).execute()["items"][0]
    out["channel_id"] = ch["id"]; out["subscribers"] = int(ch["statistics"].get("subscriberCount", 0))
    out["views_total"] = int(ch["statistics"].get("viewCount", 0))
except Exception as e:
    out["error"] = f"auth: {e}"; done(2)

if a.watermark:
    try:
        png = mark_png(os.path.abspath("subscribe_mark.png"))
        # googleapiclient(httplib2)가 빈 응답 압축 해제에서 'range() arg 3 must not be zero'로 죽음(11-18) → requests로 직접 multipart 업로드
        import requests
        from google.auth.transport.requests import Request
        cred.refresh(Request())
        meta = json.dumps({"timing": {"type": "offsetFromStart", "offsetMs": 0}, "position": {"type": "corner", "cornerPosition": "bottomRight"}})
        r = requests.post("https://www.googleapis.com/upload/youtube/v3/watermarks/set",
                          params={"channelId": out["channel_id"], "uploadType": "multipart"},
                          headers={"Authorization": f"Bearer {cred.token}"},
                          files={"metadata": ("metadata", meta, "application/json; charset=UTF-8"), "media": ("mark.png", open(png, "rb"), "image/png")},
                          timeout=60)
        if r.status_code >= 300:
            raise RuntimeError(f"HTTP {r.status_code} {r.text[:150]}")
        out["watermark"] = "set"
    except Exception as e:
        out["watermark"] = f"실패: {str(e)[:200]} (운영자가 Studio > 맞춤설정 > 브랜딩 > 동영상 워터마크에서 넣는다)"
    done()

if a.report:
    end = dt.date.today(); start = end - dt.timedelta(days=a.report)
    try:
        ya = build("youtubeAnalytics", "v2", cache_discovery=False, credentials=cred)
        r = ya.reports().query(ids="channel==MINE", startDate=start.isoformat(), endDate=end.isoformat(),
                               metrics="views,subscribersGained,subscribersLost", dimensions="video", sort="-views", maxResults=50).execute()
        out["videos"] = [{"id": v, "views": vw, "gained": g, "lost": l, "per1k": round(g / vw * 1000, 2) if vw else None} for v, vw, g, l in r.get("rows", [])]
        t = ya.reports().query(ids="channel==MINE", startDate=start.isoformat(), endDate=end.isoformat(), metrics="views,subscribersGained,subscribersLost").execute()
        vw, g, l = (t.get("rows") or [[0, 0, 0]])[0]
        out["total"] = {"views": vw, "gained": g, "lost": l, "net_per1k": round((g - l) / vw * 1000, 2) if vw else None}
    except Exception as e:
        out["analytics"] = f"못 읽음: {str(e)[:160]} (토큰에 yt-analytics.readonly 권한이 없으면 채널 구독자 수 변화로만 판정)"
    done()
done()
