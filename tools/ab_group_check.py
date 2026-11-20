#!/usr/bin/env python3
"""experiments.md '적용 기록'의 조(A/B)가 회차 번호 규칙(홀수 B · 짝수 A)과 맞는지 검사.
11-20: 101·103·105가 홀수인데 A로 적혀 들어간 실수를 막는다(운영자 바로잡기 ①).
사용: python3 tools/ab_group_check.py [--from 106] [--expect N]   → AB_OK | AB_FAIL (n=… 조 X, 규칙 Y)
--expect N: 다음 회차 N의 조를 출력(A|B)만 한다(제작 시작 때 조 정하기)."""
import re, sys, os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'review', 'experiments.md')
rule = lambda n: 'B' if n % 2 else 'A'
if '--expect' in sys.argv:
    print(rule(int(sys.argv[sys.argv.index('--expect') + 1]))); sys.exit(0)
start = int(sys.argv[sys.argv.index('--from') + 1]) if '--from' in sys.argv else 106
t = open(P).read(); t = t[t.index('## 적용 기록'):t.index('## 시험 A 회차표')]
bad, n = [], 0
for m in re.finditer(r'^\| (\d+) \| (\d\d-\d\d) \| ([^|]+)\| ([AB]) \|', t, re.M):
    k, g = int(m.group(1)), m.group(4)
    if k < start: continue
    n += 1
    if g != rule(k): bad.append(f'{k} 조 {g}, 규칙 {rule(k)} ({m.group(3).strip()[:20]})')
print('AB_FAIL ' + ' · '.join(bad) if bad else f'AB_OK {n}행(회차 {start}~)'); sys.exit(1 if bad else 0)
