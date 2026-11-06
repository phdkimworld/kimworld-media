#!/usr/bin/env python3
"""트래픽 컷오프(운영자 지시 11-05 "정규와 요청 모두에 트래픽 컷오프를 적용해서 트래픽 실적 안 좋은건 못 만들도록 해",
"할수 있으면 종목 컷오프 및 랭킹 시에 인게이지먼트 지표도 반영 해").
이미 만든 종목: 공개 3일 지난 롱폼 기준으로
  지수 = 0.7 × (편당 평균 조회 ÷ 종목별 중앙값) + 0.3 × (참여율 ÷ 종목별 중앙값)
  참여율 = (좋아요 + 댓글×2) ÷ 조회 수(운영자 11-05 "뷰나 좋아요는 조회수당으로 정규화") — stats_engagement.json, yt_stats.py가 매번 갱신
평균 시청 비율(stats_retention.json, yt-analytics 범위 토큰이 있을 때)이 있으면 조회 0.5·참여 0.25·시청 비율 0.25로 바꾼다.
판정(운영자 지시 11-06 "그냥 랭크섬으로 처리해"): 편당 조회 순위 + 참여율 순위의 합이 전체 중앙값 이하면 통과.
만든 적 없거나 3일 지난 영상이 없으면 '신규'로 통과.
사용: python3 tools/traffic_cut.py [티커…]
"""
import glob, re, os, json, datetime, sys
HERE = os.path.dirname(os.path.abspath(__file__)); MEDIA = os.path.dirname(HERE)
SITE = os.path.join(os.path.dirname(MEDIA), 'kimworld-site')
def engagement():
    p = os.path.join(MEDIA, 'stats_engagement.json')
    return json.load(open(p))['e'] if os.path.exists(p) else {}
def retention():
    p = os.path.join(MEDIA, 'stats_retention.json')
    return json.load(open(p))['r'] if os.path.exists(p) else {}
def eng_points(vid, E):
    l, c = E.get(vid, [0, 0]); return l + 2 * c
def load():
    v = json.loads(open(os.path.join(MEDIA, 'stats_snapshots.jsonl')).readlines()[-1])['v']
    E = engagement(); RT = retention(); today = datetime.date.today(); per = {}; ret = {}
    for f in glob.glob(os.path.join(SITE, 'content/reports/*.md')):
        h = open(f, encoding='utf-8').read(4000)
        tk = re.search(r"^ticker:\s*['\"]?([A-Za-z0-9.]+)", h, re.M)
        y = re.search(r"^youtube_id:\s*['\"]?([\w-]{6,})", h, re.M)
        d = re.search(r"^date:\s*['\"]?(\d{4}-\d\d-\d\d)", h, re.M)
        if not (tk and y and d) or y.group(1) not in v: continue
        if (today - datetime.date.fromisoformat(d.group(1))).days < 3: continue
        per.setdefault(tk.group(1).upper(), []).append((v[y.group(1)], eng_points(y.group(1), E)))
        if y.group(1) in RT: ret.setdefault(tk.group(1).upper(), []).append(RT[y.group(1)][1])
    # (편당 평균 조회, 참여율 = 참여 합 ÷ 조회 합)
    stat = {k: (sum(a for a, _ in x) / len(x), sum(b for _, b in x) / max(sum(a for a, _ in x), 1)) for k, x in per.items()}
    med = lambda xs: sorted(xs)[len(xs) // 2] if xs else 0
    mv, me = med([s[0] for s in stat.values()]), med([s[1] for s in stat.values()])
    cap = lambda r: min(r, 3.0)  # 한 종목의 튀는 값이 지수를 혼자 끌지 않게 비율은 3배까지
    rp = {k: sum(x) / len(x) for k, x in ret.items()}; mr = med(list(rp.values()))
    if rp:  # 지속 시청 자료가 있으면: 조회 0.5 · 참여 0.25 · 평균 시청 비율 0.25
        idx = {k: 0.5 * cap(a / mv if mv else 1) + 0.25 * cap(b / me if me else 1) + 0.25 * cap(rp.get(k, mr) / mr if mr else 1) for k, (a, b) in stat.items()}
    else:
        idx = {k: 0.7 * cap(a / mv if mv else 1) + 0.3 * cap(b / me if me else 1) for k, (a, b) in stat.items()}
    # 랭크섬(운영자 11-06 "너무 복잡하네. 그냥 랭크섬으로 처리해"): 편당 조회 순위 + 참여율 순위(둘 다 높을수록 1위).
    # 합이 작을수록 좋다. 판정: 랭크섬 ≤ 전체 중앙값(상위 절반)이면 통과.
    ks = list(stat); n = len(ks)
    rv = {k: i + 1 for i, k in enumerate(sorted(ks, key=lambda k: -stat[k][0]))}
    re_ = {k: i + 1 for i, k in enumerate(sorted(ks, key=lambda k: -stat[k][1]))}
    rs = {k: rv[k] + re_[k] for k in ks}
    rs_cut = sorted(rs.values())[n // 2] if n else 0
    idx = {k: rs[k] for k in ks}  # 순위용(작을수록 좋음)
    return {'stat': stat, 'idx': idx, 'mv': mv, 'me': me, 'rp': rp, 'mr': mr, 'rv': rv, 're': re_, 'rs_cut': rs_cut, 'n': n}
def eng_factor(tk, S):
    # 랭킹용 참여 배수: 참여율 순위 1위 1.3 ~ 꼴찌 0.7, 신규 1.0
    tk = tk.upper()
    if tk not in S['re'] or S['n'] < 2: return 1.0
    return 1.3 - 0.6 * (S['re'][tk] - 1) / (S['n'] - 1)
def verdict(tk, S, _=None):
    tk = tk.upper()
    if tk not in S['idx']: return True, '신규'
    a, b = S['stat'][tk]
    return S['idx'][tk] <= S['rs_cut'], f"{round(a)}회({S['rv'][tk]}위)·참여율 {b*100:.1f}%({S['re'][tk]}위)·랭크섬 {S['idx'][tk]}/{S['rs_cut']}"
if __name__ == '__main__':
    S = load()
    print(f"랭크섬 = 편당 조회 순위 + 참여율((좋아요+댓글×2)/조회) 순위 · 종목 {S['n']}개 · 통과 = 랭크섬 {S['rs_cut']} 이하(상위 절반)")
    for t in sys.argv[1:]:
        ok, a = verdict(t, S); print(t.upper(), a, '통과' if ok else '컷오프')
