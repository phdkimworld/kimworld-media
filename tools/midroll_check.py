#!/usr/bin/env python3
"""영양제 중간광고 문단 검사(health_midroll.md 3·5·8절). 녹음 전에 돈다(pre_tts_check.sh).
112회차(INOD) 도입: 111회차 SMR에서 광고가 5문장 37초로 길었고, 식약처 문구를 quote 슬라이드에 올려
quote 틀의 '?' 표시가 문구 옆에 붙었다. 이 두 가지와 health.yaml banned·drop_words를 기계로 막는다.
사용: python3 tools/midroll_check.py <video 폴더>   → MIDROLL_OK | MIDROLL_FAIL … | MIDROLL_SKIP(광고 문단 없음)
- 광고 문단 = slides.json에서 'shop'이 있고 대본에 '유료 광고'가 든 문단
- 문장 3개 이하, 그 문단 슬라이드에 layout 'quote' 없음(물음표 표시), 위치 50~65%(문단 번호 기준 대략값, 실제 초는 합성 뒤)
- narration·description·pinned에 health.yaml banned·drop_words 0건, 광고 문단에 논문 용어 직역('묶음'·'코호트'·'메타분석에서'·'WMD') 0건(주식 쪽 '1년 최저 묶음'은 허용)
"""
import json, os, re, sys
V = sys.argv[1]
H = '/home/user/kimworld-site/health/health.yaml'
paras = [p for p in open(os.path.join(V, 'narration.txt'), encoding='utf-8').read().split('\n\n') if p.strip()]
deck = json.load(open(os.path.join(V, 'slides.json'), encoding='utf-8'))
idx = [i for i, p in enumerate(deck['paras']) if p.get('shop') and i < len(paras) and '유료 광고' in paras[i]]
if not idx: print('MIDROLL_SKIP 광고 문단 없음'); sys.exit(0)
i = idx[0]; bad = []
sents = [s for s in re.split(r'(?<=[.?!])\s+', paras[i].strip()) if s]
if len(sents) > 3: bad.append(f'문장 {len(sents)}개 > 3(세 문장 이내, 20~30초)')
q = [s.get('from') for s in deck['paras'][i]['slides'] if s.get('layout') == 'quote']
if q: bad.append(f"광고 문단에 quote 슬라이드(물음표 표시) {len(q)}장 — 문구는 아이콘 없는 카드(stat·shop 이미지)로")
pos = i / max(1, len(paras) - 1)
if not 0.45 <= pos <= 0.70: bad.append(f'문단 위치 {pos:.0%}(50~65% 지점 근처)')
words = []
try:
    import yaml
    h = yaml.safe_load(open(H, encoding='utf-8')); words = list(set(h.get('banned', [])) | set(h.get('drop_words', [])))
except Exception as e:
    bad.append(f'health.yaml 읽기 실패: {e}')
lit = [w for w in ('묶음', '코호트', '메타분석에서', 'WMD') if w in paras[i]]
if lit: bad.append(f'광고 문단 논문 용어 직역 {lit}(8절: "~드신 분들은", "연구 N개를 모아 보니")')
for f in ('narration.txt', 'description.txt', 'pinned.txt'):
    p = os.path.join(V, f)
    if not os.path.exists(p): continue
    t = open(p, encoding='utf-8').read()
    hit = [w for w in words if w in t]
    if hit: bad.append(f'{f}: 금지 낱말 {hit}')
if bad: print('MIDROLL_FAIL p%d · ' % (i + 1) + ' · '.join(bad)); sys.exit(1)
print(f'MIDROLL_OK p{i+1} 문장 {len(sents)} · quote 0 · 위치 약 {pos:.0%} · 금지 낱말 0')
