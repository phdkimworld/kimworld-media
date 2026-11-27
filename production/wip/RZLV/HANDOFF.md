# HANDOFF — RZLV 11-27 요청 후속편 (rzlv1127, 127회차 B그룹 잠정) · 갱신 2026-11-27 08:05Z

작업 폴더 /dev/shm/rzlv1127 (= /home/claude/rzlv1127) · 사이트 worktree /dev/shm/site-rzlv · wip: 미디어 production/wip/RZLV
가정: 11/25 종가 0.8762 기준(11/26 휴장, 11/27 반일장 마감 전 작성 — 브리핑 규칙). 127회차 B(같은 날 정규 PLUG 126 잠정, STATE 순서).

## 상태: 리포트 LIVE · 녹음 끝 · 합성 전 ASR 검사 2번 실패로 멈춤
- 리포트 https://drkimworld.com/r/rzlv-2026-11-2/ LIVE(wait_live) · 사이트 main deb8118(site_pub: 1차 exit 3 PLUG 리포트 유입 → pull·test_build 1회 → PUSHED)
- TTS(맥 실패 → 클라우드 st_tts 4코어): 롱폼 07:10:56→07:30:07Z = 19분 11초(음성 682.5초), 쇼츠 1분 6초
- 검사 통과: EASY_OK · CLOSE_OK · GROUP_OK B 12.87KB · PRE_OK 13 · MIDROLL_OK p14 50% · PREV_CALLS_OK · PLAIN_OK · TTS_FRESH_OK · DEBREATH_OK · SHORTS_OK · AUDIO_OK

## 멈춘 이유(규칙 3: 같은 단계 2번 실패)
- 1차 chain.log: `ASR_MISS 문단 1: 일억 사백만 | 들린 말: … 뭘로대출이약 1억 40만달러이고 …` → 원인: '일억 사백만' 뭉갬 → 고침 하나: p1을 '먼로 대출 잔액이 일억 달러가 넘고'로, st_redo 1(임시 폴더 /tmp/tmphkwoj13e), 슬라이드 big '1억 달러 넘음'
- 2차 chain.log: `ASR_MISS 문단 1: 일억 | 들린 말: … 뭘로대출자네기록달러가넘고 …` · `ASR_MISS 문단 17: 이십사 | 들린 말: … 그뒤 20 사거리일제를보면 …`
- 가설: p1은 '잔액이 일억'이 붙어 읽힘(받침 연음) → '먼로 대출이 일억 달러를 넘고'처럼 '잔액이'를 빼고 st_redo 1. p17 '이십사 거래일째'는 1차에서 통과한 같은 녹음이라 ASR 흔들림일 가능성 → 들어 보고 괜찮으면 video/asr_check.ok(CLSK 11-25 선례), 아니면 '스물네 거래일'로 st_redo 17.

## 남은 일(순서)
1. 위 p1(·p17) 처리 → `bash /dev/shm/rzlv1127/bin/after_tts.sh`(백그라운드, after.log AFTER_CHAIN_OK) → slides_out/brand_intro·anim preview·product 카드 눈 확인
2. `bash bin/publish_loop.sh`(백그라운드, publish.log): 업로드(썸네일 한 번, 429면 record.py가 pending) → youtube_id → SNS 대기열(sns/mk_queue.py, T20·self_reply) → 쇼츠 → 기록(record.py: STATE·experiments 127·improvements·sub_test·followups 12-31·RZLV.md·sector_map·ad_conv H2)
3. 완료 답글 UgyqG6ZkNhTM9-DIAWF4AaABAg(150자 이내, 영상·리포트 맨 주소, 권유 없음) `yt_reply.py --reply … --kind request` → requests.md RZLV 행 '완료(rzlv-2026-11-2, <ID>)' + 답글 ID
4. 정리: raw.wav·redo·slides_out 삭제, `git -C /home/user/kimworld-site worktree remove --force /dev/shm/site-rzlv`, production/wip/RZLV 삭제
- 선택: `python3 tools/llm_judge.py rzlv-2026-11-2 --wait 10` 지적 반영

## 막힌 것(운영자 확인 필요)
- 맥 TTS 117(PLUG)·118(RZLV) exit 2: `✗ ollama 서버가 응답하지 않음 (0시간 대기 후 포기)` — tools/mac.py가 tts 묶음에도 ollama 확인 줄을 넣음, 새 인텔 맥에 ollama 없음. mac.py 수정(tts·fetch·shell만이면 ollama 줄 생략)은 권한 거부.
