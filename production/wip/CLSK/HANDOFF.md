# HANDOFF — CLSK 11-25 요청 1편 (clsk1125) · 1단계 끝 2026-11-25 10:05Z (05:05 ET)

## 지금 상태: ① 조사·대본·리포트 초안 끝 → **대기: 11/25 16:00 ET 확정 종가**
- 요청: @이준호-c3o(IREN 영상 MGh3KnhUDAM) "실적과 데이터센터전환", 스레드 `UgxJ7XlKj9zWiD-RZa94AaABAg@MGh3KnhUDAM`, requests.md CLSK 행 '대기' → 공개 뒤 comments.md 2-1 완료 답글(영상+리포트 맨 주소)
- slug **clsk-2026-11**(새), 직전 clsk-2026-10(10-09, 영상 zJw57dTqD-0). 매매 질문 **H1 '지금 팔아야 될까?'**(angle_pick 1순위 7.1) — 후보 E6(6, 단 S-3ASR은 실제 판매 아님 → '증자 발표' 표현 부정확), E8(6, 조건: 11/25 첫날 -10% 이하 = 4.60 이하일 때만). 대안 H8 '오래 들고 가도 될까?'(데이터센터 전환 질문에 맞음)
- **숫자 단일 원천 research/events.md**(SEC 3건 원문 요약·종가·비트코인·기저율). 공시 원문 텍스트 research/sec/
- 11/24 종가 **5.115**(나스닥 historical = 야후 regularMarketPrice). 나스닥 info secondaryData 5.08은 시간외 → 쓰지 않음(PLUG 사고 재현 확인)
- 지난 편 채점 research/prev_report.md: 적중 3 · 빗나감 3 · 확인 전 1(시나리오 3 = 12/02 종가 판정). 장부(pred_ledger)엔 CLSK 0건 → 사람 채점
- 가능성 research/prob_basis.md: 12/23 종가(11/24 5.115 기준 고정) 5.63 위 25 · 4.89~5.63 20 · 4.35~4.89 20 · **4.35 아래 35(유력)**
- 거시 research/macro.md(MACRO_OK, 구간 10/09→11/24): QQQ -15.1%, 평소 민감도 2.46배 예상 -35.6% vs 실제 -51.3%(평소 흔들림 안). 다음 12/9 FOMC. CPI·고용 일정 BLS 403(NEED.txt)
- 대본 video/narration.txt(24문단 초안, 【11/25 종가 한글】·【11/25 등락 한글】 자리) — NUMSPEAK_OK·JOSA_OK·AI_FEEL_OK·CLOSE_OK·macro_check script OK. 영양제 **H3 유산균** 15문단(62%, 첫 단서 직후·갈래 앞), 사이트 안내(ad) 9문단(37%, 중간광고와 6문단 떨어짐), 구독 문장 19문단
- 리포트 report/clsk-2026-11.md(story, 그림 6장 자리) — easy_check: **그림 파일·명세 없음만 남음**(나머지 통과), macro_check report OK. 【11/25 종가】【11/25 등락】【칸】 자리 4곳 + sources 【2단계】 줄
- 썸네일 video/thumb/COPY.md(시안 a·b·c, 제목 초안) + spec_draft.json(closes 끝 【11/25】). 그림 계획 figs/FIGS_PLAN.md

## 대기: 11/25 16:00 ET 확정 종가 (16:10 ET 이후)
1. 나스닥 `curl -s -A 'Mozilla/5.0 research' 'https://api.nasdaq.com/api/quote/CLSK/info?assetclass=stocks'` secondaryData 'Closed at Nov 25, 2026 4:00 PM ET' — **단 16:00 체결가인지 분봉으로 확인**(야후 `v8/finance/chart/CLSK?range=1d&interval=1m&includePrePost=true`의 15:59~16:00 ET = 20:59~21:00Z 값), 야후 `range=5d&interval=1d` meta.regularMarketPrice로 대조. 나스닥 historical에 11/25가 올라오면 그것이 최종
2. 같은 방법으로 QQQ·IREN·APLD·CORZ 11/25 종가(시장 표 한 줄 추가할지 판단), 비트코인 11/25
3. 11/25 오후 EDGAR 재확인(`data.sec.gov/submissions/CIK0000827876.json`) — 424B(판매 보충서)·8-K 새로 있으면 events.md에 추가하고 판정/대본 고침

## 남은 일(2단계 → 3단계)
1. 자리 채우기: events.md 6절 【11/25 종가】, 리포트(summary·첫 문단·'지금 자리 【칸】'·sources), 대본 1문단, 썸네일 spec, 제목. 11/25 등락 = 5.115 대비. 칸: 5.63 위/4.89~5.63/4.35~4.89/4.35 아래
2. 질문 확정: 11/25 ≤ 4.60(-10%)이면 E8도 검토(직전 5회 H2 T3 E2 N4 E5 — H1·E8 모두 겹치지 않음). 확정 뒤 `angle_pick.py --check "<제목>"`
3. 사이트 worktree(`git -C /home/user/kimworld-site worktree add /home/claude/site-clsk origin/main`) → figs.json(FIGS_PLAN.md) → figkit make → 원고 복사 → data/tickers.yaml CLSK 확인 → easy_check EASY_OK → `python3 tests/test_build.py`·`python3 build.py --strict` → `bash /home/user/kimworld-media/tools/site_push.sh` → `python3 tools/llm_judge.py clsk-2026-11 --wait 10` 반영(**녹음 전에**)
4. slides.json(mk_slides, 지난 편 성적 list 슬라이드·anim 60%↑·H3 카드·sub·ad 번호) → `pre_tts_check.sh` PRE_OK → 맥 TTS → chain_long(video_check long·ad_gap_check --strict)
5. upload_meta(설명란 둘째 줄 💊 marketing.md 3절 맨 위 형식: `💊 하루 대부분 앉아서 차트를 보신다면 — 유산균은 뒷면 균주 이름(비피더스균 락티스)(식약처 기준) 하나만 보면 됩니다. 고르는 법(광고): https://health.drkimworld.com/guide/probiotics/?utm_source=youtube&utm_medium=midroll&utm_campaign=clsk-2026-11#items`, 📺 함께 보면: 아이렌 MGh3KnhUDAM, ⏮ 지난 편 zJw57dTqD-0, 📊 성적표, 지난 예측 한 줄, 시청자 요청 출처) → 업로드 → youtube_id → 요청 완료 답글(yt_reply --kind request, 리포트 끝 '지난 예측 채점표'·'데이터센터 전환 진행' 표 안내) → requests.md '완료(clsk-2026-11, <ID>)'
6. 쇼츠·Threads 2글(💊 줄은 링크 목록과 빈 줄로 뗀 자기 문단)·릴스, followups.md(12/02 시나리오 3 채점, 12/23 판정), angle_log --add, ad_log H3, ebook filings(S-3ASR 사례), review/predictions/CLSK.md 새로 만들기, sector_map.md CLSK 줄(macro_ctx 경고)
7. 정리: 디스크 6.2G(1단계에 x8_1124/video/slides_out 1.5G 지움, 썸네일·thumbswap/build 보존)

## 막힌 것
- BLS CPI·고용 일정 403(NEED.txt) — '확인 안 됨'으로 둠
- 세입자 이름·텍사스 독점 만료 날짜·새 판매 금액: 공시에 없음 → 쓰지 않음(지난 리포트의 '메타 자회사'는 인용으로만)
