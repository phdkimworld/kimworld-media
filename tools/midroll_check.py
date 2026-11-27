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
- 11-26 AD2(health_midroll 10절): 회차 data_as_of 11-26~ — kind "ad", '제품 링크는 설명란', 💊 줄 쿠팡 직접 링크·구분선·광고·파트너스 문장. 옵션 --date YYYY-MM-DD, --compat(옛 규칙만)
- 11-27 AD3(health_midroll 10.6, RZLV 전환 분석 반영): 회차 data_as_of 11-28~ — ① 광고 문단 슬라이드에 '근거 질' 문구 없음(근거 질 메모는 리포트·건강 가이드)
  ② product 카드 'why'는 health.yaml 기능성 문구 그대로 ③ 하루 값(원) 주장은 '기준일'과 함께만 ④ 대본 행동 문장·마무리 한 문장에 '고정댓글 둘째 줄'
  ⑤ 마무리 한 문장은 정리·투표 문단보다 앞, 같은 문단의 교육용 고지 문장보다 앞 ⑥ 고정댓글·설명란: 리포트 링크 줄 바로 다음 구역이 💊 구역(빈 줄·구분선만 사이에)
"""
import json, os, re, sys
V = sys.argv[1]
H = '/home/user/kimworld-site/health/health.yaml'
paras = [p for p in open(os.path.join(V, 'narration.txt'), encoding='utf-8').read().split('\n\n') if p.strip()]
deck = json.load(open(os.path.join(V, 'slides.json'), encoding='utf-8'))
idx = [i for i, p in enumerate(deck['paras']) if (p.get('shop') or p.get('kind') == 'ad') and i < len(paras) and '유료 광고' in paras[i]]
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
# 11-24 운영자 철학 "수요와 공급을 연결"(health_midroll.md 0절): 광고 문단에 ① 누구(조건·상황 호명) ② 제품 조건(성분·함량·뒷면 숫자)
WHO = r'분이라면|분들은|분들이|분이시라면|하시는 분|드시는 분|보시는 분|분께|이라면|이시라면|신 분'
SUP = r'mg|밀리그램|그램|함량|뒷면|성분|균주|균|EPA|DHA|이피에이|디에이치에이|루테인|지아잔틴|오메가|유산균|하루 \S+'
if not re.search(WHO, paras[i]): bad.append('수요(누구) 없음 — "~하시는 분이라면"처럼 조건·상황으로 부를 것(health_midroll 0절)')
if not re.search(SUP, paras[i]): bad.append('공급(제품 조건) 없음 — 성분·하루 함량·뒷면 숫자 중 하나(health_midroll 0절)')
for f in ('description.txt', 'pinned.txt'):
    pp = os.path.join(V, f)
    if os.path.exists(pp):
        for l in open(pp, encoding='utf-8').read().splitlines():
            if '💊' in l and not re.search(WHO + r'|날이 많다면|많으시다면', l): bad.append(f'{f}: 💊 줄에 "누구"(조건·상황) 없음 — "<누구>이라면 — <성분>은 <뒷면 숫자> 하나만"(marketing 3절)')
# AD2(2026-11-26 운영자 "광고는 시각적으로나 호흡으로나 딱 구분되는게 더 이목을 끌거 같아. 링크는 이제 몰이 아니라 제품 링크를 바로 달기로 했어." — health_midroll 10절)
#   회차 날짜(리포트 data_as_of, 없으면 --date/MIDROLL_DATE) 11-26~만. 옛 회차는 그대로(--compat이면 날짜와 상관없이 옛 규칙만)
#   ① slides.json 광고 문단 "kind": "ad"(slidekit 광고 화면·앞뒤 무음) ② 대본 광고 문단에 '제품 링크는 설명란'(4칸 ④ 행동)
#   ③ 설명란·고정댓글·쇼츠 설명란 💊 줄: 쿠팡 제품 직접 링크(link.coupang.com), 건강몰 가이드 링크 금지, '광고' 표시, 구분선 줄 + 빈 줄로 뗀 자기 구역,
#      리포트·텔레그램 링크와 다른 구역 ④ 글 전체에 쿠팡 파트너스 문장 ⑤ 누구(조건·상황)는 위 검사 그대로
AD2_FROM = '2026-11-26'
def ep_date():
    for k, a in enumerate(sys.argv):
        if a == '--date' and k + 1 < len(sys.argv): return sys.argv[k + 1]
    if os.environ.get('MIDROLL_DATE'): return os.environ['MIDROLL_DATE']
    try:
        slug = re.search(r'drkimworld\.com/r/([a-z0-9\-]+)/', open(os.path.join(V, 'description.txt'), encoding='utf-8').read()).group(1)
        site = os.environ.get('KW_SITE', '/home/user/kimworld-site')
        fm = open(os.path.join(site, 'content', 'reports', slug + '.md'), encoding='utf-8').read(3000)
        return re.search(r'^data_as_of:\s*["\']?(\d{4}-\d\d-\d\d)', fm, re.M).group(1)
    except Exception:  # 리포트가 아직 사이트에 없으면(녹음 전) 대본 파일 날짜
        import datetime as _dt
        return _dt.datetime.fromtimestamp(os.path.getmtime(os.path.join(V, 'narration.txt'))).strftime('%Y-%m-%d')
DIV = re.compile(r'^\s*(?:[─━—–\-=·]{3,}|[─━—–\-]+\s*광고\s*[─━—–\-]+)\s*$')
def ad2_text(name, txt):
    out = []; L = txt.split('\n')
    pills = [k for k, l in enumerate(L) if '💊' in l]
    if not pills: out.append(f'{name}: 💊 줄 없음'); return out
    for k in pills:
        l = L[k]
        if 'health.drkimworld.com' in l: out.append(f'{name}: 💊 줄에 건강몰 가이드 링크 — 쿠팡 제품 직접 링크로(tools/product_link.py)')
        if not re.search(r'https://link\.coupang\.com/(a|re)/', l): out.append(f'{name}: 💊 줄에 쿠팡 제품 직접 링크(link.coupang.com) 없음')
        if '광고' not in l: out.append(f"{name}: 💊 줄에 '광고' 표시 없음")
        j = k - 1
        while j >= 0 and L[j].strip() and not DIV.match(L[j]): j -= 1  # 💊 구역 첫 줄 위로
        if j < 0 or not DIV.match(L[j]): out.append(f'{name}: 💊 구역 앞에 구분선 줄 없음("─────" 또는 "— 광고 —")')
        else:
            if j > 0 and L[j - 1].strip(): out.append(f'{name}: 구분선 줄 앞에 빈 줄 없음(리포트 링크와 떼기)')
            blk_end = k
            while blk_end + 1 < len(L) and L[blk_end + 1].strip(): blk_end += 1
            blk = '\n'.join(L[j + 1:blk_end + 1])
            if re.search(r'drkimworld\.com/r/|텔레그램|t\.me/', blk): out.append(f'{name}: 💊 구역 안에 리포트·텔레그램 링크 — 빈 줄로 뗀다')
    if not re.search(r'쿠팡 ?파트너스 활동의 일환', txt): out.append(f'{name}: 쿠팡 파트너스 문장("…쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.") 없음')
    return out
DATE = ep_date()
NEW = '--compat' not in sys.argv and DATE is not None and DATE >= AD2_FROM
if NEW:
    if deck['paras'][i].get('kind') != 'ad': bad.append('slides.json 광고 문단에 "kind": "ad" 없음(광고 화면·앞뒤 무음 — slidekit)')
    if not re.search(r'제품 링크는 (고정 ?댓글 둘째 줄[·,과와 ]*)?설명란', paras[i]): bad.append("광고 문단 행동 문장 — '<조건> 맞는 제품 링크는 설명란 둘째 줄'(4칸 ④)")
    for f in ('description.txt', 'pinned.txt'):
        pp = os.path.join(V, f)
        if os.path.exists(pp): bad += ad2_text(f, open(pp, encoding='utf-8').read())
    sm = os.path.join(os.path.dirname(os.path.abspath(V)), 'shorts', 'upload_meta.json')
    if os.path.exists(sm):
        try: bad += ad2_text('쇼츠 설명란', json.load(open(sm, encoding='utf-8')).get('description', ''))
        except Exception as e: bad.append(f'쇼츠 upload_meta 읽기 실패: {e}')
AD3_FROM = '2026-11-28'
NEW3 = NEW and DATE >= AD3_FROM
def report_first(name, txt):
    out = []; L = txt.split('\n'); nz = [k for k, l in enumerate(L) if l.strip()]
    rep_k = next((k for k in nz[:2] if 'drkimworld.com/r/' in L[k]), None)
    if rep_k is None: return [f'{name}: 리포트 링크가 첫 두 줄 안에 없음']
    pill = next((k for k, l in enumerate(L) if '💊' in l), None)
    if pill is None or pill < rep_k: return out
    mid = [L[k] for k in range(rep_k + 1, pill) if L[k].strip() and not DIV.match(L[k])]
    if mid: out.append(f'{name}: 리포트 링크 줄과 💊 줄 사이에 다른 줄 {len(mid)}개("{mid[0][:20]}…") — 💊 구역을 리포트 링크 바로 다음으로(빈 줄·구분선만)')
    return out
if NEW3:
    ad_txt = json.dumps(deck['paras'][i].get('slides', []), ensure_ascii=False)
    if re.search(r'근거\s*(의\s*)?질', ad_txt): bad.append("광고 문단 슬라이드에 '근거 질' 문구 — 광고 화면은 고르는 기준(제품 이름 표기)으로, 근거 질 메모는 리포트·건강 가이드에(AD3)")
    try:
        mfds = set(re.findall(r'\{text: "([^"]+)", dose', open(H, encoding='utf-8').read()))
    except Exception: mfds = set()
    for sl in deck['paras'][i].get('slides', []):
        if sl.get('layout') == 'product' and sl.get('why'):
            w = re.sub(r'^\s*식약처\s*[:：]\s*', '', sl['why']).strip()
            if mfds and w not in mfds: bad.append(f"product 'why'가 health.yaml 기능성 문구와 다름: {w[:30]}…(식약처 문구는 그대로)")
    PRICE = r'(하루|1일)\s*(약\s*)?[\d,]+\s*원|[\d,]+\s*원\s*/\s*일|하루\s*\S+\s*원꼴'
    for name, txt in [('광고 슬라이드', ad_txt), (f'narration p{i+1}', paras[i])] + [z for z in zone if z[0] in ('description.txt', 'pinned.txt')]:
        if re.search(PRICE, txt) and '기준일' not in txt: bad.append(f'{name}: 하루 값(원) 주장에 기준일 없음 — 확인된 가격과 기준일이 없으면 쓰지 않는다(AD3)')
    if not re.search(r'제품 링크는 고정 ?댓글 둘째 줄', paras[i]): bad.append("광고 문단 행동 문장 — '제품 링크는 고정댓글 둘째 줄·설명란 둘째 줄'(AD3, 고정댓글 둘째 줄이 먼저)")
    close = [j for j, p in enumerate(paras) if j != i and re.search(r'아까 말씀드린|제품 링크는', p) and '둘째 줄' in p]
    summ = next((j for j, p in enumerate(paras) if j > i and re.match(r'\s*(정리하면|마지막으로 투표|투표 하나)', p)), None)
    if not close: bad.append("마무리 한 문장(아까 말씀드린 … 제품 링크는 고정댓글 둘째 줄·설명란 둘째 줄) 없음(9절 1번)")
    for j in close:
        if summ is not None and j >= summ: bad.append(f'마무리 한 문장이 p{j+1}(정리·투표 p{summ+1} 이후) — 정리·투표 앞 문단 끝으로(AD3)')
        ss = [x for x in re.split(r'(?<=[.?!])\s+', paras[j].strip()) if x]
        k_ad = next((k for k, x in enumerate(ss) if re.search(r'아까 말씀드린|제품 링크는', x)), None)
        k_leg = next((k for k, x in enumerate(ss) if re.search(r'교육용|결정은 각자', x)), None)
        if k_ad is not None and k_leg is not None and k_ad > k_leg: bad.append(f'p{j+1}: 마무리 광고 문장이 교육용 고지 문장 뒤 — 고지 앞으로(AD3)')
        if k_ad is not None and not re.search(r'고정 ?댓글 둘째 줄', ss[k_ad]): bad.append(f"p{j+1}: 마무리 한 문장에 '고정댓글 둘째 줄' 없음(AD3)")
    for f in ('description.txt', 'pinned.txt'):
        pp = os.path.join(V, f)
        if os.path.exists(pp): bad += report_first(f, open(pp, encoding='utf-8').read())
if bad: print('MIDROLL_FAIL p%d · ' % (i + 1) + ' · '.join(bad)); sys.exit(1)
print(f'MIDROLL_OK p{i+1} 문장 {len(sents)} · quote 0 · 위치 약 {pos:.0%} · 금지 낱말 0 · 수요·공급 OK · 긴급성·후기 표지 0(검사 {len(zone)}곳) · ' + (f'AD2 제품 직접 링크·구분선·광고 화면 OK({DATE})' + (' · AD3 근거 질 문구·식약처 문구·마무리 위치·💊 둘째 구역 OK' if NEW3 else '') if NEW else f'AD2 대상 아님(회차 {DATE or "날짜 모름"}{" · --compat" if "--compat" in sys.argv else ""})'))
