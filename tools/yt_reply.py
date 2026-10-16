# 김박사 월드 채널 댓글에 답글을 단다(YouTube Data API).
# 인증: 업로드·yt_stats.py 와 같은 환경 변수 YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (youtube.force-ssl 범위). 값은 출력하지 않는다.
# 사용:
#   python3 yt_reply.py --list [--days 7] [--video VIDEO_ID] [--search 글자]
#       내 채널 영상의 댓글 가운데 답할 차례인 것을 JSON 으로 출력한다.
#         kind=top      : 시청자 댓글에 내 채널 답글이 아직 없다.
#         kind=followup : 내 채널 답글(또는 내 채널이 쓴 고정 댓글 등) 뒤에 시청자 대댓글이 새로 달렸다.
#                         followups 에 내 마지막 답글 뒤의 시청자 대댓글, context 에 스레드 대화 전체(시간순)가 들어 있다.
#       my_replies_24h 는 최근 24시간에 내 채널이 단 답글 수(하루 한도 확인용, 읽은 스레드 범위 안에서 센다).
#       유튜브 답글은 한 단계뿐이라 대댓글에 답할 때도 --reply 에는 스레드 ID 를 준다(본문 앞에 @이름을 붙여 상대를 가리킨다).
#   python3 yt_reply.py --reply THREAD_ID --text-file 답글.txt [--kind top|followup|request]
#       답글 본문의 리포트 링크(drkimworld.com/r/<slug>/)에 위치별 UTM 을 붙인다(운영자 지시 2026-10-16):
#       utm_source=youtube&utm_medium=comment&utm_campaign=<slug>&utm_content=reply|followup|request
#       (--kind 기본 top → reply, 대댓글에 답하면 followup, 종목 요청 답글은 request). 이미 있던 utm 값은 덮어쓴다.
#       답글 1개를 단다. 성공하면 답글 ID 를 출력한다. 실패하면 다시 시도하지 않고 오류만 출력하고 1 로 끝난다.
import os, re, sys, json, argparse, datetime, urllib.request, urllib.parse, urllib.error

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
    def item(c):
        sn = c['snippet']
        return {'commentId': c['id'], 'author': sn.get('authorDisplayName'), 'authorChannelId': sn.get('authorChannelId', {}).get('value'),
                'isMe': sn.get('authorChannelId', {}).get('value') == me, 'text': sn.get('textOriginal') or sn.get('textDisplay'),
                'likeCount': sn.get('likeCount', 0), 'publishedAt': sn['publishedAt']}
    out, mine24, pt, pages = [], 0, None, 0
    while True:
        r = call(tok, 'commentThreads', **q, **({'pageToken': pt} if pt else {})); pages += 1
        fresh = False
        for t in r.get('items', []):
            topc = t['snippet']['topLevelComment']; top = topc['snippet']
            reps = t.get('replies', {}).get('comments', [])
            if t['snippet'].get('totalReplyCount', 0) > len(reps):  # 답글이 5개를 넘으면 전부 받아 확인
                reps, rpt = [], None
                while True:
                    rr = call(tok, 'comments', part='snippet', parentId=t['id'], maxResults=100, textFormat='plainText', **({'pageToken': rpt} if rpt else {}))
                    reps += rr.get('items', []); rpt = rr.get('nextPageToken')
                    if not rpt: break
            conv = sorted([item(topc)] + [item(c) for c in reps], key=lambda x: x['publishedAt'])
            if max(ts(c['publishedAt']) for c in conv) < since and not search: continue
            fresh = True
            mine = [c for c in conv if c['isMe']]
            mine24 += sum(1 for c in mine if c['commentId'] != topc['id'] and ts(c['publishedAt']) >= now - datetime.timedelta(hours=24))
            base = {'threadId': t['id'], 'videoId': top.get('videoId'), 'replyCount': t['snippet'].get('totalReplyCount', 0)}
            if not mine:
                if ts(top['publishedAt']) < since and not search: continue
                out.append({**base, 'kind': 'top', **{k: v for k, v in item(topc).items() if k not in ('isMe', 'commentId')}})
                continue
            last = max(ts(c['publishedAt']) for c in mine)
            fu = [c for c in conv if not c['isMe'] and ts(c['publishedAt']) > last and (search or ts(c['publishedAt']) >= since)]
            if not fu: continue
            out.append({**base, 'kind': 'followup', 'author': fu[-1]['author'], 'authorChannelId': fu[-1]['authorChannelId'],
                        'text': fu[-1]['text'], 'likeCount': max(c['likeCount'] for c in fu), 'publishedAt': fu[-1]['publishedAt'],
                        'topIsMe': top.get('authorChannelId', {}).get('value') == me, 'followups': fu,
                        'my_replies_in_thread_24h': sum(1 for c in mine if ts(c['publishedAt']) >= now - datetime.timedelta(hours=24)),
                        'context': [{k: c[k] for k in ('author', 'isMe', 'text', 'publishedAt')} for c in conv][-12:]})
        pt = r.get('nextPageToken')
        # order=time 은 스레드 시작 시각 순이라, 오래된 스레드의 새 대댓글을 놓치지 않도록 새 활동이 없는 페이지가 나올 때까지(최대 10쪽) 더 읽는다
        if not pt or (not fresh and not search) or pages >= 10: break
    ids = sorted({c['videoId'] for c in out if c['videoId']}); titles = {}
    for k in range(0, len(ids), 50):
        for v in call(tok, 'videos', part='snippet', id=','.join(ids[k:k + 50])).get('items', []): titles[v['id']] = v['snippet']['title']
    for c in out: c['videoTitle'] = titles.get(c['videoId'], '')
    return {'channelId': me, 'since': since.isoformat(timespec='seconds'), 'my_replies_24h': mine24, 'open': out}

LINK_RE = re.compile(r'https?://(?:www\.)?drkimworld\.com/r/([a-z0-9-]+)/(\?[^\s]*)?')
UTM_CONTENT = {'top': 'reply', 'followup': 'followup', 'request': 'request'}

def tag_links(text, kind='top'):
    content = UTM_CONTENT.get(kind, 'reply')
    def sub(m):
        slug, q = m.group(1), (m.group(2) or '')[1:]
        keep = [kv for kv in q.split('&') if kv and not kv.startswith('utm_')]
        return f'https://drkimworld.com/r/{slug}/?' + '&'.join(keep + ['utm_source=youtube', 'utm_medium=comment', f'utm_campaign={slug}', f'utm_content={content}'])
    return LINK_RE.sub(sub, text)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--list', action='store_true'); ap.add_argument('--days', type=int, default=7)
    ap.add_argument('--video'); ap.add_argument('--search')
    ap.add_argument('--reply'); ap.add_argument('--text-file')
    ap.add_argument('--kind', choices=['top', 'followup', 'request'], default='top')
    a = ap.parse_args()
    if not all(os.environ.get(k) for k in ('YT_CLIENT_ID', 'YT_CLIENT_SECRET', 'YT_REFRESH_TOKEN')):
        print('유튜브 인증값 없음', file=sys.stderr); sys.exit(2)
    try: tok = token()
    except urllib.error.HTTPError as e: print('토큰 갱신 실패:', err(e), file=sys.stderr); sys.exit(1)
    if a.list:
        try: print(json.dumps(list_open(tok, a.days, a.video, a.search), ensure_ascii=False, indent=1))
        except urllib.error.HTTPError as e: print('목록 실패:', err(e), file=sys.stderr); sys.exit(1)
    elif a.reply and a.text_file:
        text = tag_links(open(a.text_file, encoding='utf-8').read().strip(), a.kind)
        if not text: print('답글이 비어 있음', file=sys.stderr); sys.exit(1)
        try: r = call(tok, 'comments', {'snippet': {'parentId': a.reply, 'textOriginal': text}}, part='snippet')
        except urllib.error.HTTPError as e: print('답글 실패(재시도 안 함):', err(e), file=sys.stderr); sys.exit(1)
        print(r['id'])
    else: ap.print_usage(); sys.exit(2)

if __name__ == '__main__': main()
