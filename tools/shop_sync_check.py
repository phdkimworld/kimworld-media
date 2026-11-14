# 쿠팡 안내 문장 ↔ yt-shop 상품 일치 검사(85회차 QXO: yt-shop을 부르기 전에 '공구 세트' 문장을 써서 맥 TTS 제출 뒤 카테고리(취미·등산 스틱)와 어긋남 → 문단 재녹음)
# 사용: python3 shop_sync_check.py <video 폴더>  — narration.txt의 '쿠팡' 문장에 ../kit/shop/candidates.json keyword 낱말(앞 두 글자)이 하나라도 있어야 한다.
#   candidates.json이 없으면 FAIL(대본 쓰기 전 yt-shop 실행, SKILL V3.9 1단계). group_check가 TTS 전에 부른다.
import json, os, re, sys
v = os.path.abspath(sys.argv[1]); nar = os.path.join(v, 'narration.txt')
cand = os.path.join(v, '..', 'kit', 'shop', 'candidates.json')
sen = [s for s in re.split(r'(?<=[.?!])\s+', open(nar, encoding='utf-8').read()) if '쿠팡' in s]
if not sen: print('SHOP_SYNC_SKIP 쿠팡 문장 없음'); sys.exit(0)
if not os.path.exists(cand): print('SHOP_SYNC_FAIL kit/shop/candidates.json 없음 — 쿠팡 문장을 쓰기 전에 yt-shop.yml 실행(SKILL V3.9)'); sys.exit(1)
kw = json.load(open(cand, encoding='utf-8')).get('keyword', '')
toks = [t[:2] for t in re.split(r'\s+', kw) if len(t) >= 2] or [kw]
if any(t in s for s in sen for t in toks): print(f'SHOP_SYNC_OK {kw}'); sys.exit(0)
print(f"SHOP_SYNC_FAIL 쿠팡 문장이 상품 '{kw}'과 다름: {sen[0].strip()[:50]}"); sys.exit(1)
