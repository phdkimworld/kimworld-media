#!/usr/bin/env python3
"""트래픽 컷오프(운영자 지시 11-05 "정규와 요청 모두에 트래픽 컷오프를 적용해서 트래픽 실적 안 좋은건 못 만들도록 해",
"할수 있으면 종목 컷오프 및 랭킹 시에 인게이지먼트 지표도 반영 해").
이미 만든 종목: 공개 3일 지난 롱폼 기준으로
  지수 = 0.7 × (편당 평균 조회 ÷ 종목별 중앙값) + 0.3 × (참여율 ÷ 종목별 중앙값)
  참여율 = (좋아요 + 댓글×2) ÷ 조회 수(운영자 11-05 "뷰나 좋아요는 조회수당으로 정규화") — stats_engagement.json, yt_stats.py가 매번 갱신
평균 시청 비율(stats_retention.json, yt-analytics 범위 토큰이 있을 때)이 있으면 조회 0.5·참여 0.25·시청 비율 0.25로 바꾼다.
판정(운영자 지시 11-06 "서로 보완하는게 아니라 둘다 통과해야 되도록 변경해", 같은 날 "참여율 기준 재량"): 편당 조회 ≥ 중앙값 **그리고**
조회 대비 참여 비율(같은 조회 수준의 기대 참여율 대비, log-log 회귀) ≥ 하위 25%선
(시청 비율 자료가 있으면 그것도 ≥ 중앙값)일 때만 통과. 지수는 순위·표시용으로만 쓰고 통과 여부에는 쓰지 않는다.
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
    # 조회 대비 참여(운영자 11-06 "참여율 기준 재량을 줄테니 최선의 랭킹법"): 참여율은 조회가 많을수록 낮아지는 경향
    # (log 참여율 = a + b·log 조회, 97종목 기울기 약 -0.56)이 있어, 같은 조회 수준에서 기대되는 참여율과 비교한다.
    import math
    pts = [(math.log(a), math.log(b)) for a, b in stat.values() if a > 0 and b > 0]
    if len(pts) >= 10:
        mx = sum(x for x, _ in pts) / len(pts); my = sum(y for _, y in pts) / len(pts)
        sxx = sum((x - mx) ** 2 for x, _ in pts) or 1
        b1 = sum((x - mx) * (y - my) for x, y in pts) / sxx; a1 = my - b1 * mx
    else:
        a1, b1 = math.log(me) if me else 0, 0.0
    er = {k: (b / math.exp(a1 + b1 * math.log(a)) if a > 0 and b > 0 else 0.0) for k, (a, b) in stat.items()}
    q = sorted(er.values()); e_cut = q[len(q) // 4] if q else 0  # 하위 25%선
    # 순위 점수: 조회 비율^0.7 × 조회 대비 참여 비율^0.3 (각 3배 상한) — 지수(1.0 = 중앙 수준)
    idx = {k: min(a / mv if mv else 1, 3.0) ** 0.7 * min(er[k], 3.0) ** 0.3 for k, (a, b) in stat.items()}
    return {'stat': stat, 'idx': idx, 'mv': mv, 'me': me, 'rp': rp, 'mr': mr, 'er': er, 'e_cut': e_cut, 'fit': (a1, b1)}
def eng_factor(tk, S):
    # 랭킹용 참여율 배수: 0.7 + 0.3 × (참여율 ÷ 중앙값, 3배 상한). 중앙값이면 1.0, 신규는 1.0
    tk = tk.upper()
    if tk not in S['stat']: return 1.0
    return 0.7 + 0.3 * min(S['er'].get(tk, 1.0), 3.0)  # 조회 대비 참여 비율 기준(11-06)
def verdict(tk, S, _=None):
    tk = tk.upper()
    if tk not in S['idx']: return True, '신규'
    a, b = S['stat'][tk]
    r = f"·시청 {S['rp'][tk]:.0f}%" if tk in S.get('rp', {}) else ''
    ok_v = a >= S['mv']; ok_e = S['er'][tk] >= S['e_cut']
    ok_r = (S['rp'][tk] >= S['mr']) if tk in S.get('rp', {}) and S.get('mr') else True
    why = '' if (ok_v and ok_e and ok_r) else '(' + '·'.join(x for x, o in (('조회 미달', ok_v), ('참여 미달', ok_e), ('시청 미달', ok_r)) if not o) + ')'
    return ok_v and ok_e and ok_r, f"{round(a)}회·참여율 {b*100:.1f}%(조회 대비 {S['er'][tk]:.2f}배){r}·지수 {S['idx'][tk]:.2f}{why}"
if __name__ == '__main__':
    S = load()
    print(f"중앙값: 편당 조회 {round(S['mv'])} · 참여율((좋아요+댓글×2)/조회) {S['me']*100:.1f}% (종목 {len(S['idx'])}개) · 통과 = 조회 ≥ 중앙값 그리고 조회 대비 참여 ≥ 하위 25%선({S['e_cut']:.2f}배)")
    for t in sys.argv[1:]:
        ok, a = verdict(t, S); print(t.upper(), a, '통과' if ok else '컷오프')
