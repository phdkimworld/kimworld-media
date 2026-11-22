#!/usr/bin/env python3
"""영양제 중간광고 문단 검사(health_midroll.md 3·5·8절). 녹음 전에 돈다(pre_tts_check.sh).
112회차(INOD) 도입: 111회차 SMR에서 광고가 5문장 37초로 길었고, 식약처 문구를 quote 슬라이드에 올려
quote 틀의 '?' 표시가 문구 옆에 붙었다. 이 두 가지와 health.yaml banned·drop_words를 기계로 막는다.
사용: python3 tools/midroll_check.py <video 폴더>   → MIDROLL_OK | MIDROLL_FAIL … | MIDROLL_SKIP(광고 문단 없음)
- 광고 문단 = slides.json에서 'shop'이 있고 대본에 '유료 광고'가 든 문단
- 문장 3개 이하, 그 문단 슬라이드에 layout 'quote' 없음(물음표 표시), 위치 50~65%(문단 번호 기준 대략값, 실제 초는 합성 뒤)
- narration·description·pinned에 health.yaml banned·drop_words 0건, 광고 문단에 논문 용어 직역('묶음'·'코호트'·'메타분석에서'·'WMD') 0건(주식 쪽 '1년 최저 묶음'은 허용)
- 11-22(marketing.md 6절): 문장 상한 4(health_midroll 9절 2번). 광고 문단·마무리 안내 문단('고르는 법'·'설명란 둘째 줄')·설명란/고정댓글의 💊·건강몰 줄에
  거짓 긴급성 낱말과 지어낸 후기 표지 0건(주식 문단은 보지 않음 — 오탐 방지)
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
if len(sents) > 4: bad.append(f'문장 {len(sents)}개 > 4(넷 이내, 30초 이내 — 9절 2번)')
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
URG = r'오늘만|오늘까지만?|마감 ?임박|품절 ?임박|품절 ?전|한정 ?수량|수량 ?한정|지금 안 사면|지금 사지 않으면|놓치면 후회|마지막 기회|선착순|곧 가격이 오릅|재고가? 얼마 (안|없)'
FAKE = r'(제가|직접|저도) 먹어 ?보니|먹어 ?봤더니|저도 (매일 )?먹고 있|구매자\s*\S*\s*\d+\s*%|구매자 ○+%|재구매율|만족도\s*\d+\s*%|별점|\d[\d,]*\s*명이 (샀|구매|선택)'
zone = [(f'narration p{i+1}', paras[i])] + [(f'narration p{j+1}', p) for j, p in enumerate(paras) if j != i and ('고르는 법' in p or '설명란 둘째 줄' in p)]
for f in ('description.txt', 'pinned.txt'):
    p = os.path.join(V, f)
    if os.path.exists(p):
        zone += [(f, l) for l in open(p, encoding='utf-8').read().splitlines() if '💊' in l or 'health.drkimworld.com' in l]
for name, txt in zone:
    u = sorted({m.group(0) for m in re.finditer(URG, txt)}); k = sorted({m.group(0) for m in re.finditer(FAKE, txt)})
    if u: bad.append(f'{name}: 거짓 긴급성 {u}(marketing.md 1절 — 재고·마감은 우리가 확인할 수 없음)')
    if k: bad.append(f'{name}: 지어낸 후기 표지 {k}(직접 섭취·실측 확인 전 금지, HEALTH_CHANNEL 2장)')
if bad: print('MIDROLL_FAIL p%d · ' % (i + 1) + ' · '.join(bad)); sys.exit(1)
print(f'MIDROLL_OK p{i+1} 문장 {len(sents)} · quote 0 · 위치 약 {pos:.0%} · 금지 낱말 0 · 긴급성·후기 표지 0(검사 {len(zone)}곳)')
