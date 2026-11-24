# HANDOFF — PLUG 11-24 정규2 (x8_1124, 121회차 B그룹) · 갱신 2026-11-24 17:00 ET

## 지금 상태: ② 리포트 push 중 → llm_judge → 맥 TTS → chain_long → 업로드
- **확정 종가 정정**: 16:11 info secondaryData 0.937801은 시간외 체결가(분봉 확인) → 폐기. 공식 종가 = 야후 regularMarketPrice(16:00 ET) **PLUG 0.9314(-6.3%)**, QQQ 638.10 등 — research/events.md 맨 아래 '★ 정정' 절이 단일 원천. **할 일: 나스닥 historical에 11/24가 올라오면 0.9314와 대조**(다르면 리포트 updated).
- 매매 질문 **N4 '어디까지 떨어질 수 있을까'**(JOBY 같은 날 H1). 제목: `플러그 파워(PLUG) 어디까지 떨어질까? 1달러 아래 3거래일째 0.9314달러, 병합 권한은 7월에 끝났다 #PLUG`(angle_pick --check OK)
- 판정선: 12/18 종가 1.00 위 26% · 0.927~1.00 24% · 0.838~0.927 20% · 0.838 아래 30%(prob_basis.md)
- 리포트 report/plug-2026-11-5.md(EASY_OK, 그림 6장 figs/) → bin/site_pub.sh 실행 중(report/site_pub.log)
- 대본 video/narration.txt(23문단, GROUP_OK B, PRE_OK 13개) · slides.json(mk_slides.py, anim 15/21, 새 화면 체계) · mk_meta.py · 쇼츠 shorts/(SHORTS_OK) · SNS sns/mk_queue.py(S1) · 썸네일 video/thumb/custom(make_v7 a·b, PLUG_thumbnail.jpg = a) · 영양제 H2 p14(59%, AB5-B) kit/h2_card.png
- bin/publish_loop.sh: reel_cover(cover_ig.jpg)·angle N4 반영, bin/record.py 새로 씀

## 남은 일
1. site_pub 끝나면 `python3 tools/llm_judge.py plug-2026-11-5 --wait 10` → 맞는 지적만 고쳐 다시 push(updated)
2. 맥 TTS `bash bin/tts_mac.sh`(run_in_background) → `bash bin/after_tts.sh` → CHAIN_DONE·video_check long·ad_gap_check --strict
3. `bash bin/publish_loop.sh`(run_in_background) — 업로드 한도면 30분마다 재시도
## 막힌 것
- listingcenter.nasdaq.com 403(NEED.txt) · 나스닥 historical 11/24 게시 지연
