# HANDOFF — LEU 11-26 요청편 (leu1126, 124회차 A그룹)
작업 폴더 실제 위치: /dev/shm/leu1126_w (symlink /home/claude/leu1126) · 사이트 worktree /dev/shm/site-leu1126 (symlink /home/claude/site-leu1126) — 디스크 / 가 99%라 shm 사용

## 확정
- 기준 11/25 확정 종가 83.19(-1.0%, 나스닥 historical 11/25 행). 11/26 추수감사절 휴장
- 매매 질문 H8 '오래 들고 가도 될까'(angle_pick 1순위, --event 계약,실적후,최저)
- 리포트 leu-2026-11 사이트 main 771ac47(첫 발행) + 모델 심사 반영본 site_pub2(진행/완료 확인: report/site_pub2.log)
- 대본 9.6KB GROUP_OK A, PRE_OK 13, 맥 TTS 114_kwa_leu1126_tts1(525초) — raw.wav·shorts_raw.wav 받음
- 영양제 H1 오메가3, 쿠팡 단축 링크 https://link.coupang.com/a/iZktLrbsoS (mdomleu, product_link --set 완료), kind ad, midroll_check --date 2026-11-26 AD2 OK
- 썸네일 video/thumb/LEU_thumbnail.jpg(V7 a), SNS sns/mk_queue.py(queue_dry OK), 메타 video/mk_meta.py·shorts/mk_meta.py, 기록 bin/record.py(인자: 롱폼ID 쇼츠ID 124)

## 남은 일
1. bin/after_tts.sh(백그라운드) → video/chain.log CHAIN_DONE 확인(TMPDIR=/dev/shm/leu_tmp). 실패 시 asr_check.log·check_slides.log 확인
2. ad_gap_check --strict, video_check long·shorts 확인
3. bin/publish_loop.sh(백그라운드): wait_live → 롱폼 업로드(썸네일 1회, 429면 record.py가 pending 처리) → youtube_id 연결 → SNS 대기열 → 쇼츠 → record.py → media push
4. 완료 답글: python3 tools/yt_reply.py --reply Ugz-xDC0xZhlf97Rwbp4AaABAg --text-file /home/claude/leu1126/reply.txt --kind request → requests.md 49행 완료(leu-2026-11, 영상ID) + 답글 ID
5. 정리: production/wip/LEU 삭제 커밋, git -C /home/user/kimworld-site worktree remove --force /dev/shm/site-leu1126, rm symlinks
