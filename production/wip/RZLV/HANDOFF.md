# HANDOFF — RZLV 11-27 요청 후속편 (rzlv1127, 127회차 B그룹 잠정) · 갱신 2026-11-27 07:15Z

작업 폴더 /dev/shm/rzlv1127 (= /home/claude/rzlv1127 심볼릭 링크) · 사이트 worktree /dev/shm/site-rzlv · wip: 미디어 production/wip/RZLV
가정: 11/25 종가 0.8762 기준(11/26 휴장, 11/27 반일장 13:00 ET 전 작성 — 브리핑 규칙). 127회차 B(같은 날 정규 PLUG 126 잠정, STATE 순서).

## 끝난 것 (1단계: 조사·리포트·대본)
- 조사 research/: events.md(확정 사실·출처), prev_report.md(지난 예측 4개 모두 확인 전), prob_basis.md, macro.md, sec/(6-K 11/19 PDF·10/8 녹취 정정본·H1 MD&A)
- 리포트 report/rzlv-2026-11-2.md EASY_OK·CLOSE_OK, 그림 6장(figs/) → 사이트 worktree 커밋, bin/site_pub.sh 실행 중(로그 report/site_pub.log, test_build 약 40분)
- 대본 video/narration.txt 12.87KB GROUP_OK B(안내 p10), PRE_OK 13, midroll H2 p14(50%), slides.json(anim 17/27), 쇼츠 shorts/(SHORTS_OK)
- 썸네일 video/thumb/RZLV_thumbnail.jpg(V7 a), 메타 video/mk_meta.py(PLAIN_OK)·shorts/mk_meta.py, SNS sns/mk_queue.py(dry: cover 파일만 없음)
- 쿠팡 H2 mdlurzlv https://link.coupang.com/a/i0Y9Qhnl9g (review/product_links.json 커밋)
- bin/: after_tts.sh(합성), publish_loop.sh(wait_live→업로드→youtube_id→SNS→쇼츠→기록), record.py(기록), site_pub.sh

## 막힌 것
- 맥 TTS 118_kwa_rzlv1127_tts1 exit 2: 로그 "✗ ollama 서버가 응답하지 않음 (0시간 대기 후 포기)" — mac.py가 만드는 큐 스크립트가 tts 묶음에도 ollama를 요구, 새 인텔 맥에 ollama 없음. 117 PLUG도 같은 원인. mac.py 수정은 권한 거부 → 운영자 확인 필요(tts·fetch·shell만이면 ollama 줄 생략).
- 대신 클라우드 TTS(사이트 tools/tts/st_tts.py, 4코어) 07:11Z 시작 → video/tts_run.log(CLOUD_TTS_START/LONG_DONE/SHORTS_DONE/TTS_DONE)

## 남은 일
1. TTS_DONE 확인 → `bash /dev/shm/rzlv1127/bin/after_tts.sh` (백그라운드, after.log에 AFTER_CHAIN_OK) — slides_out/brand_intro·anim preview 눈 확인
2. 사이트 push 확인(report/site_pub.log SITE_PUSHED) → `bash bin/publish_loop.sh`(백그라운드, publish.log) — wait_live 뒤 업로드
3. 요청 완료 답글(UgyqG6ZkNhTM9-DIAWF4AaABAg, 150자, 영상·리포트 맨 주소) → requests.md 완료 + 답글 ID → 기록 커밋 → 정리(raw/redo wav·slides_out 삭제, worktree 제거, wip 삭제)
