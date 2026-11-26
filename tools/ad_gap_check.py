#!/usr/bin/env python3
"""롱폼 광고 간격·총량 검사 (운영자 2026-11-22 "유저경험 해치지 않는 한도에서 광고 꽉꽉 채워넣어" — UX 한도).
합성 뒤(slides_out/segments.json이 생긴 뒤) 돈다. chain_long.sh가 video_check 다음에 부른다.

사용: python3 tools/ad_gap_check.py <video 폴더> [--strict] [--retention]
  --retention: 업로드 뒤(폴더에 video_id) 광고 구간마다 시청 유지 하락(시작 직전 − 끝 1초 뒤, %p)을 한 줄 더 찍는다 —
    tools/yt_analytics_read.py 유지 곡선(최근 14일 롱폼, 사이트 yt-analytics.yml). AD1 광고 가드 영상 쪽 판정 자료(판정은 사람이, 숫자는 공개 기록에 쓰지 않음)
  → AD_GAP_OK … | AD_GAP_WARN …(기본: 끝 코드 0) | AD_GAP_FAIL …(--strict일 때 끝 코드 1)
  slides_out/yt_midroll_points.txt 에 유튜브 미드롤 광고 권장 시각(장면 전환)을 쓴다(8분 이상만, 업로드 때 운영자 스튜디오 몫).

광고로 세는 화면(겹치면 하나로 합침):
  - 사이트 안내 전체 화면(segments 'ad' = ('AD','rep'|'app'))·쿠팡/몰 카드(('AD','shop'))·사이트 안내 하단 배너(키 4칸 'B')
  - 쿠팡·몰 짧은 띠(shop_strip_at, 6초씩)
  - 영양제 중간광고 문단 전체(slides.json 'shop' 문단 중 대본에 '유료 광고'가 든 문단 — midroll_check와 같은 기준)
  세지 않는 것: 구독 띠·이어 보기 띠(채널 안 안내), 마무리 직전 '고르는 법' 한 문장(화면은 본문 그대로)

규칙(근거: 11-21~22 롱폼 3편 실측 — 길이 499~634초, 광고 화면 53~66초(10~12%), 띠가 중간광고 시작과 겹침, 광고 사이 22~47초 간격 4곳):
  1. 첫 30초에 광고 없음
  2. outro(마지막 outro_sec, 보통 20초)에 광고 없음
  3. 광고 사이 60초 이상(합친 구간 끝 → 다음 구간 시작)
  4. 광고 화면 합계 ≤ min(영상 길이의 12%, 75초)
"""
import ast, json, os, re, sys

V = sys.argv[1]
STRICT = '--strict' in sys.argv
STRIP_SEC = 6.0
GAP, HEAD, SHARE, CAP = 60.0, 30.0, 0.12, 75.0

seg_p = os.path.join(V, 'slides_out', 'segments.json')
if not os.path.exists(seg_p):
    print('AD_GAP_SKIP segments.json 없음(합성 전)'); sys.exit(0)
d = json.load(open(seg_p, encoding='utf-8'))
deck = json.load(open(os.path.join(V, 'slides.json'), encoding='utf-8'))
paras = [p for p in open(os.path.join(V, 'narration.txt'), encoding='utf-8').read().split('\n\n') if p.strip()] if os.path.exists(os.path.join(V, 'narration.txt')) else []
dur = float(d['duration']); outro0 = dur - float(d.get('outro_sec') or 20.0)
segs = []
for a, k, b in d['segments']:
    try: segs.append((float(a), ast.literal_eval(k), float(b)))
    except Exception: pass

win = []  # (시작, 끝, 이름)
for a, k, b in segs:
    if k and k[0] == 'AD': win.append((a, b, 'shop카드' if k[1] == 'shop' else '사이트안내(전체)'))
    elif k and k[0] == 'AG': win.append((a, b, '영양제 중간광고'))  # 광고 표지(11-26)
    elif len(k) == 4: win.append((a, b, '사이트안내(배너)'))
for t in d.get('shop_strip_at') or []:
    win.append((float(t), float(t) + STRIP_SEC, '쿠팡·몰 띠'))
mid = [i for i, p in enumerate(deck.get('paras', [])) if (p.get('shop') or p.get('kind') == 'ad') and i < len(paras) and '유료 광고' in paras[i]]
for i in mid[:1]:
    xs = [(a, b) for a, k, b in segs if k and k[0] == i]
    if xs: win.append((min(x[0] for x in xs), max(x[1] for x in xs), '영양제 중간광고'))
# 2026-11-26 광고 구분(slidekit 문단 "kind": "ad"): 앞 '광고' 표지·무음 0.8초와 뒤 무음 0.6초까지 광고 구간으로 센다(segments 'ad_kind')
if d.get('ad_kind'): win.append((float(d['ad_kind'][0]), float(d['ad_kind'][1]), '영양제 중간광고'))
win.sort()
merged = []
for a, b, n in win:
    if merged and a <= merged[-1][1] + 0.5:
        merged[-1] = [merged[-1][0], max(merged[-1][1], b), merged[-1][2] + ('+' + n if n not in merged[-1][2] else '')]
    else:
        merged.append([a, b, n])

bad = []
total = round(sum(b - a for a, b, _ in merged), 1)
cap = round(min(dur * SHARE, CAP), 1)
for a, b, n in merged:
    if a < HEAD: bad.append(f'첫 {HEAD:.0f}초 안 광고 {n} {a:.0f}초')
    if b > outro0 + 0.5: bad.append(f'outro 안 광고 {n} {a:.0f}~{b:.0f}초(outro {outro0:.0f}초~)')
for (a1, b1, n1), (a2, b2, n2) in zip(merged, merged[1:]):
    if a2 - b1 < GAP: bad.append(f'간격 {a2 - b1:.0f}초<{GAP:.0f}: {n1}({b1:.0f}) → {n2}({a2:.0f})')
if total > cap: bad.append(f'광고 화면 합계 {total}초 > 상한 {cap}초(길이 {dur:.0f}초의 {SHARE:.0%}·최대 {CAP:.0f}초)')

# 유튜브 미드롤 광고 권장 시각: 8분 이상만. 문단 경계(장면 전환) 중 첫 60초·outro 앞 60초 밖, 우리 광고 구간 ±20초 밖, 2분 이상 간격
pts = []
if dur >= 480:
    starts = sorted({round(min(a for a, k, b in segs if k and k[0] == i), 1) for i in range(len(deck.get('paras', []))) if any(k and k[0] == i for _, k, _ in segs)})
    for t in starts:
        if t < 60 or t > outro0 - 60: continue
        if any(a - 20 <= t <= b + 20 for a, b, _ in merged): continue
        if pts and t - pts[-1] < 120: continue
        pts.append(t)
    with open(os.path.join(V, 'slides_out', 'yt_midroll_points.txt'), 'w', encoding='utf-8') as f:
        f.write('# 유튜브 스튜디오 > 콘텐츠 > 영상 > 수익 창출 > 광고 시점(미드롤) 권장 위치 — 장면 전환, 우리 광고 구간 ±20초 밖(YPP가 열린 뒤에만 쓸모)\n')
        f.write('\n'.join(f'{int(t // 60)}:{int(t % 60):02d}' for t in pts) + '\n')

summ = f'길이 {dur:.0f}초 · 광고 {len(merged)}곳 합계 {total}초({total / dur:.0%}, 상한 {cap}초) · 구간 ' + ', '.join(f'{a:.0f}~{b:.0f} {n}' for a, b, n in merged)
if pts: summ += f' · 유튜브 미드롤 권장 {len(pts)}곳(slides_out/yt_midroll_points.txt)'
if '--retention' in sys.argv:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from yt_analytics_read import ret_drop
    vid = open(os.path.join(V, 'video_id')).read().strip() if os.path.exists(os.path.join(V, 'video_id')) else ''
    dr = [(a, n, ret_drop(vid, max(0.0, a - 1), b + 1)) for a, b, n in merged] if vid else []
    print('AD_RETENTION ' + (' · '.join(f'{a:.0f}초 {n} {x:+.1f}%p' for a, n, x in dr if x is not None) or '자료 없음(video_id·유지 곡선 — yt_analytics_read.py --pull)'))
if bad:
    print(('AD_GAP_FAIL ' if STRICT else 'AD_GAP_WARN ') + ' · '.join(bad) + ' | ' + summ)
    sys.exit(1 if STRICT else 0)
print('AD_GAP_OK ' + summ)
