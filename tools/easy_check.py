# 리포트가 비전문가도 읽히는지 발행 전에 본다(운영자 지시 2026-10-26: "리포트가 좀 어려운거 같아. 딥다이브는 좋은데. 설명을 앞으로는 비전문가도 알아먹게 좀 해줘").
# 사용: python3 easy_check.py <리포트.md> [--glossary <사이트 data/glossary.yaml>]
#  - 1~6부마다 '**쉽게 말하면**' 한 줄(그 부를 중학생도 알게 1~2문장)
#  - 본문 문장(표·제목·인용·출처 제외) 가운데 90자 넘는 문장 비율 10% 이하, 날짜를 뺀 숫자 4개 이상 든 문장 5% 이하
#  - 영어 약어(대문자 2자 이상)는 처음 나올 때 괄호 풀이나 용어 사전 항목이 있어야 한다(티커·단위 제외)
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
    if '**쉽게 말하면**' not in parts[i + 1][:1500]:
        bad.append(f'{parts[i]}부 첫머리에 **쉽게 말하면** 줄이 없음')
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
print('\n'.join(bad) if bad else f'EASY_OK 문장 {len(sents)} · 90자↑ {len(longs)} · 숫자 많은 문장 {len(dense)}')
sys.exit(1 if bad else 0)
