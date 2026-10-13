# YouTube Analytics API(yt-analytics.readonly 범위)로 채널 지표를 받아 analytics/latest.json에 저장한다.
# 인증: YT_ANALYTICS_REFRESH_TOKEN(없으면 YT_REFRESH_TOKEN). 이 토큰을 다른 OAuth 클라이언트로 받았다면
#       YT_ANALYTICS_CLIENT_ID·YT_ANALYTICS_CLIENT_SECRET도 넣는다(없으면 YT_CLIENT_ID·YT_CLIENT_SECRET)
#  - 일별 조회수·시청 시간·구독자 증감(최근 90일), 시청자 연령·성별, 국가, 유입 경로, 기기
#  - API에는 '시간대(시)' 차원이 없다. 요일·시각 핫스팟은 tools/yt_hourly.py + tools/hotspots.py로 직접 잰다
# 사용: python3 tools/yt_analytics.py [--days 90]
import os, sys, json, datetime, urllib.request, urllib.parse, urllib.error

def token():
    rt = os.environ.get('YT_ANALYTICS_REFRESH_TOKEN') or os.environ['YT_REFRESH_TOKEN']
    d = urllib.parse.urlencode({'client_id': os.environ.get('YT_ANALYTICS_CLIENT_ID') or os.environ['YT_CLIENT_ID'],
                                'client_secret': os.environ.get('YT_ANALYTICS_CLIENT_SECRET') or os.environ['YT_CLIENT_SECRET'],
                                'refresh_token': rt, 'grant_type': 'refresh_token'}).encode()
    return json.load(urllib.request.urlopen('https://oauth2.googleapis.com/token', d))

def q(tok, **p):
    u = 'https://youtubeanalytics.googleapis.com/v2/reports?' + urllib.parse.urlencode(dict(ids='channel==MINE', **p))
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'Authorization': 'Bearer ' + tok})))
        cols = [h['name'] for h in r.get('columnHeaders', [])]
        return [dict(zip(cols, row)) for row in r.get('rows', [])]
    except urllib.error.HTTPError as e:
        return {'error': e.code, 'detail': json.loads(e.read() or b'{}').get('error', {}).get('message')}

def main():
    days = int(sys.argv[sys.argv.index('--days') + 1]) if '--days' in sys.argv else 90
    t = token()
    if 'yt-analytics' not in t.get('scope', ''):
        print(json.dumps({'error': 'scope', 'scope': t.get('scope'), 'hint': 'yt-analytics.readonly 범위가 든 refresh token을 YT_ANALYTICS_REFRESH_TOKEN에 넣는다'}, ensure_ascii=False)); sys.exit(2)
    tok = t['access_token']; end = datetime.date.today() - datetime.timedelta(days=1); start = end - datetime.timedelta(days=days - 1)
    rng = dict(startDate=start.isoformat(), endDate=end.isoformat())
    out = {'generated': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'), **rng,
           'daily': q(tok, metrics='views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost', dimensions='day', sort='day', **rng),
           'demographics': q(tok, metrics='viewerPercentage', dimensions='ageGroup,gender', sort='-viewerPercentage', **rng),
           'country': q(tok, metrics='views,estimatedMinutesWatched', dimensions='country', sort='-views', maxResults=15, **rng),
           'traffic': q(tok, metrics='views,estimatedMinutesWatched', dimensions='insightTrafficSourceType', sort='-views', **rng),
           'device': q(tok, metrics='views', dimensions='deviceType', sort='-views', **rng),
           'top_videos': q(tok, metrics='views,estimatedMinutesWatched,averageViewPercentage', dimensions='video', sort='-views', maxResults=25, **rng)}
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'analytics'); os.makedirs(d, exist_ok=True)
    json.dump(out, open(os.path.join(d, 'latest.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in out.items()}, ensure_ascii=False))

if __name__ == '__main__':
    main()
