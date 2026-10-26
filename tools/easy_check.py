# 리포트가 비전문가도 읽히는지 발행 전에 본다(운영자 지시 2026-10-26: "리포트가 좀 어려운거 같아. 딥다이브는 좋은데. 설명을 앞으로는 비전문가도 알아먹게 좀 해줘").
# 사용: python3 easy_check.py <리포트.md> [--glossary <사이트 data/glossary.yaml>]
#  - 1~6부마다 '**쉽게 말하면**' 한 줄(그 부를 중학생도 알게 1~2문장)
#  - 본문 문장(표·제목·인용·출처 제외) 가운데 90자 넘는 문장 비율 10% 이하, 날짜를 뺀 숫자 4개 이상 든 문장 5% 이하
#  - 영어 약어(대문자 2자 이상)는 처음 나올 때 괄호 풀이나 용어 사전 항목이 있어야 한다(티커·단위 제외)
#  - 말로 쭉 이어 쓰기(운영자 지시 2026-10-26 "리포트가 너무 읽기 어려워 섹션이나 카드를 너무 쪼개지 말고 그냥 차라리 말로 쭉 친절하게 설명해", SKILL R1.6):
#    `###` 소제목 4개 이하, 사건 카드 머리(**YYYY.MM.DD · …**) 0개, 글머리 목록 줄 8개 이하, 표 3개 이하,
#    '이 리포트에서 확인할 수 있는 것'·'먼저 알아둘 용어' 절 없음, 한 문장짜리 문단 25% 이하. --legacy를 주면 이 검사를 건너뛴다(옛 리포트 고칠 때)
import sys, re, os
p = sys.argv[1]
gl = sys.argv[sys.argv.index('--glossary') + 1] if '--glossary' in sys.argv else '/home/user/kimworld-site/data/glossary.yaml'
txt = open(p, encoding='utf-8').read()
body = txt.split('\n---', 2)[-1] if txt.startswith('---') else txt
fm = txt[:len(txt) - len(body)]
ticker = (re.search(r'^ticker:\s*"?([A-Z0-9.]+)', fm, re.M) or [None, ''])[1]
terms = set(re.findall(r'term:\s*"([^"]+)"', open(gl, encoding='utf-8').read())) if os.path.exists(gl) else set()
bad = []
parts = re.split(r'^## (\d)부', body, flags=re.M)
for i in range(1, len(parts), 2):
    if '쉽게 말하면' not in parts[i + 1][:1500]:
        bad.append(f'{parts[i]}부 첫머리(1500자 안)에 쉽게 말하면 문장이 없음')
lines = [re.sub(r'\]\([^)]*\)|https?://\S+', ']', l) for l in body.split('\n') if l.strip() and not l.lstrip().startswith(('|', '#', '>', '!', '<'))]
sents = [s.strip() for l in lines for s in re.split(r'(?<=[.?!다])\s+(?=\S)', re.sub(r'^\s*[-*\d.□]+\s*', '', l)) if len(s.strip()) > 5]
longs = [s for s in sents if len(s) > 90]
DATE = r'\d{4}년|\d{1,2}월|\d{1,2}일|\d{4}\.\d{1,2}\.\d{1,2}|\d{1,2}\.\d{1,2}(?=[ ·~)])|[1-6]부|\d\.\d(?=\s)|P\d+'
dense = [s for s in sents if len(re.findall(r'\d[\d,.]*', re.sub(DATE, '', s))) >= 4]
if sents and len(longs) / len(sents) > 0.10: bad.append(f'90자 넘는 문장 {len(longs)}/{len(sents)}({len(longs)/len(sents):.0%}) > 10% · 예: {longs[0][:60]}…')
if sents and len(dense) / len(sents) > 0.05: bad.append(f'숫자 4개 이상 문장 {len(dense)}/{len(sents)}({len(dense)/len(sents):.0%}) > 5% · 예: {dense[0][:60]}…')
skip = {ticker, 'ET', 'USD', 'ETF', 'AI', 'SEC', 'IR', 'CEO', 'CFO', 'PNG', 'URL', 'UTC', 'KST', 'TVA'}
seen = set()
for m in re.finditer(r'(?<![A-Za-z])([A-Z][A-Z0-9]{1,6})(?![A-Za-z])', '\n'.join(lines)):
    a = m.group(1)
    if a in seen or a in skip or a.isdigit(): continue
    seen.add(a)
    after = '\n'.join(lines)[m.end():m.end() + 3]
    before = '\n'.join(lines)[max(0, m.start() - 2):m.start()]
    if re.fullmatch(r'P\d+', a) or any(x.startswith(a) for x in terms) or after.startswith('(') or before.endswith('('): continue
    bad.append(f"약어 '{a}' 첫 등장에 풀이 없음(괄호 풀이 또는 용어 사전)")
if '--legacy' not in sys.argv:
    h3 = re.findall(r'^### ', body, re.M); cards = re.findall(r'^\*\*\d{4}\.\d{2}\.\d{2}[^*\n]*·', body, re.M)
    bullets = [l for l in body.split('\n') if re.match(r'\s*([-*]|\d+\.)\s', l)]
    tables = re.findall(r'(?:^\|.*\n)+', body, re.M)
    paras = [x.strip() for x in body.split('\n\n') if x.strip() and not x.lstrip().startswith(('|', '#', '>', '!', '-', '*', '<')) and not re.match(r'\d+\.\s', x.strip())]
    one = [x for x in paras if len(re.findall(r'[.?!다요]\s', x + ' ')) <= 1]
    if len(h3) > 4: bad.append(f'R1.6 ### 소제목 {len(h3)}개 > 4(쪼개지 말고 문단으로 이어 쓰기)')
    if cards: bad.append(f'R1.6 사건 카드 머리 {len(cards)}개(카드 대신 시간순 문단)')
    if len(bullets) > 8: bad.append(f'R1.6 글머리 목록 {len(bullets)}줄 > 8(체크리스트 외에는 문장으로)')
    if len(tables) > 3: bad.append(f'R1.6 표 {len(tables)}개 > 3')
    for sec in ('## 이 리포트에서 확인할 수 있는 것', '## 먼저 알아둘 용어'):
        if sec in body: bad.append(f"R1.6 '{sec[3:]}' 절은 빼기(용어는 처음 쓰는 문장 안에서 풀기)")
    if paras and len(one) / len(paras) > 0.25: bad.append(f'R1.6 한 문장짜리 문단 {len(one)}/{len(paras)} > 25%(2~4문장으로 이어 쓰기)')
print('\n'.join(bad) if bad else f'EASY_OK 문장 {len(sents)} · 90자↑ {len(longs)} · 숫자 많은 문장 {len(dense)}')
sys.exit(1 if bad else 0)
