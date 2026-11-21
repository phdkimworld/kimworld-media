#!/usr/bin/env python3
"""유튜브 분석 자료 읽기(2026-11-21 운영자 "지금 새 키로 넘어가").

자료: 사이트 저장소 `.github/workflows/yt-analytics.yml`(매일 09:17 UTC, 새 키 — 사이트 GitHub 비밀값 YT_*, yt-analytics.readonly)
→ 비공개 저장소 phdkimworld/kimworld ops-data `stats/yt_analytics.json` → 로컬 /home/claude/kimworld-ops (OPS_DIR).
이 컨테이너의 유튜브 키(분석 권한 없음)와 무관하다. 노출수·노출 CTR은 공개 API에 없어 자료에 없다.

사용:
  python3 tools/yt_analytics_read.py                 채널 28·7일 합계 + 영상별 상위 20(평균 시청 비율·시간·구독 증가·유입 상위)
  python3 tools/yt_analytics_read.py <영상ID> ...    그 영상들만
  python3 tools/yt_analytics_read.py --sub-test      review/sub_test.md '영상별 집계'(F10)를 이 자료로 덮어쓴다
  --pull 을 붙이면 먼저 OPS_DIR 에서 git pull
import:  from yt_analytics_read import get;  get('K6zvU0sUeak') → {views, avp, avd, subs, minutes, title, traffic:[(경로, 조회)...]} 또는 None
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
    body = ('## 영상별 집계 (F10 — 사이트 yt-analytics.yml → ops stats/yt_analytics.json 최근 28일, `tools/yt_analytics_read.py --sub-test`, 하루 첫 제작 세션이 덮어씀)\n\n'
            '| 영상 ID | A/B | 조회 | 구독 증가 | 1,000회당 |\n| --- | --- | --- | --- | --- |\n' + '\n'.join(rows) +
            f"\n\nA 합계: {per('A')} · B 합계: {per('B')} · 기간 {rg} · 갱신: {d.get('generated_at', '')[:16]}Z\n")
    # 절 끝(다음 '## ' 또는 파일 끝)까지 교체
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
    sys.exit(sub_test() if args[:1] == ['--sub-test'] else show(args))
