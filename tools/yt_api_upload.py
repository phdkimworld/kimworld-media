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
ap.add_argument("--edit", help="이미 올린 영상 ID: --meta의 제목·설명·첫 댓글로 고친다(독립 검토 반영용, 2026-10-16)")
ap.add_argument("--playlist-title", default="나스닥 내러티브 팟캐스트", help="롱폼을 넣을 재생목록 이름(운영자 지시 2026-10-15)")
ap.add_argument("--series-backfill", nargs="?", const="ALL", help="핵심 종목(review/core_tickers.md) 지난 롱폼(사이트 리포트 youtube_id)을 '<시리즈> 미스터리 추적' 재생목록에 채운다. 티커 하나 또는 생략=전부. --dry-run 가능")
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
def playlist_id(title=None):
    title = title or a.playlist_title; pt = None
    while True:
        r = yt.playlists().list(part="snippet", mine=True, maxResults=50, **({"pageToken": pt} if pt else {})).execute()
        for p in r.get("items", []):
            if p["snippet"]["title"].strip() == title: return p["id"]
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

# 제작팀 권고안 R4(2026-11-16): 핵심 종목 롱폼은 '<시리즈 이름> 미스터리 추적' 재생목록(없으면 공개로 만든다)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core_tickers as _ct
def series_playlist(tk, name, create=True, exact=None):
    t = exact or f"{name} 미스터리 추적"; pid = playlist_id(t)
    if pid or not create: return pid, t
    r = yt.playlists().insert(part="snippet,status", body={"snippet": {"title": t, "defaultLanguage": "ko",
        "description": (f"{exact}: 판정이 끝난 지난 예측을 장부로 공개 채점하고, 틀린 이유와 고친 예측 규칙을 기록하는 연재입니다. 회차마다 기록표 전체는 무료 리포트에서: https://drkimworld.com" if exact else f"{name}({tk}) 주가 미스터리를 사건 순서대로 추적합니다. 회차마다 날짜별 기록표 전체는 무료 리포트 자료실에서: https://drkimworld.com")},
        "status": {"privacyStatus": "public"}}).execute()
    return r["id"], t

if a.series_backfill:
    core = _ct.load(); tks = list(core) if a.series_backfill == "ALL" else [a.series_backfill.upper()]
    import glob as _g, re as _r
    res = {}
    for tk in tks:
        if tk not in core: res[tk] = "핵심 종목 아님"; continue
        vids = []
        for f in _g.glob(os.path.join(_ct.SITE, "content/reports/*.md")):
            t = open(f, encoding="utf-8").read(4000)
            k = _r.search(r"^ticker:\s*['\"]?([^'\"\s]+)", t, _r.M); y = _r.search(r"^youtube_id:\s*['\"]?([\w-]{6,})", t, _r.M)
            d = _r.search(r"^data_as_of:\s*['\"]?(\d{4}-\d\d-\d\d)", t, _r.M)
            if k and y and k.group(1).upper() == tk: vids.append((d.group(1) if d else "", y.group(1)))
        vids = [v for _, v in sorted(set(vids))]
        pid, title = series_playlist(tk, core[tk], create=not a.dry_run)
        have = playlist_videos(pid) if pid else set(); todo = [v for v in vids if v not in have]
        if not a.dry_run:
            for v in todo:
                try: add_to_playlist(pid, v)
                except HttpError as e:
                    res[tk] = f"error: {str(e)[:120]}"; break
        res.setdefault(tk, f"'{title}' {'(만들 예정) ' if not pid else ''}지난 롱폼 {len(vids)}편 중 추가 {len(todo)}편")
    out.update(dry_run=a.dry_run, series=res); done()

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

# 사이트 링크에 유입 구분자(UTM)를 붙인다. 설명란=description(위치별 desc_top·desc_mid·desc_end), 첫 댓글=pinned
# 롱폼·쇼츠 구분(운영자 지시 2026-10-16): utm_medium=video(롱폼) / shorts(쇼츠). 이미 붙은 유튜브 UTM은 새 값으로 바꾼다
import re
def is_shorts(meta=None, desc="", seconds=None):
    if meta and (meta.get("shorts") or meta.get("utm_content") == "shorts"): return True
    if re.search(r"#shorts\b", desc or "", re.I): return True
    return seconds is not None and seconds <= 180
def utm(text, content, medium="video"):
    pat = r"https://drkimworld\.com/r/([a-z0-9-]+)/(?:\?utm_source=youtube[^\s)]*)?(?![?\w])"
    n = len(re.findall(pat, text)); i = [0]
    def f(mo):
        slug = mo.group(1); c = content
        if content == "description" and n > 1:
            c = "desc_top" if i[0] == 0 else ("desc_end" if i[0] == n - 1 else "desc_mid")
        i[0] += 1
        return (f"https://drkimworld.com/r/{slug}/?utm_source=youtube&utm_medium={medium}"
                f"&utm_campaign={slug}&utm_content={c}")
    return re.sub(pat, f, text)
def iso_sec(d):
    mo = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    return sum(int(x or 0) * k for x, k in zip(mo.groups(), (3600, 60, 1))) if mo else None

if a.retag:
    v = yt.videos().list(part="snippet,contentDetails", id=a.retag).execute()["items"][0]; sn = v["snippet"]
    med = "shorts" if is_shorts(desc=sn["description"], seconds=iso_sec(v["contentDetails"].get("duration"))) else "video"
    nd = utm(sn["description"], "description", med); out["video_id"] = a.retag; out["utm_medium"] = med
    if nd != sn["description"]:
        yt.videos().update(part="snippet", body={"id": a.retag, "snippet": {"title": sn["title"], "description": nd,
            "categoryId": sn["categoryId"], "tags": sn.get("tags", []), "defaultLanguage": sn.get("defaultLanguage", "ko")}}).execute()
        out["description"] = "tagged"
    me = yt.channels().list(part="id", mine=True).execute()["items"][0]["id"]
    for th in yt.commentThreads().list(part="snippet", videoId=a.retag, maxResults=50, order="time").execute()["items"]:
        c = th["snippet"]["topLevelComment"]; cs = c["snippet"]
        if cs.get("authorChannelId", {}).get("value") == me and "drkimworld.com/r/" in cs["textOriginal"]:
            nt = utm(cs["textOriginal"], "pinned", med)
            if nt != cs["textOriginal"]:
                yt.comments().update(part="snippet", body={"id": c["id"], "snippet": {"textOriginal": nt}}).execute()
                out["comment"] = "tagged"
    done()

if a.delete:
    yt.videos().delete(id=a.delete).execute(); out["deleted"] = a.delete; done()

m = json.load(open(a.meta, encoding="utf-8"))
MED = "shorts" if is_shorts(m, m.get("description", "")) else "video"
_pos = m.get("utm_content") if m.get("utm_content") not in (None, "shorts") else None
m["description"] = utm(m["description"], _pos or "description", MED)
if m.get("first_comment"):
    m["first_comment"] = utm(m["first_comment"], (_pos + "_pinned") if _pos else "pinned", MED)

if a.edit:
    v = yt.videos().list(part="snippet", id=a.edit).execute()["items"][0]; sn = v["snippet"]; out["video_id"] = a.edit
    yt.videos().update(part="snippet", body={"id": a.edit, "snippet": {"title": m["title"][:100], "description": m["description"][:5000],
        "categoryId": sn["categoryId"], "tags": m.get("tags", sn.get("tags", [])), "defaultLanguage": sn.get("defaultLanguage", "ko"),
        "defaultAudioLanguage": sn.get("defaultAudioLanguage", "ko")}}).execute()
    out["snippet"] = "updated"
    if m.get("first_comment"):
        me = yt.channels().list(part="id", mine=True).execute()["items"][0]["id"]
        for th in yt.commentThreads().list(part="snippet", videoId=a.edit, maxResults=50, order="time").execute()["items"]:
            c = th["snippet"]["topLevelComment"]; cs = c["snippet"]
            if cs.get("authorChannelId", {}).get("value") == me and "drkimworld.com/r/" in cs["textOriginal"]:
                if cs["textOriginal"] != m["first_comment"]:
                    yt.comments().update(part="snippet", body={"id": c["id"], "snippet": {"textOriginal": m["first_comment"]}}).execute()
                    out["comment"] = "updated"
                break
    done()

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
parts = "snippet,status"
if m.get("paid_promo"):  # SKILL V3.9 쿠팡 상품 안내(2026-11-10): 유료 프로모션 표시
    body["paidProductPlacementDetails"] = {"hasPaidProductPlacement": True}; parts += ",paidProductPlacementDetails"
try:
    req = yt.videos().insert(part=parts, body=body, notifySubscribers=True,
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
    # R4 시리즈 재생목록: meta "series": false로 끄고, "series": "<이름>"으로 이름을 바꾼다. 티커 = meta "ticker" 또는 제목의 '(티커)'
    core = _ct.load(); tk = (m.get("ticker") or _ct.ticker_from_title(m["title"]) or "").upper()
    if m.get("series_title"):
        pass  # 아래 연재 재생목록 블록(롱폼·쇼츠 공통)에서 넣는다
    elif m.get("series", True) is not False and (tk in core or isinstance(m.get("series"), str)):
        try:
            name = m["series"] if isinstance(m.get("series"), str) else core[tk]
            spid, stitle = series_playlist(tk, name); add_to_playlist(spid, vid); out["series_playlist"] = f"ok: {stitle}"
            # 11-27 운영자 공유 '유튜브 최적화 팁 3: 설명란에 재생목록 링크': 설명란에 이 종목 연재 재생목록 한 줄(없을 때만)
            try:
                _url = f"https://www.youtube.com/playlist?list={spid}"
                _v = yt.videos().list(part="snippet", id=vid).execute()["items"][0]["snippet"]
                if _url not in _v.get("description", ""):
                    _d = _v.get("description", "")
                    _line = f"▶ {stitle} 전편 모아 보기: {_url}"
                    _i = _d.find("\n#")
                    _d = (_d[:_i] + "\n" + _line + _d[_i:]) if _i > 0 else (_d + "\n\n" + _line)
                    yt.videos().update(part="snippet", body={"id": vid, "snippet": {"title": _v["title"], "description": _d[:5000],
                        "categoryId": _v["categoryId"], "tags": _v.get("tags", []), "defaultLanguage": _v.get("defaultLanguage", "ko")}}).execute()
                    out["desc_playlist_link"] = "ok"
            except HttpError as e:
                out["desc_playlist_link"] = f"error: {e}"
        except HttpError as e:
            out["series_playlist"] = f"error: {e}"
# 채널 연재(오답노트 등, 2026-11-18 운영자 "쇼츠도 '김박사 월드 오답노트' 재생목록에 추가"): meta "series_title"이면 '미스터리 추적'을 붙이지 않고
# 그 이름 그대로 찾거나 만들어 롱폼·쇼츠 모두 넣는다. 1편 롱폼에서 409 SERVICE_UNAVAILABLE이 한 번 나 20초 뒤 두 번 더 시도
if m.get("series_title"):
    for _k in range(3):
        try:
            spid, stitle = series_playlist("", "", exact=m["series_title"]); add_to_playlist(spid, vid); out["series_playlist"] = f"ok: {stitle}"; break
        except HttpError as e:
            out["series_playlist"] = f"error: {e}"; time.sleep(20)
# 한국어 자막(운영자 11-20, 시청의 25.6%가 자막을 켜고 봄): meta 폴더의 raw_timing.json(롱폼)·shorts_raw_timing.json(쇼츠)으로 SRT를 만들어 올린다.
# 실패해도 업로드는 그대로 둔다(결과 captions 한 줄만). meta "captions": false로 끈다. 손으로 다시: python3 tools/yt_captions.py <폴더>
if m.get("captions", True) is not False:
    try:
        import subprocess
        mdir = os.path.dirname(os.path.abspath(a.meta)); cap = os.path.join(os.path.dirname(os.path.realpath(__file__)), "yt_captions.py")
        if any(os.path.exists(os.path.join(mdir, f)) for f in ("raw_timing.json", "shorts_raw_timing.json")) and os.path.exists(cap):
            r = subprocess.run([sys.executable, cap, mdir, "--vid", vid], capture_output=True, text=True, timeout=300)
            out["captions"] = ((r.stdout.strip().splitlines() or [r.stderr.strip()[-200:]])[-1])[:200]
        else:
            out["captions"] = "skip: 타이밍 파일 없음"
    except Exception as e:
        out["captions"] = f"error: {str(e)[:150]}"
done()
