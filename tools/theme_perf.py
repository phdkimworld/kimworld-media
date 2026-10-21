# 독자 반응 학습(SKILL G7 '채널 성과' 점수의 근거): 롱폼 영상마다 공개 뒤 48시간 조회수를 구해 테마·규모별로 묶는다.
# 사용: python3 theme_perf.py [사이트 저장소=/home/claude/kimworld-site] [스냅숏=stats_snapshots.jsonl]
#  - 영상 목록과 테마는 사이트 리포트 front matter(ticker·theme·date·youtube_id)에서 읽는다
#  - 공개 시각은 그 영상이 스냅숏에 처음 나온 시각(첫 스냅숏보다 먼저 공개된 영상은 리포트 날짜 정오 ET)
#  - 48시간 값은 앞뒤 스냅숏을 직선 보간한다. 48시간이 안 된 영상은 '진행 중'으로 따로 보인다
import os, re, sys, json, glob, datetime, statistics

SITE = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/kimworld-site'
SNAP = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stats_snapshots.jsonl')
H = 48
# 시가총액 약 1천억 달러 이상(대형주). tickers.yaml에 규모 칸이 없어 여기서 관리한다
BIG = {'TSLA', 'NFLX', 'ISRG', 'NVDA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'AVGO', 'SPCX', 'AMD', 'PLTR', 'ORCL', 'COIN', 'MU', 'INTC'}

def ts(s):
    return datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))

def front(path):
    m = re.match(r'---\n(.*?)\n---', open(path, encoding='utf-8').read(), re.S)
    d = {}
    for line in (m.group(1).splitlines() if m else []):
        k, _, v = line.partition(':')
        if k in ('ticker', 'theme', 'date', 'youtube_id'):
            d[k] = v.strip().strip('\'"')
    return d

def main():
    snaps = [json.loads(l) for l in open(SNAP)]
    snaps = [(ts(s['t']), s['v']) for s in snaps]
    t0, now = snaps[0][0], snaps[-1][0]
    rows = []
    for p in sorted(glob.glob(os.path.join(SITE, 'content/reports/*.md'))):
        d = front(p)
        vid = d.get('youtube_id')
        if not vid or not d.get('ticker'):
            continue
        seen = [(t, v[vid]) for t, v in snaps if vid in v]
        if not seen:
            continue
        if seen[0][0] > t0:
            pub = seen[0][0] - datetime.timedelta(hours=0.5)  # 스냅숏 간격의 절반만큼 앞당긴 추정
        else:
            pub = datetime.datetime.fromisoformat(d['date'] + 'T16:00:00+00:00')
        age = (now - pub).total_seconds() / 3600
        at = pub + datetime.timedelta(hours=H)
        v48 = None
        if age >= H:
            prev = [(t, v) for t, v in seen if t <= at]
            nxt = [(t, v) for t, v in seen if t >= at]
            if prev and nxt:
                (ta, va), (tb, vb) = prev[-1], nxt[0]
                v48 = va if tb == ta else va + (vb - va) * (at - ta).total_seconds() / (tb - ta).total_seconds()
            elif nxt:  # 48시간 전 스냅숏이 없다(첫 스냅숏 전 공개): 첫 값이 48시간보다 늦으면 쓰지 않는다
                v48 = None
        rows.append(dict(tk=d['ticker'], theme=d.get('theme', '?'), size='대형' if d['ticker'] in BIG else '중소형',
                         date=d['date'], vid=vid, age=age, v48=v48, now=seen[-1][1], pub=pub, seen=seen))
    done = [r for r in rows if r['v48'] is not None]
    print(f'스냅숏 {snaps[0][0]:%m-%d %H:%M}~{now:%m-%d %H:%M} UTC · 롱폼 {len(rows)}편 · 48시간 값 있는 영상 {len(done)}편\n')
    for key, title in (('theme', '테마'), ('size', '규모')):
        g = {}
        for r in done:
            g.setdefault(r[key], []).append(r['v48'])
        print(f'## {title}별 48시간 조회수 (중앙값 내림차순)')
        print('| 묶음 | 편수 | 중앙값 | 최고 |')
        print('|---|---|---|---|')
        for k, vs in sorted(g.items(), key=lambda x: -statistics.median(x[1])):
            print(f'| {k} | {len(vs)} | {statistics.median(vs):.0f} | {max(vs):.0f} |')
        print()
    allm = statistics.median([r['v48'] for r in done]) if done else 0
    print(f'채널 전체 48시간 중앙값: {allm:.0f}\n')
    print('## 48시간 상·하위 영상')
    for r in sorted(done, key=lambda r: -r['v48'])[:5] + [None] + sorted(done, key=lambda r: r['v48'])[:5]:
        print('  ...' if r is None else f"  {r['tk']:<6} {r['theme']:<10} {r['date']} 48h {r['v48']:.0f}  (지금 {r['now']})")
    print('\n## 진행 중(48시간 전) — 같은 나이의 채널 중앙값과 비교')
    for r in sorted([r for r in rows if r['age'] < H], key=lambda r: -r['age']):
        base = [x for x in (at_age(o, r['age']) for o in done) if x is not None]
        b = statistics.median(base) if base else 0
        print(f"  {r['tk']:<6} {r['theme']:<10} {r['age']:.0f}시간 {r['now']}회 · 같은 나이 중앙값 {b:.0f} → {r['now'] / b if b else 0:.1f}배")

def at_age(r, h):
    at = r['pub'] + datetime.timedelta(hours=h)
    prev = [(t, v) for t, v in r['seen'] if t <= at]
    nxt = [(t, v) for t, v in r['seen'] if t >= at]
    if not prev or not nxt:
        return None
    (ta, va), (tb, vb) = prev[-1], nxt[0]
    return va if tb == ta else va + (vb - va) * (at - ta).total_seconds() / (tb - ta).total_seconds()

if __name__ == '__main__':
    main()
