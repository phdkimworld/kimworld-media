# HANDOFF — PLUG 11-27 정규 (plug1127, 126회차 A그룹) · 갱신 2026-11-27

## 상태
- 선정·STATE·selection 커밋 cdf5050(미디어). 리포트 report/plug-2026-11-6.md EASY_OK, 그림 6장(figs/) → bin/site_pub.sh(로그 report/site_pub.log)
- 대본 video/narration.txt 9.08KB GROUP_OK A · slides.json(mk_slides.py) · 쇼츠 shorts/ · PRE_OK 14개 · 썸네일 video/thumb/PLUG_thumbnail.jpg(make_v7 a) · 메타 mk_meta.py(롱폼·쇼츠) · SNS sns/mk_queue.py(T20) · H2 카드 kit/h2_card.png · 쿠팡 mdluplug https://link.coupang.com/a/i0Y2a9ZczY
- 맥 TTS 117_kwa_plug1127_tts1 제출(video/tts_start 시각) → bin/tts_mac.sh 대기(로그 video/tts_run.log)
- 확정 숫자 원천: research/PLUG_long.json(나스닥 historical 11/25 1.065), research/*_5m.json(야후 5분봉), research/macro.md, research/base.py, research/prob_basis.md
- 가정: 126회차 A그룹(근거: 직전 125 B, 같은 날 RZLV 대본 12.9KB = B → 127)

## 남은 일
1. TTS_DONE 뒤 `bash bin/after_tts.sh`(chain_long → video_check·plain_check, 로그 video/after.log, chain video/chain.log)
2. `bash bin/publish_loop.sh`(wait_live → 롱폼 업로드·썸네일(429면 pending) → youtube_id push → SNS 대기열 → 쇼츠 → 기록 record.py)
3. llm_judge plug-2026-11-6 지적 반영 · 블로거(blogger.yml slug) · 정리(production/wip/PLUG, worktree /dev/shm/site-plug1127, /dev/shm/plug1127)
