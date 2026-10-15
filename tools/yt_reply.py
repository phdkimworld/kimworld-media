# 김박사 월드 채널 댓글에 답글을 단다(YouTube Data API).
# 인증: 업로드·yt_stats.py 와 같은 환경 변수 YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (youtube.force-ssl 범위). 값은 출력하지 않는다.
# 사용:
#   python3 yt_reply.py --list [--days 7] [--video VIDEO_ID] [--search 글자]
#       내 채널 영상의 댓글 스레드 가운데 내 채널 답글이 아직 없는 것을 JSON 으로 출력한다.
#       my_replies_24h 는 최근 24시간에 내 채널이 단 답글 수(하루 한도 확인용, 읽은 스레드 범위 안에서 센다).
#   python3 yt_reply.py --reply THREAD_ID --text-file 답글.txt
#       답글 1개를 단다. 성공하면 답글 ID 를 출력한다. 실패하면 다시 시도하지 않고 오류만 출력하고 1 로 끝난다.
import os, sys, json, argparse, datetime, urllib.request, urllib.parse, urllib.error

API = 'https://www.googleapis.com/youtube/v3/'

def token():
    d = urllib.parse.urlencode({'client_id': os.environ['YT_CLIENT_ID'], 'client_secret': os.environ['YT_CLIENT_SECRET'],
                                'refresh_token': os.environ['YT_REFRESH_TOKEN'], 'grant_type': 'refresh_token'}).encode()
    return json.load(urllib.request.urlopen('https://oauth2.googleapis.com/token', d))['access_token']

def call(tok, path, body=None, **q):
    req = urllib.request.Request(API + path + '?' + urllib.parse.urlencode(q), headers={'Authorization': 'Bearer ' + tok},
                                 data=json.dumps(body).encode() if body is not None else None)
    if body is not None: req.add_header('Content-Type', 'application/json')
    return json.load(urllib.request.urlopen(req))

def err(e):
    try: j = json.load(e); reason = ','.join(x.get('reason', '') for x in j['error'].get('errors', [])) or j['error'].get('message', '')
    except Exception: reason = ''
    return f'HTTP {e.code} {reason}'.strip()

def ts(s): return datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))

def list_open(tok, days, video=None, search=None):
    me = call(tok, 'channels', part='id', mine='true')['items'][0]['id']
    now = datetime.datetime.now(datetime.timezone.utc); since = now - datetime.timedelta(days=days)
    q = dict(part='snippet,replies', order='time', maxResults=100, textFormat='plainText')
    q.update({'videoId': video} if video else {'allThreadsRelatedToChannelId': me})
    if search: q['searchTerms'] = search
    out, mine24, pt = [], 0, None
    while True:
        r = call(tok, 'commentThreads', **q, **({'pageToken': pt} if pt else {}))
        old = False
        for t in r.get('items', []):
            top = t['snippet']['topLevelComment']['snippet']
            if not search and ts(top['publishedAt']) < since: old = True; continue
            reps = t.get('replies', {}).get('comments', [])
            if t['snippet'].get('totalReplyCount', 0) > len(reps):  # 답글이 5개를 넘으면 전부 받아 확인
                reps = call(tok, 'comments', part='snippet', parentId=t['id'], maxResults=100, textFormat='plainText').get('items', [])
            mine = [c for c in reps if c['snippet'].get('authorChannelId', {}).get('value') == me]
            mine24 += sum(1 for c in mine if ts(c['snippet']['publishedAt']) >= now - datetime.timedelta(hours=24))
            if top.get('authorChannelId', {}).get('value') == me or mine: continue
            out.append({'threadId': t['id'], 'videoId': top.get('videoId'), 'author': top.get('authorDisplayName'),
                        'authorChannelId': top.get('authorChannelId', {}).get('value'), 'text': top.get('textOriginal') or top.get('textDisplay'),
                        'likeCount': top.get('likeCount', 0), 'publishedAt': top['publishedAt'], 'replyCount': t['snippet'].get('totalReplyCount', 0)})
        pt = r.get('nextPageToken')
        if not pt or old: break
    ids = sorted({c['videoId'] for c in out if c['videoId']}); titles = {}
    for k in range(0, len(ids), 50):
        for v in call(tok, 'videos', part='snippet', id=','.join(ids[k:k + 50])).get('items', []): titles[v['id']] = v['snippet']['title']
    for c in out: c['videoTitle'] = titles.get(c['videoId'], '')
    return {'channelId': me, 'since': since.isoformat(timespec='seconds'), 'my_replies_24h': mine24, 'open': out}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--list', action='store_true'); ap.add_argument('--days', type=int, default=7)
    ap.add_argument('--video'); ap.add_argument('--search')
    ap.add_argument('--reply'); ap.add_argument('--text-file')
    a = ap.parse_args()
    if not all(os.environ.get(k) for k in ('YT_CLIENT_ID', 'YT_CLIENT_SECRET', 'YT_REFRESH_TOKEN')):
        print('유튜브 인증값 없음', file=sys.stderr); sys.exit(2)
    try: tok = token()
    except urllib.error.HTTPError as e: print('토큰 갱신 실패:', err(e), file=sys.stderr); sys.exit(1)
    if a.list:
        try: print(json.dumps(list_open(tok, a.days, a.video, a.search), ensure_ascii=False, indent=1))
        except urllib.error.HTTPError as e: print('목록 실패:', err(e), file=sys.stderr); sys.exit(1)
    elif a.reply and a.text_file:
        text = open(a.text_file, encoding='utf-8').read().strip()
        if not text: print('답글이 비어 있음', file=sys.stderr); sys.exit(1)
        try: r = call(tok, 'comments', {'snippet': {'parentId': a.reply, 'textOriginal': text}}, part='snippet')
        except urllib.error.HTTPError as e: print('답글 실패(재시도 안 함):', err(e), file=sys.stderr); sys.exit(1)
        print(r['id'])
    else: ap.print_usage(); sys.exit(2)

if __name__ == '__main__': main()
