#!/usr/bin/env python3
"""영상 슬라이드 숫자 ↔ 리포트 대조(합성 전 검사).

slides.json의 화면 글자에서 가격($4.15)·등락률(+4.3%)·날짜(2025.06.24)를 뽑아
리포트 본문에 같은 값이 있는지 본다. 리포트에 없는 숫자는 MISS로 알린다.
'$A → $B' 라벨과 같은 화면의 배수·%가 두 가격으로 계산한 값과 다르면 CALC로 알린다.

  python3 tools/num_check.py <slides.json> <report.md>
종료 코드: MISS·CALC가 없으면 0, 있으면 1. MISS는 고치거나(대본·화면 오류),
리포트에 그 숫자를 넣거나(리포트 누락), 그대로 둘 이유가 있으면 slides.json 옆 num_check.ok에
'MISS p3 s3 날짜 2025.12.31 | 이유' 처럼 그 줄과 이유를 적는다(적힌 줄은 통과).
(2026-10-23 QS 회차 복기: 사실 오류 2건·용어 오역이 합성 뒤에야 잡혔다)
"""
import json
import os
import re
import sys

PRICE = re.compile(r'\$(\d[\d,]*(?:\.\d+)?)(?![\d.,~])(?!\s*(?:million|billion|억|만|M\b|B\b))')
MONEY = re.compile(r'\$(\d[\d,]*(?:\.\d+)?)(?:~\d[\d,]*(?:\.\d+)?)?\s*(million|billion|M\b|B\b)')
PCT = re.compile(r'([+\-−]?\d[\d,]*(?:\.\d+)?)%')
DATE = re.compile(r'(20\d\d)\.(\d{1,2})\.(\d{1,2})')
ARROW = re.compile(r'\$(\d[\d,]*(?:\.\d+)?)\s*→\s*\$(\d[\d,]*(?:\.\d+)?)')
# '807억$'·'46.6억$어치'·'1,316.5억 달러' 같은 억 단위 달러 금액(2026-10-26 앤트로픽 40회차: 리포트에 없는 46.6억·89억이 화면에 있었는데 검사가 세지 않음)
EOK = re.compile(r'(\d[\d,]*(?:\.\d+)?)(?:조)?억\s*(?:\$|달러)')
TIMES = re.compile(r'(\d+(?:\.\d+)?)배')


def strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for k, v in o.items():
            if k not in ('layout', 'tone', 'sfx', 'from', 'at', 'ad'):
                yield from strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings(v)


def num(s):
    return float(s.replace(',', '').replace('−', '-'))


def fmt_variants(x):
    out = set()
    for p in range(0, 4):
        s = f'{x:.{p}f}'
        out.add(s)
        if '.' in s:
            out.add(s.rstrip('0').rstrip('.'))
        out.add(f'{x:,.{p}f}')
    return out


def korean_money(dollars):
    """130_700_000 → '1억 3,070만', 75_400_000 → '7,540만'"""
    man = round(dollars / 10_000)
    eok, rest = divmod(man, 10_000)
    out = []
    if eok:
        out.append(f'{eok}억')
    if rest:
        out.append(f'{rest:,}만')
    return ' '.join(out)


def in_report(rep, kind, val, raw):
    if kind == 'money':
        k = korean_money(val)
        return k in rep or k.replace(' ', '') in rep.replace(' ', '')
    if kind == 'price':
        for v in fmt_variants(val):
            if f'${v}' in rep or f'{v}달러' in rep or f'{v} 달러' in rep:
                return True
        cents = round(val * 100)
        if val < 1 and (f'{cents}센트' in rep):
            return True
        return False
    if kind == 'pct':
        a = abs(val)
        for v in fmt_variants(a):
            if re.search(r'(?<![\d.])' + re.escape(v) + r'\s*(%|퍼센트)', rep):
                return True
        return False
    if kind == 'date':
        y, m, dd = raw
        pats = [f'{y}-{int(m):02d}-{int(dd):02d}', f'{y}.{int(m):02d}.{int(dd):02d}',
                f'{int(m)}월 {int(dd)}일', f'{int(m)}/{int(dd)}']
        return any(p in rep for p in pats)
    return True


def half_unit(raw):
    raw = raw.replace(',', '')
    return 0.5 * 10 ** -(len(raw.split('.')[1]) if '.' in raw else 0)


def units(sl):
    """계산 대조 단위: stat 항목 하나, compare 왼쪽·오른쪽 하나씩"""
    if 'stats' in sl:
        return [dict(st, title=sl.get('title', '')) for st in sl['stats']]
    if 'items' in sl:
        return sl['items']
    if 'left' in sl or 'right' in sl:
        return [sl[k] for k in ('left', 'right') if k in sl]
    return [sl]


def derivable(pct, para, rep):
    """같은 문단 화면의 두 가격(둘 다 리포트에 있음)으로 계산되는 %면 통과"""
    ps = [num(x) for x in PRICE.findall(' '.join(strings(para)))]
    ps = [x for x in ps if in_report(rep, 'price', x, None)]
    for a in ps:
        for b in ps:
            if a and abs((b / a - 1) * 100 - pct) <= 0.15:
                return True
    return False


def main(slides_path, report_path):
    slides = json.load(open(slides_path))
    rep = open(report_path).read()
    miss, calc, seen, n = [], [], set(), 0
    for pi, para in enumerate(slides.get('paras', []), 1):
        for si, sl in enumerate(para.get('slides', []), 1):
            text = ' '.join(strings(sl))
            for m in PRICE.finditer(text):
                key = ('price', m.group(1))
                if key in seen:
                    continue
                seen.add(key); n += 1
                v = num(m.group(1))
                # $250,000,000 같은 원문 인용 금액은 '2억 5,000만'으로도 찾는다
                if not in_report(rep, 'price', v, None) and not (v >= 1e6 and in_report(rep, 'money', v, None)):
                    miss.append(f'p{pi} s{si} 가격 ${m.group(1)}')
            for m in MONEY.finditer(text):
                key = ('money', m.group(0))
                if key in seen:
                    continue
                seen.add(key); n += 1
                mult = 1e6 if m.group(2) in ('million', 'M') else 1e9
                if not in_report(rep, 'money', num(m.group(1)) * mult, None):
                    miss.append(f'p{pi} s{si} 금액 {m.group(0)} ({korean_money(num(m.group(1)) * mult)} 달러)')
            for m in EOK.finditer(text):
                key = ('eok', m.group(1))
                if key in seen:
                    continue
                seen.add(key); n += 1
                # 화면의 '약 596억$'는 리포트 595.97억을 반올림한 값이면 통과(같은 소수 자릿수로 반올림해 대조)
                dp = len(m.group(1).split('.')[1]) if '.' in m.group(1) else 0
                reps = {round(num(x), dp) for x in re.findall(r'(?<![\d.,])(\d[\d,]*(?:\.\d+)?)억', rep)}
                if round(num(m.group(1)), dp) not in reps:
                    miss.append(f'p{pi} s{si} 억 달러 {m.group(1)}억')
            for m in PCT.finditer(text):
                key = ('pct', m.group(1))
                if key in seen:
                    continue
                seen.add(key); n += 1
                if not in_report(rep, 'pct', num(m.group(1)), None) and not derivable(num(m.group(1)), para, rep):
                    miss.append(f'p{pi} s{si} 등락 {m.group(1)}%')
            for m in DATE.finditer(text):
                key = ('date', m.group(0))
                if key in seen:
                    continue
                seen.add(key); n += 1
                if not in_report(rep, 'date', None, m.groups()):
                    miss.append(f'p{pi} s{si} 날짜 {m.group(0)}')
            for unit in units(sl):
                utext = ' '.join(strings(unit))
                for m in ARROW.finditer(utext):
                    a, b = num(m.group(1)), num(m.group(2))
                    if a == 0:
                        continue
                    ratio, pct = b / a, (b / a - 1) * 100
                    # 화면 가격도 반올림된 값이라, 마지막 자리 반 단위만큼 오차를 허용한다
                    ha, hb = half_unit(m.group(1)), half_unit(m.group(2))
                    slack = ((b + hb) / max(a - ha, 1e-9) - (b - hb) / (a + ha)) * 50
                    for t in TIMES.finditer(utext):
                        dec = len(t.group(1).split('.')[1]) if '.' in t.group(1) else 0
                        if abs(num(t.group(1)) - ratio) > 0.5 * 10 ** -dec + 0.01 + slack / 100:
                            calc.append(f'p{pi} s{si} {t.group(0)} ≠ {m.group(0)} ({ratio:.2f}배)')
                    for t in PCT.finditer(utext):
                        v = num(t.group(1))
                        dec = len(t.group(1).split('.')[1]) if '.' in t.group(1) else 0
                        tol = 0.5 * 10 ** -dec + 0.1 + slack
                        if tol < abs(abs(v) - abs(pct)) < 50:
                            calc.append(f'p{pi} s{si} {t.group(0)} ≠ {m.group(0)} ({pct:+.1f}%)')
    ok_path = os.path.join(os.path.dirname(os.path.abspath(slides_path)), 'num_check.ok')
    if os.path.exists(ok_path):
        allowed = {l.split('|')[0].strip() for l in open(ok_path) if l.strip()}
        miss = [l for l in miss if f'MISS {l}' not in allowed]
        calc = [l for l in calc if f'CALC {l}' not in allowed]
    for line in miss:
        print('MISS', line)
    for line in calc:
        print('CALC', line)
    print(f'num_check: 숫자 {n}개, 리포트에 없음 {len(miss)}, 계산 불일치 {len(calc)}',
          'OK' if not (miss or calc) else 'FAIL')
    return 1 if (miss or calc) else 0


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
