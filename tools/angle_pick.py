#!/usr/bin/env python3
"""매매 질문 고르기·기록·제목 검사(운영자 2026-11-22 "지금 사도 될까 지금 팔아야 될까 등 직접적으로 와닿는 매매질문을
생각할 수 있는 거 다 정리해서 다양하게 던지도록 해줘").

질문 목록은 skill/runbooks/angles.md 표 하나에서만 읽는다(코드·계열·키·질문·제목 틀·썸네일 큰 글자). 사용 기록은 review/angle_log.md.

사용:
  python3 tools/angle_pick.py <티커> [--event 급락,최저] [--work <작업 폴더>] [--name "블룸 에너지"] [--date 2026-11-23] [-n 3]
        → 후보 3개: 코드 · 질문 · 제목 틀(종목 채움) · 썸네일 큰 글자 · 고른 이유
  python3 tools/angle_pick.py --add <코드> --slug <slug> --title "<유튜브 제목>" [--date YYYY-MM-DD]   → angle_log.md에 한 줄
  python3 tools/angle_pick.py --check "<제목>"   → ANGLE_TITLE_OK | ANGLE_TITLE_FAIL (금지 변형·꺾쇠는 FAIL, 앞 25자 질문은 WARN)
  python3 tools/angle_pick.py --list             → 코드 목록
회전 규칙: 직전 회차와 같은 코드 금지(-100) · 직전 5회에 쓴 코드 감점(-6) · 같은 종목 직전 회차와 같은 코드 금지(-100)·같은 계열 감점(-3)
          · 사건 일치 +4(명시·감지) / +2(날짜로 약하게) · '기본' +1 · 한 번도 안 쓴 코드 +0.5.
import: from angle_pick import title_check; title_check(제목) → (fails, warns)
"""
import datetime as dt
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANG = os.path.join(HERE, 'skill', 'runbooks', 'angles.md')
LOG = os.environ.get('ANGLE_LOG') or os.path.join(HERE, 'review', 'angle_log.md')  # ANGLE_LOG: 시험용 사본
LEDGER = os.path.join(HERE, 'review', 'predictions', 'ledger.jsonl')
SITE = os.environ.get('SITE_DIR', '/home/user/kimworld-site')
EVENTS = ('급락 급등 최저 최고 연속하락 반등 내부자매수 내부자매도 증자 실적전 실적후 공매도 상폐경고 병합 계약 편입 편출 '
          '시장동반 무리 세금매도 연말 FOMC 판정일 해제').split()
# 연준 공식 일정(2026, federalreserve.gov fomccalendars — 결정 발표일). research/macro.md가 있으면 그쪽이 우선
FOMC_2026 = ['2026-01-28', '2026-03-18', '2026-04-29', '2026-06-17', '2026-07-29', '2026-09-16', '2026-10-28', '2026-12-09']

# 금지 변형(SKILL 5장·marketing.md·angles.md 1장): 질문형은 되고 단정·권유·약속·긴급·운영자 보유는 안 된다
BANNED = [
    (r'(사|파|담으|매수하|매도하|손절하|익절하|물타기\s?하)세요', '권유형(~하세요)'),
    (r'(?<![가-힣])(사라|팔아라|사야\s?한다|팔아야\s?한다|사야\s?합니다|팔아야\s?합니다)(?![가-힣])', '단정형(사라·팔아라·~해야 한다)'),
    (r'무조건|확실(한|히)|틀림없|100\s?%\s?(오|상승|수익)', '단정어(무조건·확실)'),
    (r'마지막\s?기회|지금\s?안\s?사면|지금\s?사지\s?않으면|놓치면\s?후회|오늘만|선착순|마감\s?임박|늦기 전에', '긴급성 압박'),
    (r'목표\s?(주가|가)(?!.*인용)|\d+(\.\d+)?\s?달러\s?(간다|갑니다|돌파한다)|(두|세|열)\s?배\s?(간다|갑니다|오른다)|텐배거', '목표가·가격 단정'),
    (r'수익\s?(보장|약속|확정)|원금\s?(보장|회복\s?보장)|손실\s?없', '수익 약속'),
    (r'제가\s?(산|가진|보유|들고)|저도\s?(샀|물렸|들고|보유)|제\s?계좌|내\s?계좌|저는\s?(샀|팔았|보유)', '운영자 보유 여부'),
    (r'(AI|인공지능)(가|이|로|에게)\s?(분석|골라|고른|추천|만든|뽑은|예측)|챗GPT|클로드', 'AI 활용 언급(R1.3.1 — 업종·회사 이름의 AI는 된다)'),
    (r'회원\s?가입|가입하(세요|면)|베팅|배팅', '회원 가입·베팅'),
]


def title_check(t):
    """제목 한 줄 검사 → (fails, warns). 질문형 매매 제목이든 미스터리형이든 금지 변형만 FAIL."""
    t = str(t or '')
    fails, warns = [], []
    for pat, why in BANNED:
        m = re.search(pat, t)
        if m: fails.append(f"{why}: '{m.group(0)}'")
    if re.search('[「」『』<>]', t): fails.append('꺾쇠·부등호(「」『』<>) — 유튜브 400·V4')
    if re.search(r'[$\\]', t): fails.append("'$'·'\\' 기호(V4 8)")
    i = t.replace('？', '?').find('?')
    if 0 <= i and t.count('?') > 1: warns.append(f"'?' {t.count('?')}개 — 질문은 하나")
    if 0 <= i > 25 and i <= 60: warns.append(f"첫 '?'가 {i + 1}자째 — 종목명+질문은 앞 25자 안(사건 머리말은 뒤로)")
    if len(t) > 100: fails.append(f'{len(t)}자 > 100(유튜브 상한)')
    elif len(t) > 80: warns.append(f'{len(t)}자 > 80(V4 1)')
    return fails, warns


def load_angles():
    rows = []
    for line in open(ANG, encoding='utf-8'):
        if not re.match(r'^\| [NHECT]\d+ \|', line): continue
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) < 10: continue
        rows.append({'code': c[0], 'fam': c[1], 'keys': [k.strip() for k in c[2].split('·')], 'q': c[3], 'tpl': c[4],
                     'when': c[5], 'shorts': c[8] if len(c) > 8 else '', 'thumb': c[9] if len(c) > 9 else ''})
    return rows


def load_log():
    out = []
    if not os.path.exists(LOG): return out
    for line in open(LOG, encoding='utf-8'):
        m = re.match(r'^\| (\d{4}-\d\d-\d\d) \| ([^|]+)\| ([NHECT]\d+) \| (.*)\|\s*$', line)
        if m: out.append({'date': m.group(1), 'slug': m.group(2).strip(), 'code': m.group(3), 'title': m.group(4).strip()})
    return out


def site_name(tk):
    """사이트 최신 리포트 title에서 한글 이름('블룸 에너지 지금 사도 될까? — …' → 블룸 에너지)."""
    best = None
    for f in glob.glob(os.path.join(SITE, 'content', 'reports', f'{tk.lower()}-*.md')):
        txt = open(f, encoding='utf-8').read(3000)
        d = (re.search(r'^date:\s*"?(\d{4}-\d\d-\d\d)', txt, re.M) or [None, ''])[1]
        ti = (re.search(r'^title:\s*"?(.+?)"?\s*$', txt, re.M) or [None, ''])[1]
        if ti and (best is None or d > best[0]): best = (d, ti)
    if not best: return None
    nm = re.split(r'\s+지금|,|\s+—|\?|\s+미스터리|\(', best[1])[0].strip()
    return nm if 0 < len(nm) <= 16 else None


def detect(work):
    """작업 폴더 글에서 사건 낱말 찾기 → {사건: 근거 조각}"""
    txt = ''
    for pat in ('*.md', '*.txt', '*.json', '*/*.md', '*/*.txt'):
        for f in glob.glob(os.path.join(work, pat)):
            try: txt += '\n' + '\n'.join(l for l in open(f, encoding='utf-8').read()[:200000].split('\n') if not re.search(r'https?://|^\s*-?\s*(url|source|title|date|name):', l))
            except (OSError, UnicodeDecodeError): pass
    found = {}

    def hit(ev, pat, cond=None):
        for m in re.finditer(pat, txt):
            if cond is None or cond(m):
                found.setdefault(ev, txt[max(0, m.start() - 15):m.end() + 15].replace('\n', ' ').strip()); return
    num = lambda m: float(m.group(1).replace(',', ''))
    hit('급락', r'하루\s*-(\d+(?:\.\d+)?)%', lambda m: num(m) >= 10)
    hit('급락', r'급락')
    hit('급등', r'하루\s*\+(\d+(?:\.\d+)?)%', lambda m: num(m) >= 15)
    hit('최저', r'(1년|52주|상장 (뒤|이후)|사상) 최저(?! ?대비)')
    hit('최고', r'(1년|52주|사상) 최고')
    hit('연속하락', r'(\d+)\s*거래일 연속 (하락|내림)', lambda m: num(m) >= 5)
    hit('내부자매수', r'(장내 매수|Form 4[^\n]{0,40}매수|이사가[^\n]{0,20}샀)')
    hit('내부자매도', r'(장내 매도|세금 매도|Form 4[^\n]{0,40}매도|임원[^\n]{0,20}팔)')
    hit('증자', r'(424B\d?|유상증자|새 주식|ATM|전환사채|공모가)')
    hit('실적후', r'실적 (발표 )?(뒤|다음 날|이후)')
    hit('실적전', r'(다음|예정된?) 실적[^\n]{0,20}(\d{1,2}월 \d{1,2}일|\d{1,2}/\d{1,2})')
    hit('공매도', r'공매도 보고서')
    hit('상폐경고', r'(최저 입찰가|상장 유지|1달러 선|상장폐지)')
    hit('병합', r'(주식|액면) 병합')
    hit('계약', r'(\d[\d,.]*\s*억 달러[^\n]{0,15}(계약|수주)|(계약|수주)[^\n]{0,15}\d[\d,.]*\s*억 달러)')
    hit('편입', r'(지수|S&P ?500|러셀|나스닥 ?100)[^\n]{0,10}편입')
    hit('편출', r'편출|지수에서 (빠|제외)')
    hit('시장동반', r'(회사 (공시|소식) 0건|시장(과|을)? (함께|따라)|시장 동반)')
    hit('무리', r'(같은 업종 \d+종목|업종 \d+종목|\d+종목이 함께)')
    hit('해제', r'보호예수|락업|lock-?up')
    return found


def date_events(tk, d, work):
    ev = {}
    if (d.month == 11 and d.day >= 15) or d.month == 12: ev['세금매도'] = f'{d:%m-%d} 연말 세금 매도 기간(11-15~12-31)'
    if d.month == 12: ev['연말'] = '12월'
    fom = []
    mac = os.path.join(work, 'research', 'macro.md') if work else ''
    if mac and os.path.exists(mac):
        fom = re.findall(r'(\d{4}-\d\d-\d\d)[^\n]{0,30}FOMC', open(mac, encoding='utf-8').read())
    fom = fom or FOMC_2026
    for f in sorted(fom):
        gap = (dt.date.fromisoformat(f) - d).days
        if 0 <= gap <= 10: ev['FOMC'] = f'다음 FOMC {f}({gap}일 뒤)'; break
    if os.path.exists(LEDGER):
        for line in open(LEDGER, encoding='utf-8'):
            try: r = json.loads(line)
            except ValueError: continue
            jd = r.get('judge_date')
            if r.get('ticker') == tk and jd and not r.get('status') and 0 <= (dt.date.fromisoformat(jd[:10]) - d).days <= 30:
                ev['판정일'] = f"예측 장부 판정일 {jd[:10]}"; break
    return ev


def josa(text, nm):
    """'{종목}이 '·'{종목}을 ' 같은 틀의 조사를 이름 받침에 맞춘다(블룸 에너지가·블룸 에너지를)."""
    last = nm.rstrip(')').split('(')[0].strip()[-1:] if nm else ''
    has = bool(last) and '가' <= last <= '힣' and (ord(last) - 0xAC00) % 28 != 0
    for a, b in (('이', '가'), ('을', '를'), ('은', '는'), ('과', '와')):
        text = re.sub(r'\{종목\}[%s%s](?=[\s,.])' % (a, b), '{종목}' + (a if has else b), text)
    return text.replace('{종목}', nm)


def pick(tk, events, work, name, d, n):
    A = load_angles(); L = load_log()
    fam = {a['code']: a['fam'] for a in A}
    recent = [x['code'] for x in L[-5:]]
    last = L[-1]['code'] if L else None
    same = [x for x in L if x['slug'].split('-')[0].lower() == tk.lower()]
    prev_same = same[-1]['code'] if same else None
    used = {x['code'] for x in L}
    strong = {e: '지정' for e in events}
    if work: strong.update({k: v for k, v in detect(work).items() if k not in strong})
    weak = {k: v for k, v in date_events(tk, d, work).items() if k not in strong}
    scored = []
    for a in A:
        s, why = 0.0, []
        ws = []
        for k in a['keys']:
            if k in strong: ws.append(4 if k in events else 2.5); why.append(f"사건 {k}{'' if k in events else '(감지)'}")
            elif k in weak: ws.append(1.5); why.append(f'시기 {k}')
        ws.sort(reverse=True)
        if ws: s += ws[0] + 0.4 * sum(ws[1:3])  # 키가 많은 넓은 질문이 늘 이기지 않게: 가장 맞는 사건 하나 + 나머지 조금
        if a['code'][0] == 'E' and any(k in strong for k in a['keys']): s += 1.5; why.append('사건 질문 우선')
        if '기본' in a['keys']: s += 1
        if a['code'] == last: s -= 100; why.append('직전 회차와 같음(금지)')
        elif a['code'] in recent: s -= 6; why.append(f'직전 5회 중 {recent.count(a["code"])}번')
        if prev_same:
            if a['code'] == prev_same: s -= 100; why.append(f'{tk} 직전 회차와 같음(금지)')
            elif fam.get(prev_same) == a['fam']: s -= 3; why.append(f'{tk} 직전과 같은 계열({a["fam"]})')
        if a['code'] not in used: s += 0.5
        scored.append((s, a, why))
    scored.sort(key=lambda x: -x[0])
    nm = name or site_name(tk) or tk
    stock = f'{nm}({tk})' if nm != tk else tk
    print(f'# {tk} 매매 질문 후보 ({d}) — 종목 표기 {stock}')
    print(f"사건(지정·감지): {', '.join(f'{k}({v[:40]})' for k, v in strong.items()) or '없음'}")
    print(f"시기(약하게): {', '.join(f'{k}({v})' for k, v in weak.items()) or '없음'}")
    print(f"직전 5회: {' '.join(recent) or '-'} · {tk} 직전: {prev_same or '없음'}")
    for i, (s, a, why) in enumerate(scored[:n], 1):
        title = josa(a['tpl'], stock)
        print(f"{i}. {a['code']} [{a['fam']}] {a['q']} (점수 {s:g})\n   제목 틀: {title}\n   썸네일: {a['thumb']} · 쇼츠 첫 문장: {josa(a['shorts'], nm)}"
              f"\n   쓰는 조건: {a['when']}\n   이유: {', '.join(why) or '사건 없음 — 기본형'}")
    return scored[:n]


def add(code, slug, title, d):
    codes = {a['code'] for a in load_angles()}
    if code not in codes: sys.exit(f'모르는 코드 {code} — angles.md 목록에 없음')
    L = load_log()
    if L and L[-1]['code'] == code: print(f'WARN 직전 회차({L[-1]["slug"]})와 같은 코드 {code} — 회전 규칙 위반', file=sys.stderr)
    f, w = title_check(title)
    for x in f + w: print(('FAIL ' if x in f else 'WARN ') + x, file=sys.stderr)
    if f: sys.exit('ANGLE_TITLE_FAIL — 기록하지 않음')
    with open(LOG, 'a', encoding='utf-8') as fh: fh.write(f'| {d} | {slug} | {code} | {title.replace("|", "·")} |\n')
    print(f'ADDED {d} {slug} {code}')


def arg(k, default=None):
    return sys.argv[sys.argv.index(k) + 1] if k in sys.argv else default


if __name__ == '__main__':
    a = sys.argv[1:]
    d = dt.date.fromisoformat(arg('--date', dt.date.today().isoformat()))
    if not a or a[0] in ('-h', '--help'): print(__doc__); sys.exit(0)
    if '--list' in a:
        for x in load_angles(): print(f"{x['code']:4} [{x['fam']}] {x['q']} — 키 {'·'.join(x['keys'])}")
        sys.exit(0)
    if '--check' in a:
        f, w = title_check(arg('--check'))
        for x in f: print('FAIL', x)
        for x in w: print('WARN', x)
        print('ANGLE_TITLE_FAIL' if f else 'ANGLE_TITLE_OK'); sys.exit(1 if f else 0)
    if '--add' in a:
        if not (arg('--slug') and arg('--title')): sys.exit('--add <코드> --slug <slug> --title "<제목>"')
        add(arg('--add'), arg('--slug'), arg('--title'), d.isoformat()); sys.exit(0)
    tk = a[0].upper()
    ev = [e.strip() for e in (arg('--event') or '').replace(' ', ',').split(',') if e.strip()]
    bad = [e for e in ev if e not in EVENTS]
    if bad: sys.exit(f"모르는 사건 {bad} — 쓸 수 있는 것: {' '.join(EVENTS)}")
    pick(tk, ev, arg('--work'), arg('--name'), d, int(arg('-n', 3)))
