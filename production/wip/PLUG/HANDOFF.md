# HANDOFF — PLUG 11-27 정규 (plug1127, 126회차 A그룹) · 갱신 2026-11-27 09:35Z

## 상태: 영상 공개 완료, 사이트 2차 push만 대기(사용자 확인 필요)
- 리포트 LIVE https://drkimworld.com/r/plug-2026-11-6/ (HTTP 200, 4ee6c14) · 모델 심사 9개 중 맞는 지적 반영본은 아래 미푸시 커밋에 있음
- 롱폼 0OAr1e2zr8s 공개·썸네일 ok·첫 댓글·자막 148큐·재생목록 '플러그 파워 미스터리 추적'
- 쇼츠 aoY2i9aHBc8 공개·첫 댓글·자막 · 썸네일 429 → review/thumb_backup/pending/aoY2i9aHBc8.jpg, send_later trig_01HCa7z4wfn9bG6hvs6fuMT1(11-28 08:50Z)
- 미디어 기록 커밋 2cd621a(STATE·selection·experiments·improvements·ad_log·angle_log H6·sub_test·followups·thumb_history·ebook)

## 막힌 것 (사용자 확인 필요)
1. 사이트 worktree /dev/shm/site-plug1127 미푸시 커밋 2개: 90f6334(youtube_id + 심사 반영) · 11a61c8(SNS 대기열 4건 + static/social/plug-2026-11-6)
   - site_push exit 3 두 번: 1회 build.py(원격 7b510d1), 2회 content/reports/rzlv-2026-11-2.md(RZLV 에이전트) → 규칙 4대로 반복 중단
   - 잇는 법: cd /dev/shm/site-plug1127 && git pull --rebase origin main && python3 tests/test_build.py && python3 build.py --strict && rm -rf dist && bash /home/user/kimworld-media/tools/site_push.sh
   - Threads 둘째 글 publish_at 04:40 ET가 지났으면 push 전에 scripts/social_publish.py --next-slot 다시 → python3 /dev/shm/plug1127/sns/mk_queue.py <지금 ET> <slot> → queue_check
2. 맥 TTS 117·118 exit 2: 로그 "✗ ollama 서버가 응답하지 않음" — relay tools/mac.py가 모든 묶음에 Ollama 확인을 넣는데 새 인텔 맥엔 Ollama 없음. mac.py 수정은 권한 거부 → 클라우드 TTS로 대체(16분 15초)

## 남은 일 (push 뒤)
- 블로거 blogger.yml slug=plug-2026-11-6 (blogger-guide 2-1·2-4)
- pred_ledger --extract '새 0'(로컬 사이트 체크아웃 미갱신 추정) → 사이트 반영 뒤 다시
- 정리: production/wip/PLUG, worktree /dev/shm/site-plug1127, /dev/shm/plug1127
