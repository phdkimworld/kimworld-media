# 숫자 + 단위 뒤 조사 받침 불일치를 녹음 전에 잡는다(76회차 RUM: '열여섯 번'을 '십육 회'로 일괄 치환하다 '십육 회이'가 녹음 직전까지 남음).
# 사용: python3 josa_check.py <narration.txt|리포트.md> … → JOSA_OK 또는 'JOSA <문단> <구절>' 줄(종료 코드 1)
# 단위 앞에 한글 수사(일이삼…십백천만)나 아라비아 숫자가 있을 때만 본다(일반 낱말 오탐 방지).
import re, sys
UNITS = '회|번|개|주|년|달|배|일|월|명|건|곳|센트|달러|퍼센트|포인트|거래일|분기|가지|차례'
PAIR = {'이': '가', '은': '는', '을': '를', '과': '와', '가': '이', '는': '은', '를': '을', '와': '과'}
def has_final(ch):
    o = ord(ch) - 0xAC00
    return 0 <= o < 11172 and o % 28 != 0
pat = re.compile(r'(?:[일이삼사오육칠팔구십백천만영]|\d)\s?(' + UNITS + r')(이|은|을|과|가|는|를|와)(?=[\s.,?!)」]|$)')
bad = []
for f in sys.argv[1:]:
    for i, para in enumerate(open(f, encoding='utf-8').read().split('\n\n'), 1):
        for m in pat.finditer(para):
            unit, j = m.group(1), m.group(2)
            fin = has_final(unit[-1])
            if (fin and j in '가는를와') or (not fin and j in '이은을과'):
                bad.append(f'JOSA {f.split("/")[-1]} p{i} "{m.group(0).strip()}" → "{unit}{PAIR[j]}"')
print('\n'.join(bad) if bad else 'JOSA_OK')
sys.exit(1 if bad else 0)
