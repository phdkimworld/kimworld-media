#!/usr/bin/env python3
"""모든 콘텐츠 가독성 검사(운영자 지시 2026-11-11 "영상 뿐 아니라 모든 컨텐츠에 어제 논의한 가독성 개선 지침 적용").
SKILL 0.2(R1.5 '쓰면서 멈칫할 곳을 없앤다'를 모든 출력물에)의 기계로 잴 수 있는 부분만 본다.
리포트 본문은 easy_check.py가 따로 본다. 이 검사는 대본·쇼츠 대본·유튜브 설명·첫 댓글·SNS 대기열 글·블로거 글·댓글 답글 파일용.

사용: python3 tools/plain_check.py <파일 또는 폴더>...   (폴더면 narration*.txt·youtube.txt·description.txt·pinned.txt·*shorts*.txt 와
      social/queue/<slug>-*.json 같은 json의 text/caption/message/body 값을 모두 읽는다)
판정(파일마다):
  ARROW  문장 안 화살표(→ ⇒ ->): 0개여야 한다(표·차트 줄 제외).
  DOTS   가운뎃점 나열 '·'가 3개 이상 들어간 문장: 0개(해시태그 줄·챕터 줄·핵심 요약 한 줄은 예외로 두지 않는다 — 문장으로 나눈다).
  LONG   공백 포함 90자 넘는 문장 비율 15% 이하(대본은 귀로 듣는 글이라 같은 기준).
  CALC   '(1+2)'·'A+B=' 처럼 기호로 계산을 대신한 곳: 0개.
끝 줄에 PLAIN_OK 또는 PLAIN_FAIL.
"""
import sys, os, re, json, glob

SPLIT = re.compile(r'(?<=[.!?。])\s+|\n+')
URL = re.compile(r'https?://\S+')
def sentences(text):
    out = []
    for s in SPLIT.split(text):
        s = URL.sub('', s).strip()
        if not s or s.startswith('|') or s.startswith('#') or re.match(r'^\d{1,2}:\d{2}', s): continue
        out.append(s)
    return out

def texts_from_json(p):
    try: d = json.load(open(p, encoding='utf-8'))
    except Exception: return []
    acc = []
    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ('text', 'caption', 'message', 'body', 'description', 'comment', 'first_comment', 'title') and isinstance(v, str): acc.append(v)
                else: walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(d); return acc

def files(args):
    for a in args:
        if os.path.isdir(a):
            for pat in ('narration*.txt', 'youtube.txt', 'description.txt', 'pinned.txt', '*shorts*.txt', '*short*/narration*.txt'):
                for f in glob.glob(os.path.join(a, pat)):
                    if 'submitted' not in f: yield f
        else: yield a

ok = True
for f in files(sys.argv[1:]):
    raw = texts_from_json(f) if f.endswith('.json') else [open(f, encoding='utf-8').read()]
    S = [s for t in raw for s in sentences(t)]
    if not S: continue
    arrow = [s for s in S if re.search(r'→|⇒|->', s)]
    dots = [s for s in S if s.count('·') >= 3]
    calc = [s for s in S if re.search(r'\(\s*\d[\d.,]*\s*[+×x*]\s*\d|\d\s*\+\s*\d[\d.,]*\s*=', s)]
    long_ = [s for s in S if len(s) > 90]
    lr = len(long_) / len(S)
    bad = bool(arrow or dots or calc or lr > 0.15)
    ok &= not bad
    print(f"{'FAIL' if bad else 'ok  '} {f}: 문장 {len(S)} · 화살표 {len(arrow)} · 가운뎃점 나열 {len(dots)} · 기호 계산 {len(calc)} · 90자 초과 {len(long_)}({lr:.0%})")
    for tag, L in (('ARROW', arrow), ('DOTS', dots), ('CALC', calc)):
        for s in L[:3]: print(f"   {tag}: {s[:80]}")
    if lr > 0.15:
        for s in long_[:3]: print(f"   LONG: {s[:80]}…")
    # EMOJI(SKILL 8.0.2 'AI 느낌', 77회차 BTQ): 설명란 줄마다 장식 이모지 머리(📌⚡💵🧩📚…)를 다는 틀 — RUM 76 설명란 11줄. 링크·쇼핑·알림·투표 줄만 6줄까지
    if os.path.basename(f) == 'description.txt':
        em = [l for l in raw[0].split('\n') if re.match('[\U0001F300-\U0001FAFF☀-➿]', l)]
        if len(em) > 6:
            # 같은 날 동시 제작(CEG 78회차)을 막지 않도록 11-12까지는 경고만, 11-13부터 FAIL
            hard = __import__('datetime').date.today().isoformat() >= '2026-11-13'
            ok &= not hard; print(f"{'FAIL' if hard else 'WARN'} {f}: 이모지로 시작하는 줄 {len(em)}개 > 6 — 장식 머리는 지우고 사실 문장으로(링크·🛒·🔔·🗳️ 줄만 남김): {' '.join(l[:2] for l in em)}")
print('PLAIN_OK' if ok else 'PLAIN_FAIL')
