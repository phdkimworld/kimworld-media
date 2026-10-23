#!/usr/bin/env python3
"""미국 주식 거래일 계산(NYSE 휴장일 반영).

규칙: 'N거래일 뒤'는 기준일(보통 사건 전 종가일)에서 거래일을 N번 넘긴 날이다.
  예) 실적 전 종가 10/21 기준 20거래일 뒤 = 10/22가 1, ... 20번째 = 11/18
대본·리포트·followups.md에 미래 날짜를 쓸 때는 손으로 세지 않고 이 도구 출력을 붙인다
(2026-10-23 QS 회차에서 11/18과 11/19를 헷갈린 일이 있었다).

  python3 tools/tdays.py add 2026-10-21 20      # 기준일 + 20거래일
  python3 tools/tdays.py diff 2026-10-21 2026-11-18   # 두 날짜 사이 거래일 수
  python3 tools/tdays.py next 2026-10-21        # 다음 거래일(장 마감 뒤 발표의 첫 반응일)
"""
import datetime as dt
import sys

HOLIDAYS = {
    # 2025
    '2025-01-01', '2025-01-09', '2025-01-20', '2025-02-17', '2025-04-18', '2025-05-26',
    '2025-06-19', '2025-07-04', '2025-09-01', '2025-11-27', '2025-12-25',
    # 2026
    '2026-01-01', '2026-01-19', '2026-02-16', '2026-04-03', '2026-05-25', '2026-06-19',
    '2026-07-03', '2026-09-07', '2026-11-26', '2026-12-25',
    # 2027
    '2027-01-01', '2027-01-18', '2027-02-15', '2027-03-26', '2027-05-31', '2027-06-18',
    '2027-07-05', '2027-09-06', '2027-11-25', '2027-12-24',
}
KNOWN_YEARS = {2025, 2026, 2027}


def d(s):
    return dt.date.fromisoformat(s)


def is_td(x):
    if x.year not in KNOWN_YEARS:
        raise SystemExit(f'{x.year}년 휴장일이 없습니다. HOLIDAYS에 추가하세요.')
    return x.weekday() < 5 and x.isoformat() not in HOLIDAYS


def add(base, n):
    x, k = base, 0
    step = 1 if n >= 0 else -1
    while k != n:
        x += dt.timedelta(days=step)
        if is_td(x):
            k += step
    return x


def diff(a, b):
    sign = 1 if b >= a else -1
    lo, hi = min(a, b), max(a, b)
    n, x = 0, lo
    while x < hi:
        x += dt.timedelta(days=1)
        if is_td(x):
            n += 1
    return sign * n


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[0]
    if cmd == 'add' and len(argv) == 3:
        r = add(d(argv[1]), int(argv[2]))
        print(r.isoformat(), '월화수목금토일'[r.weekday()])
    elif cmd == 'diff' and len(argv) == 3:
        print(diff(d(argv[1]), d(argv[2])))
    elif cmd == 'next':
        r = add(d(argv[1]), 1)
        print(r.isoformat(), '월화수목금토일'[r.weekday()])
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
