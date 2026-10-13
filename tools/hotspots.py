# hourly_views.jsonl(매시 기록)로 요일·시각(미국 동부시간)별 채널 조회수 분포와 오전·오후 핫스팟을 계산한다.
# 두 기록 사이에 늘어난 조회수를 그 구간의 시간에 고르게 나눠 해당 요일·시각 칸에 더한 뒤, 칸마다 관측 주 수로 나눠 평균을 낸다.
# 사용: python3 tools/hotspots.py [기록 파일] [--md]  →  JSON(기본) 또는 SKILL.md 표(--md)
# 주의: 공개 조회수(viewCount)는 실시간이 아니라 몇 시간 단위로 묶여 갱신될 수 있다. 2주 이상 쌓인 뒤 판단한다.
import os, sys, json, datetime
from zoneinfo import ZoneInfo
ET = ZoneInfo('America/New_York'); DAYS = '월화수목금토일'

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    path = args[0] if args else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hourly_views.jsonl')
    rows = [json.loads(l) for l in open(path) if l.strip()]
    rows.sort(key=lambda r: r['t'])
    acc = {(d, h): 0.0 for d in range(7) for h in range(24)}; seen = {(d, h): set() for d in range(7) for h in range(24)}
    for a, b in zip(rows, rows[1:]):
        t0 = datetime.datetime.fromisoformat(a['t']); t1 = datetime.datetime.fromisoformat(b['t'])
        hrs = (t1 - t0).total_seconds() / 3600
        if hrs <= 0 or hrs > 6: continue          # 6시간 넘게 빈 구간은 버린다
        gain = b['total'] - a['total']
        if gain < 0: continue
        steps = max(1, round(hrs * 4))            # 15분 단위로 쪼개 칸에 나눠 담는다
        for i in range(steps):
            m = (t0 + (t1 - t0) * ((i + 0.5) / steps)).astimezone(ET)
            k = (m.weekday(), m.hour); acc[k] += gain / steps; seen[k].add(m.date())
    avg = {k: (acc[k] / len(seen[k]) if seen[k] else None) for k in acc}
    res = {'from': rows[0]['t'] if rows else None, 'to': rows[-1]['t'] if rows else None, 'samples': len(rows), 'days': []}
    for d in range(7):
        am = [(avg[(d, h)], h) for h in range(0, 12) if avg[(d, h)] is not None]
        pm = [(avg[(d, h)], h) for h in range(12, 24) if avg[(d, h)] is not None]
        weeks = min((len(seen[(d, h)]) for h in range(24)), default=0)
        res['days'].append({'day': DAYS[d], 'weeks': weeks, 'am': max(am)[1] if am else None, 'pm': max(pm)[1] if pm else None,
                            'by_hour': [round(avg[(d, h)], 1) if avg[(d, h)] is not None else None for h in range(24)]})
    if '--md' in sys.argv:
        print('| 요일 | 오전 발행 | 오후 발행 | 관측 주 |\n| --- | --- | --- | --- |')
        for x in res['days']:
            f = lambda h: '%02d:00' % h if h is not None else '-'
            print('| %s | %s | %s | %d |' % (x['day'], f(x['am']), f(x['pm']), x['weeks']))
    else:
        print(json.dumps(res, ensure_ascii=False))

if __name__ == '__main__':
    main()
