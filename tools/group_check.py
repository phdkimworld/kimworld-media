# 대본이 실험 그룹 조건에 맞는지 TTS 전에 본다(2026-10-24 EU 33회차 교훈: B그룹인데 A 위치 안내·A 길이로 써서 TTS를 다시 돌림).
# 사용: python3 group_check.py <narration.txt> <A|B>
#  - E10: A = 리포트 안내('홈페이지에 무료로')가 '첫 번째 단서' 앞 문단 / B = '첫 번째 단서' 문단 안
#  - E12 길이: A = 9.0~9.6KB(약 8분) / B = 11.0KB 이상(10~12분, 9.15KB가 8분 25초였음)
import sys
txt = open(sys.argv[1]).read(); g = sys.argv[2].upper()
paras = [p for p in txt.split('\n\n') if p.strip()]
clue = next((i for i, p in enumerate(paras) if p.startswith('첫 번째 단서')), None)
guide = [i for i, p in enumerate(paras) if '홈페이지에 무료로' in p]
kb = len(txt.encode()) / 1000; bad = []
if clue is None: bad.append("'첫 번째 단서'로 시작하는 문단 없음")
elif not guide: bad.append("리포트 안내 문장('홈페이지에 무료로') 없음")
elif g == 'A' and guide[0] >= clue: bad.append(f'E10 A: 안내가 p{guide[0]+1}, 첫 단서(p{clue+1}) 앞이어야 함')
elif g == 'B' and guide[0] != clue: bad.append(f'E10 B: 안내가 p{guide[0]+1}, 첫 단서 문단(p{clue+1}) 안이어야 함')
if g == 'A' and not 9.0 <= kb <= 9.6: bad.append(f'E12 A: 대본 {kb:.2f}KB, 9.0~9.6KB')
if g == 'B' and kb < 11.0: bad.append(f'E12 B: 대본 {kb:.2f}KB, 11.0KB 이상')
print('\n'.join(bad) if bad else f'GROUP_OK {g} {kb:.2f}KB 안내 p{guide[0]+1}')
sys.exit(1 if bad else 0)
