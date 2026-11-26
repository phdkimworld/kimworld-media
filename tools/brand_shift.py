#!/usr/bin/env python3
"""설명란 챕터 시각을 브랜드 인트로 길이만큼 민다(2026-11-22 운영자 "인트로 영상을 만들어서 브랜드를 각인", 사이트 slidekit/brand.py).
합성(make_slide_video.py)이 영상 맨 앞(0초, 11-22 운영자 "인트로로 브랜드를 각인하라고 했잖아" — 기본)이나 훅 문단 뒤(예전 방식)에 2.4초 인트로를 넣으면
그 뒤 나레이션이 모두 2.4초 밀린다. mk_meta.py는 raw_timing.json(원래 녹음 시각)으로 챕터를 쓰므로, 끼운 시각 이후 챕터에 길이를 더한다(초 올림 —
챕터가 말보다 먼저 시작하지 않게). 첫 챕터 00:00은 늘 그대로 둔다(유튜브 챕터는 0:00에서 시작해야 함 — 0초 인트로면 첫 챕터가 인트로를 품는다, '0:00 인트로' 챕터는 만들지 않음).
사용: python3 tools/brand_shift.py <video 폴더>   (mk_meta.py 바로 뒤, chain_long.sh가 부른다)
- slides_out/segments.json 'brand_intro' = [시각, 길이]가 없으면(인트로 없음·NO_BRAND) 아무것도 하지 않는다: BRAND_SHIFT_SKIP
- upload_meta.json 'brand_shift'에 적용한 값을 남겨 두 번 밀지 않는다(mk_meta.py를 다시 돌리면 그 키가 없어져 다시 민다)
- video_check.py long이 segments 'brand_intro'와 upload_meta 'brand_shift'가 다르면 실패시킨다
"""
import json, math, os, re, sys

V = sys.argv[1] if len(sys.argv) > 1 else '.'
seg = json.load(open(os.path.join(V, 'slides_out', 'segments.json'), encoding='utf-8'))
bi = seg.get('brand_intro')
mp = os.path.join(V, 'upload_meta.json')
# 2026-11-26 광고 구분(slidekit 문단 "kind": "ad"): 광고 앞 0.8초·뒤 0.6초 무음만큼 뒤 챕터도 민다(segments 'ad_gaps' = [[영상 시각, 길이]…], upload_meta 'ad_gap_shift')
def ad_gap_shift():
    gaps = seg.get('ad_gaps') or []
    if not gaps: return
    meta = json.load(open(mp, encoding='utf-8'))
    if meta.get('ad_gap_shift') == gaps: print('AD_GAP_SHIFT_OK 이미 적용', gaps); return
    k = [0]
    def fx(m):
        mm, ss = int(m.group(1)), int(m.group(2)); t = mm * 60 + ss
        if t == 0: return m.group(0)
        # 앞 무음: 광고 챕터 자체(표지 = 광고 시작)는 그대로, 그 뒤 챕터만 민다. 뒤 무음: 광고 끝 이후 챕터를 민다(앞 무음을 더한 시각으로 비교)
        t2 = float(t)
        for j, (at, sec) in enumerate(gaps):
            if t2 >= (at + 1.0 if j == 0 else at - 0.5): t2 += sec
        if t2 == t: return m.group(0)
        k[0] += 1; t = int(math.ceil(t2)); return f'{t // 60:02d}:{t % 60:02d}{m.group(3)}'
    meta['description'] = re.sub(r'^(\d{1,2}):(\d{2})(\s)', fx, meta['description'], flags=re.M)
    meta['ad_gap_shift'] = gaps
    json.dump(meta, open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'AD_GAP_SHIFT_OK 챕터 {k[0]}개 (광고 무음 {gaps})')
import atexit; atexit.register(ad_gap_shift)
if not bi: print('BRAND_SHIFT_SKIP 인트로 없음'); sys.exit(0)
meta = json.load(open(mp, encoding='utf-8'))
if meta.get('brand_shift') == bi: print('BRAND_SHIFT_OK 이미 적용', bi); sys.exit(0)
if meta.get('brand_shift'): sys.exit(f"BRAND_SHIFT_FAIL 다른 값이 이미 적용됨 {meta['brand_shift']} ≠ {bi}: mk_meta.py를 다시 돌린 뒤 실행")
at, sec = bi; n = 0
def fix(m):
    global n
    mm, ss = int(m.group(1)), int(m.group(2)); t = mm * 60 + ss
    if t == 0 or t < math.floor(at): return m.group(0)  # mk_meta는 초를 버림으로 적는다(24.8초 → 00:24)
    n += 1; t = int(math.ceil(t + sec)); return f'{t // 60:02d}:{t % 60:02d}{m.group(3)}'
meta['description'] = re.sub(r'^(\d{1,2}):(\d{2})(\s)', fix, meta['description'], flags=re.M)
meta['brand_shift'] = bi
json.dump(meta, open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'BRAND_SHIFT_OK 챕터 {n}개 +{sec}초({at}초 뒤)')
