# 리포트 독자 반응 보기(SKILL R장 '리포트 개선 실험'의 근거): 사이트 운영 요약(Analytics report 워크플로 주석)에서
# 리포트별 페이지뷰·페이지뷰당 초·스크롤과 구간별 도달·체류 곡선을 읽고, 리포트 모양(글자 수·카드 수·후속편 여부)과 함께 보인다.
# 사용: python3 report_perf.py [사이트 저장소=/home/claude/kimworld-site]
#  - 최신 실행이 오래됐으면 먼저 GitHub MCP actions_run_trigger(analytics-report.yml, ref main)로 새로 돌린다
#  - 주석은 공개 API로 읽는다(집계 숫자만 들어 있다)
import os, re, sys, json, glob, urllib.request

SITE = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/kimworld-site'
API = 'https://api.github.com/repos/phdkimworld/kimworld-site'
NAMES = {'top': '머리(요약)', 'ans': '짧은 답', 'can': '이 리포트에서', 'news': '같은 뉴스', 'term': '용어', 'p1': '1부', 'p2': '2부',
         'p3': '3부 카드', 'p4': '4부 패턴', 'p5': '5부 전략', 'p6': '6부 리스크', 'src': '출처', 'more': '다음 리포트', 'comm': '이야기'}

def get(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'kimworld-report-perf'})))

def summary():
    run = get(API + '/actions/workflows/analytics-report.yml/runs?per_page=1')['workflow_runs'][0]
    job = get(API + f"/actions/runs/{run['id']}/jobs")['jobs'][0]
    out = {}
    for a in get(API + f"/check-runs/{job['id']}/annotations?per_page=50"):
        if re.match(r'AN \d+/\d+$', a['title']):
            out.update(json.loads(a['message']))
    return run['created_at'], out

def shape(slug):
    p = os.path.join(SITE, 'content/reports', slug + '.md')
    if not os.path.exists(p):
        return {}
    t = open(p, encoding='utf-8').read()
    body = t.split('\n---', 2)[-1]
    return {'chars': len(re.sub(r'\s', '', body)), 'cards': len(re.findall(r'^\*\*\d{4}\.\d\d\.\d\d', body, re.M)),
            'follow': bool(re.search(r'^## 지난 리포트 이후', body, re.M)), 'theme': (re.search(r'^theme:\s*(.+)$', t, re.M) or [None, ''])[1].strip()}

def main():
    when, s = summary()
    print(f'운영 요약 {when} (지난 {s.get("days")}일)\n')
    print('## 리포트별(페이지뷰 순): 페이지뷰 · 초/뷰 · 스크롤% · 본문 글자 · 카드 · 후속편')
    for r in s.get('reports', []):
        slug = r['path'].strip('/').split('/')[-1]; sh = shape(slug)
        print(f"  {slug:<22} {r.get('pv', 0):>4} {r.get('secs/pv') or 0:>5.0f}초 {r.get('scroll_pct') or 0:>4.0f}%  "
              f"{sh.get('chars', 0):>6} {sh.get('cards', 0):>3} {'후속' if sh.get('follow') else '':<2} {sh.get('theme', '')}")
    sec = s.get('sections') or {}
    def line(name, c):
        if not c:
            print(f'  {name}: 아직 자료 없음'); return
        cells = [f"{NAMES.get(k, k)} {v[0]:.0f}%·{v[1]:.0f}초" for k, v in c.items() if k != 'n']
        print(f"  {name} (n={c['n']}): " + ' → '.join(cells))
    print('\n## 구간별 도달·체류(첫 구간 대비 도달 %, 도달한 사람 평균 초)')
    line('전체', sec.get('all'))
    for p, c in (sec.get('reports') or {}).items():
        line(p.strip('/').split('/')[-1], c)

if __name__ == '__main__':
    main()
