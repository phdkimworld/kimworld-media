# 회차 번호 충돌 검사(83회차 SLDP, 81회차 LAES 복기 '동시 제작 ASST가 82회차를 먼저 잡아 LAES가 대본을 다시 씀').
# 사용: python3 tools/episode_check.py [STATE.md]  — 같은 회차 번호가 다른 종목 행에 두 번 이상 있으면 FAIL.
# 동시 제작 규칙: 시작하자마자 STATE.md에 '<티커>(NN회차, ...)' 행을 커밋·푸시하고, 충돌하면 뒤에 푸시한 쪽이 다음 번호로 바꾼다.
import re, sys, os
p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'production', 'STATE.md')
seen = {}; bad = []
for ln in open(p, encoding='utf-8'):
    if not ln.startswith('|'): continue
    c = [x.strip() for x in ln.strip().strip('|').split('|')]
    if len(c) < 3: continue
    for n in re.findall(r'(\d{2,3})회차', c[2]):
        tk = (re.match(r'[A-Z0-9.]+|선정 중', c[2]) or [c[2][:8]])[0]
        if n in seen and seen[n] != tk: bad.append(f'{n}회차: {seen[n]} / {tk}')
        seen.setdefault(n, tk)
print('\n'.join('EPISODE_DUP ' + b for b in bad) if bad else f'EPISODE_OK 회차 {len(seen)}개')
sys.exit(1 if bad else 0)
