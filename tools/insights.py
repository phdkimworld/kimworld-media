# 모든 아웃렛을 한 표로 묶어 보는 통합 인사이트(운영자 지시 2026-10-26 "매회 개선시 운영통계를 포함 모든 아웃렛에서 얻은
# 인사이트를 종합해서 모든 아웃렛들을 작성하는 지침을 최소 하나씩 수정. 개별적으로만 보지말고. 통합해서.")
# 사용: python3 tools/insights.py [사이트 저장소=/home/user/kimworld-site] [회차 수=10]
#  - 유튜브: stats_snapshots.jsonl에서 롱폼·쇼츠의 공개 뒤 약 24시간 조회수(처음 보인 스냅숏 기준)와 지금 조회수
#  - 사이트: 최신 운영 요약(analytics-report)의 리포트별 페이지뷰·초/뷰, 유입 채널·utm 위치, 구간 도달
#  - SNS·블로거: 지난 7일 게시 수(social/posted, social/blogger/posted.json)와 그 채널에서 온 세션
#  - 회차별 깔때기: 롱폼 24시간 조회 → 리포트 페이지뷰(전환 %) → 초/뷰, 그룹·후속편·요청 여부
# 출력은 집계 숫자만(개인정보·검색어 원문 없음). 끝에 '자동 관찰' 줄을 붙인다: 사람이 통합 판단을 쓰는 출발점이다.
import os, re, sys, json, glob, datetime as dt
sys.path.insert(0, os.path.dirname(__file__))
from report_perf import summary

SITE = sys.argv[1] if len(sys.argv) > 1 else '/home/user/kimworld-site'
N = int(sys.argv[2]) if len(sys.argv) > 2 else 10
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda t: dt.datetime.fromisoformat(t.replace('Z', '+00:00'))

def episodes():
    rows = []
    for l in open(os.path.join(HERE, 'review/experiments.md'), encoding='utf-8'):
        m = re.match(r'\| (\d+) \| ([\d-]+) \| ([^|]+)\| ([AB]) \|', l)
        if not m: continue
        ids = re.findall(r'· ([\w-]{11}) · 쇼츠 ([\w-]{11}) \|\s*$', l)
        if not ids: continue
        name = m.group(3).strip()
        rows.append({'no': int(m.group(1)), 'date': m.group(2), 'name': name, 'tk': re.match(r'[A-Z]+', name).group(0),
                     'group': m.group(4), 'long': ids[0][0], 'short': ids[0][1],
                     'kind': '요청' if '요청' in name else ('후속' if '업데이트' in name else '신규')})
    return rows[-N:]

def views():
    snaps = [json.loads(l) for l in open(os.path.join(HERE, 'stats_snapshots.jsonl'))]
    first, at24, now = {}, {}, snaps[-1]['v']
    for s in snaps:
        t = P(s['t'])
        for v, n in s['v'].items():
            first.setdefault(v, t)
            if t - first[v] <= dt.timedelta(hours=26): at24[v] = (n, round((t - first[v]).total_seconds() / 3600))
    return at24, now, P(snaps[-1]['t'])

def slug_of(ytid):
    for f in glob.glob(os.path.join(SITE, 'content/reports/*.md')):
        if re.search(r"^youtube_id: *['\"]?" + re.escape(ytid), open(f, encoding='utf-8').read(2000), re.M):
            return os.path.basename(f)[:-3]

def posted7(now):
    out = {}
    for f in glob.glob(os.path.join(SITE, 'social/posted/*.json')):
        d = json.load(open(f, encoding='utf-8'))
        if d.get('posted_at') and now - P(d['posted_at']) <= dt.timedelta(days=7):
            for c in d.get('channels', []): out[c] = out.get(c, 0) + 1
    b = json.load(open(os.path.join(SITE, 'social/blogger/posted.json'), encoding='utf-8'))
    out['blogger'] = sum(1 for v in b.values() if isinstance(v, dict) and v.get('at') and now - P(v['at']) <= dt.timedelta(days=7))
    return out

def main():
    when, s = summary()
    at24, now, tnow = views()
    pv = {r['path'].strip('/').split('/')[-1]: r for r in s.get('reports', [])}
    print(f'통합 인사이트 · 유튜브 스냅숏 {tnow:%m-%d %H:%M}Z · 사이트 요약 {when[:16]}Z (지난 {s.get("days")}일)\n')
    print('## 회차별 깔때기: 롱폼 24h 조회 → 쇼츠 24h → 리포트 페이지뷰(롱폼 24h 대비) · 초/뷰')
    rows = []
    for e in episodes():
        l24 = at24.get(e['long'], (None, 0)); s24 = at24.get(e['short'], (None, 0)); sl = slug_of(e['long']); r = pv.get(sl, {})
        conv = (r.get('pv', 0) / l24[0] * 100) if l24[0] else None
        rows.append((e, l24, s24, r, conv))
        print(f"  {e['no']:>2} {e['tk']:<5} {e['group']} {e['kind']}  롱폼 {l24[0] if l24[0] is not None else '-':>5}({l24[1]}h) 지금 {now.get(e['long'], '-'):>5}"
              f" · 쇼츠 {s24[0] if s24[0] is not None else '-':>5} 지금 {now.get(e['short'], '-'):>5}"
              f" · 리포트 {r.get('pv', 0):>3}pv {('%.1f%%' % conv) if conv is not None else '  -  ':>6} {r.get('secs/pv') or 0:>4.0f}초")
    camp = s.get('campaigns', [])
    p7 = posted7(tnow)
    print('\n## 아웃렛별 7일: 게시 수 → 사이트 세션')
    def cs(src):
        return sum(c.get('sess', 0) for c in camp if c.get('src') == src)
    for name, src, n in [('유튜브 고정댓글', 'youtube', None), ('Threads', 'threads', p7.get('threads', 0)), ('인스타그램', 'ig', p7.get('instagram', 0)),
                         ('페이스북', 'facebook', p7.get('facebook', 0)), ('블로거', 'blogger', p7.get('blogger', 0))]:
        print(f"  {name:<10} 게시 {n if n is not None else '-':>3} · 세션 {cs(src) if src != 'youtube' else '아래 위치별'}")
    print('  유튜브 위치별: ' + ', '.join(f"{c.get('cont')} {c.get('sess')}" for c in camp if c.get('src') == 'youtube'))
    print('  채널: ' + ', '.join(f"{c.get('ch')} {c.get('sess')}·{c.get('secs/sess') or 0:.0f}초" for c in (s.get('channels') or [])))
    sec = s.get('sections', {}).get('all') if isinstance(s.get('sections'), dict) else None
    # 자동 관찰: 사람이 통합 판단을 쓰는 출발점(근거 숫자 포함)
    print('\n## 자동 관찰')
    obs = []
    ok = [x for x in rows if x[4] is not None and x[1][0]]
    if ok:
        for key, lab in [('group', '그룹'), ('kind', '종류')]:
            g = {}
            for e, l24, s24, r, conv in ok: g.setdefault(e[key], []).append((l24[0], conv, r.get('secs/pv') or 0))
            obs.append(f'{lab}별 평균: ' + ' / '.join(f"{k} 롱폼24h {sum(a for a,_,_ in v)/len(v):.0f} · 전환 {sum(c for _,c,_ in v)/len(v):.1f}% · {sum(t for *_,t in v)/len(v):.0f}초/뷰 (n={len(v)})" for k, v in sorted(g.items())))
        best = max(ok, key=lambda x: x[4]); worst = min(ok, key=lambda x: x[4])
        obs.append(f"전환 최고 {best[0]['tk']} {best[4]:.1f}% · 최저 {worst[0]['tk']} {worst[4]:.1f}% (롱폼 24h {best[1][0]} vs {worst[1][0]})")
        sh = [(x[2][0], x[1][0]) for x in rows if x[2][0] is not None and x[1][0]]
        if sh: obs.append(f"쇼츠 24h ÷ 롱폼 24h 평균 {sum(a/b for a,b in sh)/len(sh):.2f}배 (n={len(sh)})")
    yt = {c.get('cont'): c.get('sess', 0) for c in camp if c.get('src') == 'youtube'}
    tot = sum(yt.values()) or 1
    obs.append('유튜브 유입 위치 비중: ' + ', '.join(f"{k} {v/tot*100:.0f}%" for k, v in sorted(yt.items(), key=lambda kv: -kv[1])))
    for name, src, key in [('Threads', 'threads', 'threads'), ('블로거', 'blogger', 'blogger'), ('페이스북', 'facebook', 'facebook'), ('인스타', 'ig', 'instagram')]:
        n = p7.get(key, 0); se = cs(src)
        obs.append(f"{name}: 게시 {n}건 → 세션 {se} ({(se/n if n else 0):.2f}/건)")
    sec = (s.get('sections') or {}).get('all') or {}
    if sec:
        drops = sorted(((k, sec[a][0] - sec[k][0]) for a, k in zip(list(sec)[1:-1], list(sec)[2:]) if isinstance(sec.get(k), list) and isinstance(sec.get(a), list)), key=lambda x: -x[1])[:2]
        best = max(((k, v[1]) for k, v in sec.items() if isinstance(v, list)), key=lambda x: x[1])
        obs.append('리포트 구간: 이탈 큰 곳 ' + ', '.join(f"{k} -{d:.0f}%p" for k, d in drops) + f" · 체류 최장 {best[0]} {best[1]:.0f}초 (n={sec.get('n')})")
    land = [x for x in s.get('landings', []) if x.get('src') not in ('youtube', 'direct')][:3]
    if land: obs.append('비유튜브 착지 상위: ' + ', '.join(f"{x['path'].strip('/').split('/')[-1]}←{x['src']} {x['sess']}세션·{x['secs']/max(x['sess'],1):.0f}초" for x in land))
    se = s.get('sentiment') or {}
    if se: obs.append(f"사이트 투표 {se.get('votes')}표(지난 기간 {se.get('prevVotes')}) · 종목 {se.get('tickers')}개")
    tt = s.get('totals') or {}
    if tt: obs.append('사이트 합계: ' + ', '.join(f"{k} {v['now']}({v['chg_pct']:+.0f}%)" for k, v in tt.items() if isinstance(v, dict) and 'now' in v))
    for o in obs: print('  - ' + o)

if __name__ == '__main__':
    main()
