#!/usr/bin/env python3
"""트래픽 컷오프(운영자 지시 11-05 "정규와 요청 모두에 트래픽 컷오프를 적용해서 트래픽 실적 안 좋은건 못 만들도록 해",
"할수 있으면 종목 컷오프 및 랭킹 시에 인게이지먼트 지표도 반영 해").
이미 만든 종목: 공개 3일 지난 롱폼 기준으로
  지수 = 0.7 × (편당 평균 조회 ÷ 종목별 중앙값) + 0.3 × (편당 인게이지먼트 ÷ 종목별 중앙값)
  인게이지먼트 = 좋아요 + 댓글×2 (stats_engagement.json, yt_stats.py가 매번 갱신)
지수 < 1.0 이면 컷오프(제작 불가). 만든 적 없거나 3일 지난 영상이 없으면 '신규'로 통과.
사용: python3 tools/traffic_cut.py [티커…]
"""
import glob, re, os, json, datetime, sys
HERE = os.path.dirname(os.path.abspath(__file__)); MEDIA = os.path.dirname(HERE)
SITE = os.path.join(os.path.dirname(MEDIA), 'kimworld-site')
def engagement():
    p = os.path.join(MEDIA, 'stats_engagement.json')
    return json.load(open(p))['e'] if os.path.exists(p) else {}
def eng_points(vid, E):
    l, c = E.get(vid, [0, 0]); return l + 2 * c
def load():
    v = json.loads(open(os.path.join(MEDIA, 'stats_snapshots.jsonl')).readlines()[-1])['v']
    E = engagement(); today = datetime.date.today(); per = {}
    for f in glob.glob(os.path.join(SITE, 'content/reports/*.md')):
        h = open(f, encoding='utf-8').read(4000)
        tk = re.search(r"^ticker:\s*['\"]?([A-Za-z0-9.]+)", h, re.M)
        y = re.search(r"^youtube_id:\s*['\"]?([\w-]{6,})", h, re.M)
        d = re.search(r"^date:\s*['\"]?(\d{4}-\d\d-\d\d)", h, re.M)
        if not (tk and y and d) or y.group(1) not in v: continue
        if (today - datetime.date.fromisoformat(d.group(1))).days < 3: continue
        per.setdefault(tk.group(1).upper(), []).append((v[y.group(1)], eng_points(y.group(1), E)))
    stat = {k: (sum(a for a, _ in x) / len(x), sum(b for _, b in x) / len(x)) for k, x in per.items()}
    med = lambda xs: sorted(xs)[len(xs) // 2] if xs else 0
    mv, me = med([s[0] for s in stat.values()]), med([s[1] for s in stat.values()])
    cap = lambda r: min(r, 3.0)  # 한 종목의 튀는 값이 지수를 혼자 끌지 않게 비율은 3배까지
    idx = {k: 0.7 * cap(a / mv if mv else 1) + 0.3 * cap(b / me if me else 1) for k, (a, b) in stat.items()}
    return {'stat': stat, 'idx': idx, 'mv': mv, 'me': me}
def verdict(tk, S, _=None):
    tk = tk.upper()
    if tk not in S['idx']: return True, '신규'
    a, b = S['stat'][tk]
    return S['idx'][tk] >= 1.0, f"{round(a)}회·참여 {b:.1f}·지수 {S['idx'][tk]:.2f}"
if __name__ == '__main__':
    S = load()
    print(f"중앙값: 편당 조회 {round(S['mv'])} · 편당 참여(좋아요+댓글×2) {S['me']:.1f} (종목 {len(S['idx'])}개) · 지수 1.0 미만 컷오프")
    for t in sys.argv[1:]:
        ok, a = verdict(t, S); print(t.upper(), a, '통과' if ok else '컷오프')
