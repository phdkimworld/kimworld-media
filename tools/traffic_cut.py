#!/usr/bin/env python3
"""트래픽 컷오프(운영자 지시 11-05 "정규와 요청 모두에 트래픽 컷오프를 적용해서 트래픽 실적 안 좋은건 못 만들도록 해").
이미 만든 종목: 공개 3일 지난 롱폼의 편당 평균 조회 < 채널 종목별 편당 평균의 중앙값 → 컷오프(제작 불가).
한 번도 만든 적 없거나 3일 지난 영상이 없는 종목은 '신규'로 통과. 사용: python3 tools/traffic_cut.py [티커…]
"""
import glob, re, os, json, datetime, sys
HERE = os.path.dirname(os.path.abspath(__file__)); MEDIA = os.path.dirname(HERE)
SITE = os.path.join(os.path.dirname(MEDIA), 'kimworld-site')
def load():
    v = json.loads(open(os.path.join(MEDIA, 'stats_snapshots.jsonl')).readlines()[-1])['v']
    today = datetime.date.today(); per = {}
    for f in glob.glob(os.path.join(SITE, 'content/reports/*.md')):
        h = open(f, encoding='utf-8').read(4000)
        tk = re.search(r"^ticker:\s*['\"]?([A-Za-z0-9.]+)", h, re.M)
        y = re.search(r"^youtube_id:\s*['\"]?([\w-]{6,})", h, re.M)
        d = re.search(r"^date:\s*['\"]?(\d{4}-\d\d-\d\d)", h, re.M)
        if not (tk and y and d) or y.group(1) not in v: continue
        if (today - datetime.date.fromisoformat(d.group(1))).days < 3: continue
        per.setdefault(tk.group(1).upper(), []).append(v[y.group(1)])
    avg = {k: sum(x) / len(x) for k, x in per.items()}
    med = sorted(avg.values())[len(avg) // 2] if avg else 0
    return avg, med
def verdict(tk, avg, med):
    tk = tk.upper()
    if tk not in avg: return True, '신규'
    return avg[tk] >= med, round(avg[tk])
if __name__ == '__main__':
    avg, med = load()
    print(f'편당 평균 조회 중앙값 {round(med)} (종목 {len(avg)}개, 공개 3일 지난 롱폼)')
    for t in sys.argv[1:]:
        ok, a = verdict(t, avg, med); print(t.upper(), a, '통과' if ok else '컷오프')
