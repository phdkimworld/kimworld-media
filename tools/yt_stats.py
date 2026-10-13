# 김박사 월드 채널의 모든 업로드와 조회수를 YouTube Data API로 받아 종목 선정 지침(3장 업무 1)용 표를 만든다.
# 인증: 환경 변수 YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (업로드와 같은 토큰, youtube.force-ssl 범위)
# 사용: python3 yt_stats.py [스냅숏 파일=stats_snapshots.jsonl]
#  - 매 실행마다 영상별 누적 조회수를 스냅숏 파일에 한 줄로 추가하고,
#    직전 스냅숏과 비교한 '최근 VPH'(시간당 조회수)와 공개 이후 평균 VPH를 함께 계산한다
#  - 롱폼만(길이 180초 초과) 종목별로 묶어 마지막 업데이트일과 등급(🔴/🟡/✅)을 출력한다
import os, re, sys, json, datetime, urllib.request, urllib.parse

def token():
    d = urllib.parse.urlencode({'client_id': os.environ['YT_CLIENT_ID'], 'client_secret': os.environ['YT_CLIENT_SECRET'],
                                'refresh_token': os.environ['YT_REFRESH_TOKEN'], 'grant_type': 'refresh_token'}).encode()
    return json.load(urllib.request.urlopen('https://oauth2.googleapis.com/token', d))['access_token']

def get(tok, path, **q):
    u = 'https://www.googleapis.com/youtube/v3/' + path + '?' + urllib.parse.urlencode(q)
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'Authorization': 'Bearer ' + tok})))

def dur(s):
    m = re.match(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', s); d, h, mi, se = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + se

ALIAS = {'GRHL': 'GRML', 'VS': 'VST', 'SDEOV': 'SDEV'}  # 제목 해시태그 오기·옛 표기를 같은 종목으로 묶는다

def ticker(title):
    m = re.search(r'#\s*([A-Z0-9]{1,6})\s*$', title.strip())
    return ALIAS.get(m.group(1), m.group(1)) if m else None

def main():
    snap = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stats_snapshots.jsonl')
    tok = token(); now = datetime.datetime.now(datetime.timezone.utc)
    ch = get(tok, 'channels', part='contentDetails', mine='true')['items'][0]
    up = ch['contentDetails']['relatedPlaylists']['uploads']
    ids, pt = [], None
    while True:
        r = get(tok, 'playlistItems', part='contentDetails', playlistId=up, maxResults=50, **({'pageToken': pt} if pt else {}))
        ids += [i['contentDetails']['videoId'] for i in r['items']]; pt = r.get('nextPageToken')
        if not pt: break
    vids = []
    for k in range(0, len(ids), 50):
        r = get(tok, 'videos', part='snippet,statistics,contentDetails,status', id=','.join(ids[k:k + 50]))
        for v in r['items']:
            if v['status'].get('privacyStatus') != 'public': continue
            vids.append({'id': v['id'], 'title': v['snippet']['title'], 'pub': v['snippet']['publishedAt'],
                         'views': int(v['statistics'].get('viewCount', 0)), 'sec': dur(v['contentDetails']['duration'])})
    prev = {}
    if os.path.exists(snap):
        lines = [json.loads(l) for l in open(snap) if l.strip()]
        if lines: prev = lines[-1]
    with open(snap, 'a') as f:
        f.write(json.dumps({'t': now.isoformat(), 'v': {x['id']: x['views'] for x in vids}}) + '\n')
    dt_prev = (now - datetime.datetime.fromisoformat(prev['t'])).total_seconds() / 3600 if prev else None
    for x in vids:
        p = datetime.datetime.fromisoformat(x['pub'].replace('Z', '+00:00'))
        x['age_h'] = (now - p).total_seconds() / 3600
        x['vph_avg'] = x['views'] / max(x['age_h'], 1)
        pv = prev.get('v', {}).get(x['id']) if prev else None
        x['vph_recent'] = (x['views'] - pv) / dt_prev if (pv is not None and dt_prev and dt_prev > 0.2) else None
        x['tk'] = ticker(x['title'])
    longs = [x for x in vids if x['sec'] > 180 and x['tk']]
    by = {}
    for x in longs: by.setdefault(x['tk'], []).append(x)
    rows = []
    for tk, vs in by.items():
        vs.sort(key=lambda x: x['pub']); last = vs[-1]; age_d = last['age_h'] / 24
        old = [x for x in vs if x['age_h'] > 7 * 24]
        grade = '🔴' if age_d > 7 else ('🟡' if age_d >= 5 else '✅')
        best_old = max(old, key=lambda x: (x['vph_recent'] if x['vph_recent'] is not None else x['vph_avg'])) if old else None
        rows.append({'ticker': tk, 'grade': grade, 'last_pub': last['pub'], 'days': round(age_d, 1),
                     'expires': (datetime.datetime.fromisoformat(last['pub'].replace('Z', '+00:00')) + datetime.timedelta(days=7)).isoformat(),
                     'latest_vph_recent': last['vph_recent'], 'latest_vph_avg': round(last['vph_avg'], 2), 'latest_views': last['views'],
                     'old_vph_recent': best_old['vph_recent'] if best_old else None, 'old_vph_avg': round(best_old['vph_avg'], 2) if best_old else None,
                     'total_views': sum(x['views'] for x in vs), 'n': len(vs)})
    key = lambda r: (r['old_vph_recent'] if r['old_vph_recent'] is not None else r['old_vph_avg'] or 0)
    red = sorted([r for r in rows if r['grade'] == '🔴'], key=lambda r: -key(r))
    yel = sorted([r for r in rows if r['grade'] == '🟡'], key=lambda r: (r['expires'][:10], -(r['latest_vph_recent'] if r['latest_vph_recent'] is not None else r['latest_vph_avg'])))
    out = {'now': now.isoformat(), 'videos': len(vids), 'long_videos': len(longs), 'recent_window_h': round(dt_prev, 2) if dt_prev else None,
           'red': red, 'yellow': yel, 'fresh': sorted(r['ticker'] for r in rows if r['grade'] == '✅')}
    print(json.dumps(out, ensure_ascii=False, indent=1))

if __name__ == '__main__':
    main()
