#!/usr/bin/env python3
"""영양제 중간광고 전환 추적 (운영자 2026-11-21 "광고 전환율도 잘 추적해서 매회 개선해 나가").

깔때기: 롱폼 조회(stats_snapshots) → 건강몰 방문(utm_medium=midroll, utm_campaign=<리포트 slug>)
        → 쿠팡 클릭·주문·수수료(가이드 sub: hmomega·hmlutein·hmprobio …).
자료: 비공개 통계 /home/claude/kimworld-ops/stats/{analytics.json(hmall),coupang.json(by_sub)}
      (report_perf.summary()가 git이 아니면 다시 받음), 회차 기록 review/improvements.md '네 지표' 표,
      광고 코드↔회차 표 review/ad_log.md(회차마다 한 줄: 날짜|slug|영상ID|코드|성분|위치초|슬라이드).
사용: python3 tools/ad_conv.py            # 표 출력 + review/ad_conv.md 갱신
      python3 tools/ad_conv.py --add <날짜> <slug> <영상ID> <H1|H2|H3> <위치초> <슬라이드 설명>
출력 끝 '다음 회차 개선안' 줄은 자동 관찰(사람이 판단해 하나를 적용).
2026-11-26 운영자 "링크는 이제 몰이 아니라 제품 링크를 바로 달기로 했어": 💊 줄이 쿠팡 제품으로 바로 가므로 회차 지표는
  쿠팡 하위 ID md<성분 2자><티커>(tools/product_link.py, health_midroll 10절)의 클릭·주문·수수료가 주(主)이고, 건강몰 방문(utm)은 옛 회차·보조.
"""
import json, os, re, sys, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OPS = os.environ.get('OPS_DIR', '/home/claude/kimworld-ops')
LOG = os.path.join(ROOT, 'review', 'ad_log.md')
OUT = os.path.join(ROOT, 'review', 'ad_conv.md')
CODES = {'H1': ('omega3', 'hmomega'), 'H2': ('lutein', 'hmlutein'), 'H3': ('probiotics', 'hmprobio')}
TWO = {'H1': 'om', 'H2': 'lu', 'H3': 'pb'}
MD_FROM = '2026-11-26'  # 회차 하위 ID md<2자><티커> (product_link.py CODES와 같게)


def md_sub(code, slug):
    return re.sub(r'[^a-z0-9]', '', f"md{TWO.get(code, 'xx')}{slug.split('-')[0].lower()}")[:20]


def load(p, d):
    try:
        return json.load(open(p, encoding='utf-8'))
    except Exception:
        return d


def ensure_log():
    if not os.path.exists(LOG):
        open(LOG, 'w', encoding='utf-8').write(
            '# 영양제 중간광고 회차 기록 (tools/ad_conv.py가 읽음)\n\n'
            '| 날짜 | 리포트 slug | 영상ID | 코드 | 성분 | 위치(초) | 슬라이드 |\n|---|---|---|---|---|---|---|\n')


def read_log():
    ensure_log()
    rows = []
    for ln in open(LOG, encoding='utf-8'):
        c = [x.strip() for x in ln.strip().strip('|').split('|')]
        if len(c) >= 7 and re.match(r'\d{4}-\d{2}-\d{2}', c[0]):
            rows.append(dict(date=c[0], slug=c[1], vid=c[2], code=c[3], ing=c[4], pos=c[5], slide=c[6]))
    return rows


def views(vid):
    p = os.path.join(ROOT, 'stats_snapshots.jsonl')
    last = None
    try:
        for ln in open(p, encoding='utf-8'):
            if vid in ln:
                last = json.loads(ln).get('v', {}).get(vid, last)
    except Exception:
        pass
    return last


def main():
    a = sys.argv[1:]
    if a[:1] == ['--add']:
        if len(a) < 7:
            sys.exit('사용: --add <날짜> <slug> <영상ID> <코드> <위치초> <슬라이드>')
        ensure_log()
        code = a[4].upper()
        ing = CODES.get(code, ('?', '?'))[0]
        open(LOG, 'a', encoding='utf-8').write(f'| {a[1]} | {a[2]} | {a[3]} | {code} | {ing} | {a[5]} | {" ".join(a[6:])} |\n')
        print('ADDED', a[2], code)
        return
    try:
        sys.path.insert(0, HERE)
        import report_perf  # 사본이 git이 아니면 다시 받는다
        report_perf.summary()
    except Exception:
        pass
    an = load(os.path.join(OPS, 'stats', 'analytics.json'), {})
    cp = load(os.path.join(OPS, 'stats', 'coupang.json'), {})
    hm = an.get('hmall') or {}
    camp = {}
    for r in hm.get('campaigns') or []:
        k = r.get('camp') or r.get('campaign') or r.get('c')
        if k and (r.get('med') in (None, 'midroll') or 'midroll' in json.dumps(r)):
            camp[k] = camp.get(k, 0) + int(r.get('sess') or r.get('sessions') or 0)
    bysub = cp.get('by_sub') or {}
    rows = read_log()
    lines = ['# 영양제 중간광고 전환 (자동 생성: tools/ad_conv.py, %s)' % dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%MZ'),
             '', f"자료: 건강몰 분석 {'있음' if hm.get('totals') else '비어 있음'} · 쿠팡 기간 {an.get('days', '?')}일 · 회차 {len(rows)}",
             '', '| 날짜 | 회차 | 코드 | 위치 | 롱폼 조회 | 제품 클릭(md 하위 ID) | 클릭/1만 조회 | 건강몰 방문(옛 midroll) |', '|---|---|---|---|---|---|---|---|']
    agg = {}
    for r in rows:
        v = views(r['vid']) or 0
        s = camp.get(r['slug'], 0)
        new = r['date'] >= MD_FROM  # 11-26~ 제품 직접 링크 회차만 md 하위 ID가 있다
        sid = md_sub(r['code'], r['slug']); c = int((bysub.get(sid) or {}).get('clicks') or 0) if new else 0
        rate = f'{(c if new else s) / v * 10000:.1f}' if v else '-'
        lines.append(f"| {r['date']} | {r['slug']} | {r['code']} | {r['pos']}초 | {v} | {f'{c} ({sid})' if new else '- (가이드 링크 회차)'} | {rate} | {s} |")
        g = agg.setdefault(r['code'], [0, 0, 0, 0])
        g[0] += 1; g[1] += v; g[2] += s; g[3] += c
    lines += ['', '| 코드 | 성분 | 회차 수 | 조회 합 | 제품 클릭(md) | 클릭/1만 조회 | md 주문 | md 수수료(원) | 건강몰 방문 | 가이드 쿠팡 클릭(hm) |', '|---|---|---|---|---|---|---|---|---|---|']
    best = None
    for code, (ing, sub) in CODES.items():
        n, v, s, c = agg.get(code, [0, 0, 0, 0])
        b = bysub.get(sub) or {}
        md = [x for k, x in bysub.items() if k.startswith('md' + TWO[code]) and isinstance(x, dict)]
        mo = sum(int(x.get('orders') or 0) for x in md); mc = sum(int(x.get('commission') or 0) for x in md)
        rate = ((c or s) / v * 10000) if v else None  # 제품 클릭이 있으면 그것, 옛 회차뿐이면 건강몰 방문
        if rate is not None and (best is None or rate > best[1]):
            best = (code, rate)
        lines.append(f"| {code} | {ing} | {n} | {v} | {c} | {('%.1f' % rate) if rate is not None else '-'} | {mo} | {mc} | {s} | {b.get('clicks', 0)} |")
    lines += ['', '## 자동 관찰', ]
    if not rows:
        lines.append('- 아직 광고 회차 없음 — 첫 회차부터 `--add`로 기록한다.')
    if not hm.get('totals'):
        lines.append('- 건강몰 분석(hmall)이 비어 있음 — 방문 수는 0으로 보인다. 사이트 analytics-report의 hmall 수집을 확인할 것(쿠팡 sub 클릭은 별도로 집계됨).')
    if best:
        lines.append(f'- 지금까지 제품 클릭(옛 회차는 건강몰 방문)/1만 조회 최고: {best[0]} ({best[1]:.1f}). 표본이 회차 3개 미만이면 관찰 중.')
    lines.append('- 11-26~ 회차는 쿠팡 하위 ID md<성분><티커>로 본다(쿠팡 실적은 하루 늦게 들어온다). 옛 회차(건강몰 가이드 링크)는 건강몰 방문 칸.')
    lines.append('- 다음 회차 개선안 후보: ① 위치(답 공개 직후 vs 시나리오 직후) ② 슬라이드(비교 막대 vs 문구 카드) ③ 연결 문장(검진표·눈·장) ④ 설명란 줄 위치 — 한 번에 하나만 바꾸고 improvements.md 네 지표 표에 적는다.')
    txt = '\n'.join(lines) + '\n'
    open(OUT, 'w', encoding='utf-8').write(txt)
    print(txt)


if __name__ == '__main__':
    main()
