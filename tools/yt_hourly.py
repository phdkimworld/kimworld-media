# 채널 공개 영상 전체의 누적 조회수 합계를 한 줄로 기록한다(매시 GitHub Actions에서 실행).
# 연속한 두 기록의 차이 = 그 시간대에 채널이 얻은 조회수. tools/hotspots.py가 요일·시각별로 묶어 핫스팟을 낸다.
# 인증: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (Data API, youtube.force-ssl 범위면 충분)
# 사용: python3 tools/yt_hourly.py [기록 파일=hourly_views.jsonl]
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yt_stats import token, get as _get
import time

def get(tok, path, **q):
    for i in range(4):
        try: return _get(tok, path, **q)
        except Exception:
            if i == 3: raise
            time.sleep(5 * (i + 1))

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hourly_views.jsonl')
    tok = token(); now = datetime.datetime.now(datetime.timezone.utc)
    up = get(tok, 'channels', part='contentDetails', mine='true')['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    ids, pt = [], None
    while True:
        r = get(tok, 'playlistItems', part='contentDetails', playlistId=up, maxResults=50, **({'pageToken': pt} if pt else {}))
        ids += [i['contentDetails']['videoId'] for i in r['items']]; pt = r.get('nextPageToken')
        if not pt: break
    total = n = 0; fresh = {}
    for k in range(0, len(ids), 50):
        for v in get(tok, 'videos', part='statistics,status,snippet', id=','.join(ids[k:k + 50]))['items']:
            if v['status'].get('privacyStatus') != 'public': continue
            c = int(v['statistics'].get('viewCount', 0)); total += c; n += 1
            pub = datetime.datetime.fromisoformat(v['snippet']['publishedAt'].replace('Z', '+00:00'))
            if (now - pub).total_seconds() < 72 * 3600: fresh[v['id']] = c   # 공개 3일 이내 영상은 개별로도 남긴다(첫 72시간 곡선)
    with open(out, 'a') as f:
        f.write(json.dumps({'t': now.isoformat(timespec='seconds'), 'total': total, 'n': n, 'fresh': fresh}) + '\n')
    print(json.dumps({'t': now.isoformat(timespec='seconds'), 'total': total, 'n': n, 'fresh': len(fresh)}))

if __name__ == '__main__':
    main()
