# slidekit 대기 변경안 — 광고 간격 60초·총량 상한 (2026-11-22 "광고 꽉꽉" UX 한도)

상태: **적용**(2026-11-22, 사이트 `tools/slidekit/make_slide_video.py` `strip_windows()` + 브랜드 스팅 앞뒤 2초·outro(엔드카드) 금지, `check_slides.py` WARN ADGAP, `chain_long.sh` `ad_gap_check.py --strict`). 아래는 적용 전 기록.

이전 상태: 대기. 사이트 `tools/slidekit/`은 다른 에이전트가 브랜드 인트로·아웃트로 엔드카드 작업 중이라 그 작업이 끝난 뒤 적용한다(아웃트로 엔드카드 홍보 칸 2개는 그 에이전트 몫 — 여기서 다루지 않음).
적용한 뒤: `tools/chain_long.sh`의 `ad_gap_check.py . | tail -1`을 `ad_gap_check.py . --strict … || { echo "CHAIN_FAIL ad_gap_check"; exit 1; }`로 올리고 이 문서 상태를 '적용'으로.

근거: 11-21~22 롱폼 3편 `ad_gap_check.py` — 띠가 영양제 중간광고 시작과 겹침(3편 모두), 광고 사이 22~59초 간격 2~3곳씩, 합계 11~13%. 원인은 `strip_windows()`가 ① 중간광고 문단(사진 없는 'shop' 카드가 든 문단 전체)을 바쁜 구간으로 안 보고 ② 다른 광고와 띠 사이를 0.5초만 띄우고 ③ 띠끼리 30초만 띄우며 ④ '카드 직전' 목표가 중간광고 문단 시작에 떨어지기 때문.

## 1. `tools/slidekit/make_slide_video.py` `strip_windows()` (현재 214~226행 근처)
```python
AD_GAP = 60.0   # 광고 사이 최소 간격(초)
def strip_windows():
    if not deck.get('shop_strip'): return []
    # 광고 구간: 사이트 안내(전체·배너)·카드 + 영양제 중간광고 문단 전체(문단 'shop'이 있는 문단)
    adw = [(a, b) for a, k, b, _ in segs if isad(k) or len(k) == 4]
    for pi, pd in enumerate(D):
        if pd.get('shop'):
            adw.append((P[pi]['start'], P[pi]['sents'][-1]['end']))
    busy = [(a - AD_GAP, b + AD_GAP) for a, b in adw] \
         + [(a, b) for a, k, b, _ in segs if isanim(k)] + [(0, 30.0), (outro_t0, total)] + sub_win + next_win
    free = lambda t: all(t + STRIP_SEC <= a - 0.5 or t >= b + 0.5 for a, b in busy)
    cuts = sorted({round(a, 2) for a, _, _, _ in segs})
    targets = [total / 3, total * 2 / 3]          # '카드 직전' 목표는 뺀다(카드가 중간광고 문단 안이라 광고가 붙음)
    cap = min(total * 0.12, 75.0) - sum(b - a for a, b in adw)   # 광고 화면 합계 상한에서 남은 초
    wins = []
    for tg in targets:
        if cap < STRIP_SEC: break
        cand = [c for c in cuts if tg - 25 <= c <= tg + 40] + [tg]
        cand.sort(key=lambda c: abs(c - tg) + (0 if c in cuts else 8))
        for c in cand:
            if c >= 0 and free(c) and all(abs(c - w) >= AD_GAP + STRIP_SEC for w in wins):
                wins.append(round(c, 2)); cap -= STRIP_SEC; break
    return sorted(wins)
```
- 바뀌는 점: 띠 0~2개(전에는 2~3개). 넣을 자리가 없으면 띠를 빼는 것이 맞다(간격·총량이 먼저).
- health_midroll.md 9절 1번 '마지막 2분 화면 아래 💊 띠'를 따로 구현할 때도 같은 `busy`·`cap`을 쓰고 outro(`outro_t0` 뒤)에는 넣지 않는다.

## 2. 사이트 안내 배너(`ad_style` 'banner')
- 첫 안내 문단 배너가 34~43초에 뜬다(첫 30초 밖이라 통과). 그대로 두되, 대본 쪽 규칙(production.md 미드롤·음성 안내 줄)으로 안내 문장을 중간광고·띠와 60초 떨어뜨린다. slidekit 변경 없음.

## 3. `check_slides.py` (선택)
- `ADGAP` 경고: 'ad' 문장이 든 문단과 'shop' 문단의 문단 번호 거리가 1 이하이면 WARN(합성 전 미리 알림). 최종 판정은 합성 뒤 `ad_gap_check.py`.

## 4. 시험
- 11-21~22 세 편(xtra3_1121·xtra4_1121·wk1122 사본)으로 합성만 다시 돌려 `ad_gap_check.py --strict`가 OK인지, 띠 프레임이 핵심 숫자를 가리지 않는지 Read로 확인.
