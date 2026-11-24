# HANDOFF — PLUG 11-24 정규2 (x8_1124) · 갱신 2026-11-24 12:20 ET

## 지금 상태: ① 조사 1차 끝 → **대기: 11/24 16:00 ET 확정 종가**
- 종목: **PLUG 플러그 파워(잠정)** — selection.md·STATE.md(진행 중) 기록. 종가 뒤 PLUG·LAES·SLDP 다시 보고 확정(LAES는 72시간 안이라 사실상 PLUG·SLDP 비교, SLDP는 SEC 11/04 뒤 0건).
- 회차 번호: STATE 마지막 119(LAES) → JOBY(joby1124)가 120이면 이 편 **121 = 홀수 B그룹**(STATE 푸시 때 번호 겹침 확인).
- 사이트 worktree `/home/claude/site-x8`(origin/main 0756654, 디자인 개편 포함), slidekit `/home/claude/slidekit` = main tools/slidekit(SAME 확인 11-24 11:58 ET). 디스크 7.3G 남음(업로드 끝난 렌더 wk·wk1122·x5·plugtest·옛 /tmp/kws-* 지움).
- slug 예정 `plug-2026-11-5`(없음 확인).

## 확정 숫자·출처 → `research/events.md`(단일 원천)
- 11/19 1.03 · 11/20 0.9565(2025-06 뒤 첫 1달러 아래 마감) · 11/23 0.9936(+3.9%, QQQ +7.0%) · 11/24 장중 0.92 전후(-7.5%)
- 1달러 규칙: 11/20부터 계속 아래면 30번째 거래일 2027-01-05, 20번째 12-18(지난 편 판정일)
- 새 사실(공시 원문 확인): 2025-07-03 주총 병합 권한(1대5~1대200)은 1년 안 미실행 시 소멸 → 2026-07-03 소멸, 2026-06-11 주총 안건에 병합 없음, 2026-02-12 수권 주식 30억 주로 늘림. 10-Q엔 상장 유지·병합 언급 없음.
- 지난 편 네 갈래(12/18): 1.11 위 35%(유력, 처음으로 위쪽) · 1.00~1.11 25% · 0.927~1.00 15% · 0.927 아래 25%. 확인 3순위 '1달러 아래 마감' → 11/20 발생. "1달러 아래 마감이면 앞당김" 약속을 이번 편이 지킴.
- 기저율 스크립트 `research/base.py <11/24종가> <QQQ종가>`(1달러 아래 구간 5개·1년 최저). 지난 편 표 '1년 최저 17번(9 높음·8 낮음)'·'심포지엄 7번' 재사용 가능.

## 남은 일(다음 에이전트)
1. 16:05 ET 뒤: `curl -s -A 'Mozilla/5.0 research' "https://api.nasdaq.com/api/quote/PLUG/info?assetclass=stocks"` secondaryData "Closed at Nov 24, 2026 4:00 PM ET" — PLUG·QQQ(etf)·IWM·ICLN·FCEL·BLDP·BE·LAES·SLDP. EDGAR 제출 목록 다시(장후 8-K 있으면 원문).
2. `python3 research/base.py <종가> <QQQ>` → 1년 최저 여부·'2025-06-05 뒤 최저' 여부. `python3 bin/macro_wrap.py PLUG --date 2026-11-24 --work /home/claude/x8_1124`(이미 core1123 래퍼를 11/24용으로 바꿔 둠).
3. 매매 질문: `angle_pick.py PLUG --event 최저,상폐경고,급락` 후보 H1 '지금 팔아야 될까'(7.1)·N4 '어디까지 떨어질 수 있을까'·H4 '손절선은 어디일까'·H9 '물렸다면'. 직전 5회 N1·N1·H2·T3·E2 → H1 또는 N4 권장. '상폐경고'는 아직 통지 없음 — 대본·제목에 '경고'라고 쓰지 말고 '1달러 규칙'으로.
4. prob_basis.md(유력 ≤40%, 핵심 통찰 1: 이탈 쪽 4/4·지킨다 0/4, 지난 편 위쪽 35%가 다음 날 깨짐을 '틀린다면'에), prev_report.md(지난 편 4갈래·확인 3개 채점), 리포트(style: story, 그림 4~6, 새 리포트 첫 화면 규칙: 사이트 AGENTS.md·seo.md summary·seo_desc), 대본·slides.json(V6.4~6.7 새 체계, 0초 인트로 질문 줄), 쇼츠.
5. 영양제 **H2 루테인**, 바꿀 한 가지 = **AB5-B 위치: 시나리오 직후(약 62%)**(ad_log: H2 직전 iren 266초 52%·AB6-B 다리 질문형 — 나머지 AB1-B·AB3-B·AB4-B 그대로). ad_conv 전부 방문 0 → 표본 부족, 하나만 바꿈.
6. llm_judge는 리포트 push 뒤 **녹음 전에**. 녹음은 `bin/tts_mac.sh`(맥 중계), 뒤 `bin/after_tts.sh`(chain_long). 사이트 push `bin/site_pub.sh "<메시지>" <파일…>`. 업로드 `bin/publish_loop.sh`(run_in_background만, slug plug-2026-11-5로 치환돼 있음 — 기록 함수 record.py는 새로 써야 함, 선례 /home/claude/core1123/bin/record.py).
7. **새 키트 첫 실전**: 합성 뒤 video_check long·ad_gap_check --strict 통과 확인, 실패 시 키트 원인 짧게. 썸네일 make_v7.py 시안 a·b → `/tmp/claude-0/-home-user/4daa7866-678d-5bcc-85e5-eccd4498203b/scratchpad/x8/`에도 복사. SNS: reel_cover.py → static/social/plug-2026-11-5/cover_ig.jpg + media.cover, Threads 첫 줄 45자·문단 100자, queue_check [S1].

## 막힌 것
- listingcenter.nasdaq.com 규칙 원문 403 → 우회 안 함(NEED.txt), 지난 편 sources 그대로.
