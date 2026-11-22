#!/usr/bin/env python3
"""유튜브 분석 자료 읽기(2026-11-21 운영자 "지금 새 키로 넘어가").

자료: 사이트 저장소 `.github/workflows/yt-analytics.yml`(매일 09:17 UTC, 새 키 — 사이트 GitHub 비밀값 YT_*, yt-analytics.readonly)
→ 비공개 저장소 phdkimworld/kimworld ops-data `stats/yt_analytics.json` → 로컬 /home/claude/kimworld-ops (OPS_DIR).
이 컨테이너의 유튜브 키(분석 권한 없음)와 무관하다. 노출수·노출 CTR은 공개 API에 없어 자료에 없다.

사용:
  python3 tools/yt_analytics_read.py                 채널 28·7일 합계 + 영상별 상위 20(평균 시청 비율·시간·구독 증가·유입 상위)
  python3 tools/yt_analytics_read.py <영상ID> ...    그 영상들만
  python3 tools/yt_analytics_read.py --sub-test      review/sub_test.md '영상별 집계'(F10)를 이 자료로 덮어쓴다
  python3 tools/yt_analytics_read.py --retention <영상ID> [--at 초[,초2]]
        시청 유지 곡선(2026-11-22~, 최근 14일 롱폼만 — 사이트 yt_analytics.py 'retention'). --at 없으면 10% 간격 요약,
        --at 초 = 그 시각 유지 비율(audienceWatchRatio, %)·상대 유지(relativeRetentionPerformance), --at a,b = a초 − b초 유지 차(%p).
        곡선은 길이의 1% 간격 점이라(10분 영상이면 6초) 사이는 직선 보간 — 2.4초 스팅은 점 1~2개 차이로 본다.
        브랜드 스팅 판정(review/experiments.md 브랜드 줄): --at <brand_intro 시각>,<시각+길이+1>(segments.json 'brand_intro')
  --pull 을 붙이면 먼저 OPS_DIR 에서 git pull
import:  from yt_analytics_read import get;  get('K6zvU0sUeak') → {views, avp, avd, subs, minutes, title, traffic:[(경로, 조회)...]} 또는 None
         from yt_analytics_read import ret_at, ret_drop;  ret_at(ID, 초) → (유지 %, 상대 유지) 또는 None · ret_drop(ID, a, b) → %p 또는 None
"""
import json
import os
import re
import subprocess
import sys

OPS = os.environ.get('OPS_DIR', '/home/claude/kimworld-ops')
PATH = os.path.join(OPS, 'stats', 'yt_analytics.json')
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUB_TEST = os.path.join(HERE, 'review', 'sub_test.md')
_cache = None


def load(pull=False):
    global _cache
    if pull:
        subprocess.run(['git', '-C', OPS, 'pull', '-q'], check=False)
        _cache = None
    if _cache is None:
        if not os.path.exists(PATH):
            return None
        with open(PATH, encoding='utf-8') as f:
            _cache = json.load(f)
    return _cache


def _row(v, d):
    vid = v['video']
    tr = d.get('traffic', {}).get('videos', {}).get(vid) or []
    return {'video': vid, 'title': v.get('title', ''), 'views': v.get('views'), 'minutes': v.get('estimatedMinutesWatched'),
            'avd': v.get('averageViewDuration'), 'avp': v.get('averageViewPercentage'), 'subs': v.get('subscribersGained'),
            'traffic': [(t['insightTrafficSourceType'], t.get('views')) for t in tr[:3]]}


def get(video_id):
    """영상 ID 하나의 최근 28일 분석 값. 자료가 없거나 상위 200편 밖이면 None."""
    d = load()
    if not d:
        return None
    for v in d.get('videos', []):
        if v.get('video') == video_id:
            return _row(v, d)
    return None


def avp_map():
    """{영상ID: 평균 시청 비율(%)} — insights.py 등에서 씀."""
    d = load() or {}
    return {v['video']: v.get('averageViewPercentage') for v in d.get('videos', [])}


def retention(video_id):
    """{video, title, published, duration_sec, rows:[[비율, 유지, 상대], …]} 또는 None(최근 14일 롱폼 밖·자료 없음)."""
    d = load() or {}
    for r in d.get('retention') or []:
        if r.get('video') == video_id and r.get('rows'):
            return r
    return None


def ret_at(video_id, sec):
    """sec 초 지점 (audienceWatchRatio ×100, relativeRetentionPerformance) — 앞뒤 점 직선 보간."""
    r = retention(video_id)
    if not r or not r.get('duration_sec'):
        return None
    x, rows = float(sec) / r['duration_sec'], r['rows']
    if x <= rows[0][0]:
        return rows[0][1] * 100, rows[0][2]
    for (x0, a0, p0), (x1, a1, p1) in zip(rows, rows[1:]):
        if x0 <= x <= x1:
            w = (x - x0) / (x1 - x0) if x1 > x0 else 0
            return (a0 + (a1 - a0) * w) * 100, p0 + (p1 - p0) * w
    return rows[-1][1] * 100, rows[-1][2]


def ret_drop(video_id, a, b):
    """a초 유지 − b초 유지(%p). 광고·스팅 앞뒤 이탈 보기용."""
    va, vb = ret_at(video_id, a), ret_at(video_id, b)
    return None if va is None or vb is None else va[0] - vb[0]


def show_retention(vid, at=None):
    r = retention(vid)
    if not r:
        print(f'{vid}: 유지 곡선 없음(최근 14일 롱폼만 받음 · 사이트 yt-analytics.yml 실행 뒤 --pull)')
        return 1
    print(f"{vid} 유지 곡선 · 길이 {r['duration_sec']}초 · 점 {len(r['rows'])}개 · {r.get('title', '')[:30]}")
    if at:
        ts = [float(x) for x in at.split(',')]
        for t in ts:
            v = ret_at(vid, t)
            print(f'  {t:.1f}초: 유지 {v[0]:.1f}% · 상대 유지 {v[1]:.2f}')
        if len(ts) == 2:
            print(f'  차이 {ts[0]:.1f}초 → {ts[1]:.1f}초: {ret_drop(vid, ts[0], ts[1]):+.1f}%p(양수 = 그 사이 이탈)')
    else:
        for k in range(0, 101, 10):
            v = ret_at(vid, r['duration_sec'] * k / 100)
            print(f"  {k:3d}% ({r['duration_sec'] * k / 100:5.0f}초): 유지 {v[0]:5.1f}% · 상대 {v[1]:.2f}")
    return 0


def _fmt(r):
    tr = ', '.join(f'{k} {n}' for k, n in r['traffic']) or '-'
    avd = r['avd'] or 0
    return (f"{r['video']}  조회 {r['views']:>6} · 평균 시청 {r['avp'] or 0:5.1f}% · {int(avd) // 60}:{int(avd) % 60:02d}"
            f" · 구독 +{r['subs']} · 유입 {tr}  {r['title'][:30]}")


def show(ids):
    d = load()
    if not d:
        print(f'자료 없음: {PATH} (사이트 yt-analytics.yml 실행 → --pull)')
        return 1
    rg = d.get('range', {})
    print(f"유튜브 분석 · 생성 {d.get('generated_at', '')[:16]}Z · 28일 {'~'.join(rg.get('d28', []))} · 영상 {len(d.get('videos', []))}편")
    if d.get('errors'):
        print('  오류: ' + ', '.join(f'{k} {v}' for k, v in d['errors'].items()))
    if not ids:
        for k in ('d28', 'd7'):
            t = d.get('totals', {}).get(k) or {}
            if t:
                print(f"  {k}: 조회 {t.get('views')} · 시청 {t.get('estimatedMinutesWatched')}분 · 평균 {t.get('averageViewPercentage')}%"
                      f" · 구독 +{t.get('subscribersGained')} -{t.get('subscribersLost')}")
        ch = d.get('traffic', {}).get('channel') or []
        print('  채널 유입: ' + ', '.join(f"{t['insightTrafficSourceType']} {t.get('views')}" for t in ch[:6]))
        rows = [_row(v, d) for v in d.get('videos', [])[:20]]
    else:
        rows = [get(i) or {'video': i, 'missing': True} for i in ids]
    for r in rows:
        print('  ' + (f"{r['video']}  (28일 상위 200편에 없음)" if r.get('missing') else _fmt(r)))
    return 0


def sub_test():
    """review/sub_test.md '영상별 집계'(F10) 표를 이 자료로 덮어쓴다(위 표의 영상 ID·A/B 기준)."""
    d = load()
    if not d:
        print('자료 없음 — 사이트 yt-analytics.yml 실행 뒤 --pull')
        return 1
    text = open(SUB_TEST, encoding='utf-8').read()
    head, sep, tail = text.partition('## 영상별 집계')
    if not sep:
        print('sub_test.md 에 영상별 집계 절 없음')
        return 1
    # 제작 세션이 표 대신 파일 끝(집계 아래)에 붙인 회차 행은 위 표로 옮긴다
    pat = r'^\| [^|]+\| [^|]+\| ([\w-]{11}) \| ([AB]) \|.*$'
    stray = [m.group(0) for m in re.finditer(pat, tail, re.M)]
    if stray:
        tail = re.sub(pat + r'\n?', '', tail, flags=re.M)
        head = head.rstrip('\n') + '\n' + '\n'.join(stray) + '\n\n'
    vids = [(m.group(1), m.group(2)) for m in re.finditer(pat, head, re.M)]
    rows, sums = [], {'A': [0, 0], 'B': [0, 0]}
    for vid, g in vids:
        r = get(vid)
        if not r:
            rows.append(f'| {vid} | {g} | - | - | - |')
            continue
        v, s = int(r['views'] or 0), int(r['subs'] or 0)
        sums[g][0] += v
        sums[g][1] += s
        rows.append(f"| {vid} | {g} | {v} | {s} | {s / v * 1000:.1f} |" if v else f'| {vid} | {g} | 0 | {s} | - |')
    per = lambda g: f"조회 {sums[g][0]} · 구독 {sums[g][1]} · {sums[g][1] / sums[g][0] * 1000:.1f}/1,000회" if sums[g][0] else '—'
    rg = '~'.join(d.get('range', {}).get('d28', []))
    # 11-22 운영자 "비공개로 옮겨": 숫자 표는 비공개 ops 저장소에만, 공개 미디어에는 판정만
    priv = os.path.join(os.environ.get('OPS_DIR', '/home/claude/kimworld-ops'), 'review', 'sub_test_per_video.md')
    os.makedirs(os.path.dirname(priv), exist_ok=True)
    open(priv, 'w', encoding='utf-8').write(
        '# 구독 시험 영상별 집계 (비공개 — tools/yt_analytics_read.py --sub-test가 덮어씀)\n\n'
        '| 영상 ID | A/B | 조회 | 구독 증가 | 1,000회당 |\n| --- | --- | --- | --- | --- |\n' + '\n'.join(rows) +
        f"\n\nA 합계: {per('A')} · B 합계: {per('B')} · 기간 {rg} · 갱신: {d.get('generated_at', '')[:16]}Z\n")
    have = sum(1 for r in rows if not r.endswith('| - | - | - |'))
    ra = sums['A'][1] / sums['A'][0] if sums['A'][0] else None
    rb = sums['B'][1] / sums['B'][0] if sums['B'][0] else None
    if ra is None or rb is None:
        verdict = '아직 비교할 자료 부족'
    else:
        lead = 'B(질문형)' if rb > ra else ('A' if ra > rb else '같음')
        verdict = f"1,000회당 구독은 {lead} 쪽이 높음 — 관찰 중(12-01 판정)"
    body = ('## 영상별 집계 (F10 — 숫자는 비공개: phdkimworld/kimworld ops-data `review/sub_test_per_video.md`, 운영자 11-22 "비공개로 옮겨")\n\n'
            f"- 자료 있는 영상 {have}/{len(rows)}편 · {verdict} · 갱신 {d.get('generated_at', '')[:10]}\n")
    nxt = re.search(r'^## ', tail[1:], re.M)
    rest = tail[1 + nxt.start():] if nxt else ''
    open(SUB_TEST, 'w', encoding='utf-8').write(head + body + ('\n' + rest if rest else ''))
    print(f'sub_test.md 영상별 집계 {len(rows)}행 갱신')
    return 0


if __name__ == '__main__':
    args = sys.argv[1:]
    pull = '--pull' in args
    args = [a for a in args if a != '--pull']
    load(pull)
    if args[:1] == ['--retention'] and len(args) > 1:
        sys.exit(show_retention(args[1], args[args.index('--at') + 1] if '--at' in args[:-1] else None))
    sys.exit(sub_test() if args[:1] == ['--sub-test'] else show(args))
