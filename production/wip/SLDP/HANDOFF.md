# HANDOFF — SLDP 11-25 정규 (sldp1125, 123회차 잠정 B그룹) · 갱신 2026-11-25 16:40Z

## 지금 상태: ① 조사·대본·리포트 끝 → ② 맥 TTS 대기 + 리포트 사이트 발행(test_build) 진행
- 선정: SLDP★ — 11/24 1.32(-6.7%) 1년 최저 2거래일 만에 재경신, 경신 구간 11번째(10/19 1.95 대비 -32.3%), SEC 11/4 뒤 0건. review/selection.md 11-25 (sldp1125) 줄
- 숫자 원천: research/events.md · research/prob_basis.md · research/macro.md · research/base.py(dl/ 나스닥 1,390일)
- 확정 종가 = 나스닥 historical 11/24 행(SLDP 1.32, QQQ 638.10, LIT 53.69, QS 2.78)
- 매매 질문 H3 '물타기 해도 될까'. 제목 `솔리드파워(SLDP) 물타기 해도 될까? 1년 최저 1.32달러를 2거래일 만에 또, 현금의 0.76배 #SLDP`(ANGLE_TITLE_OK)
- 판정 12/23 종가: 1.73 위 8% · 1.32~1.73 30% · 1.17~1.32 28% · 1.17 아래 34%
- 리포트 report/sldp-2026-11-5.md(EASY_OK, 그림 6장, 사이트 worktree /home/claude/site-sldp25에 복사) — bin/site_pub.sh → report/site_pub.log(SITE_PUSHED 확인)
- 대본 video/narration.txt(21문단 12.92KB, GROUP_OK B, PRE_OK 9개, num_check OK, prev_calls OK) · slides.json(mk_slides.py, anim 15/21) · mk_meta.py · 쇼츠 shorts/(mk_shorts.py·mk_meta.py) · SNS sns/mk_queue.py(dry queue_check: 표지 파일만 없음) · 썸네일 video/thumb/SLDP_thumbnail.jpg(make_v7 a) · 영양제 H2 p12 kit/h2_card.png · 미드롤 kit/sldp_youtube_midroll_*.png
- 맥 TTS id 110_kwa_sldp1125_tts1 (bin/tts_mac.sh, 로그 video/tts_run.log — 'TTS_DONE'이면 끝)

## 진행(17:25Z)
- 리포트 push b480f2e(SITE_PUSHED) · llm_judge 10개 중 맞는 지적 반영(report/ 원고만, youtube_id 연결 때 함께 push) · EASY_OK
- TTS 끝(110_kwa_sldp1125_tts1) · ASR: 문단 7·13·18 st_redo(18은 '남은 시장 매각 한도, 약 오천구백만'), 남은 MISS 2는 표기 한계 → video/asr_check.ok
- check_slides(beats·BIG)·still_check(p3·p13 stat 연속) 고쳐 chain 재실행 중(video/chain.log)

## 남은 일(순서)
1. site_pub SITE_PUSHED 뒤 `python3 tools/llm_judge.py sldp-2026-11-5 --wait 10` → 맞는 지적만 report 고쳐 updated 그대로 둬도 됨(youtube_id 연결 때 함께 push)
2. TTS_DONE 뒤 `bash bin/after_tts.sh`(run_in_background) → video/after.log 'AFTER_CHAIN_OK'(chain_long: debreath·video_check long/shorts·ad_gap_check·midroll) — 직접 `python3 tools/ad_gap_check.py --strict video` 한 번 더
3. `bash bin/publish_loop.sh`(run_in_background) — wait_live → 업로드(썸네일 429면 재시도 없음, record.py가 thumb_history pending에 적음) → youtube_id 연결 → SNS 대기열(queue_check) → 쇼츠 → angle_log H3 · ledger extract/score · record.py · media push
4. 끝나면 production/wip/SLDP 지우기, worktree /home/claude/site-sldp25 제거(썸네일 끝난 뒤)
## 막힌 것
- 없음(BLS 일정 403 — macro_ctx NEED.txt, CPI 날짜 미확인으로 표기)
