# HANDOFF — LAES 11-26 정규 (laes1126, 125회차 B그룹) · 갱신 2026-11-26 09:35Z

## 상태: ③ 발행 단계 — 리포트 push 완료(origin/main 83ec937, 09:58Z). 다음은 남은 일 1의 llm_judge부터
- 선정: LAES★ — 11/25 10:02 ET 보도자료·16:57 6-K 유로넥스트 그로스 파리 2차 상장 승인(12/2 거래, 새 주식·판매·대금 없음) + 11/25 종가 1.07 +9.9%(나스닥 historical; 장중 저가 0.8809 -9.6%, 소식 뒤 90분 0.89~0.91, 정오부터 무리·QQQ와 함께 회복). PLUG·JOBY(11-24)·SLDP(11-25)는 72시간 안.
- 72시간: 지난 롱폼 zbq6gLjyeVI 11-24 02:18Z → upload_meta publish_at 2026-11-26T21:20-05:00(쇼츠 21:30). yt_api_upload가 비공개+publishAt로 올림.
- 회차 125 = B그룹(LEU가 124 A). 대본 11.41KB GROUP_OK B, 안내 p11(첫 번째 단서). 맥 TTS 115_kwa_laes1126_tts2(613.6초). 쇼츠 음성 112_kwa_laes1126_tts1.
- 앵글 N5 '반등 신호일까?'(angle_log 기록 완료). 영양제 H1 오메가3, 쿠팡 단축 https://link.coupang.com/a/iZkUIIHzEa (mdomlaes, product_links.json 캐시)
- 검사: EASY_OK · PRE_OK 13 · MIDROLL_OK(AD2, --date 2026-11-26) · ASR(asr_check.ok 사유 기록) · check_slides·still OK · AD_GAP_OK(--strict, 627초 중 광고 52.4초 8%) · video_check long OK(최장 정지 14초) · video_check shorts OK(2.5초) · PLAIN_OK · QUEUE dry OK(cover 파일만 남음)
- 산출물: video/LAES_slide_video.mp4 · video/thumb/LAES_thumbnail.jpg · shorts/LAES_shorts.mp4 · shorts/cover.jpg·cover_ig.jpg (slides_out·shorts_out은 /dev/shm/laes1126 — 재시작하면 사라짐, mp4는 디스크)
- 사이트 worktree /home/claude/site-reg1126: 리포트 커밋 2개(laes-2026-11-7 + 60일 협상 문장). `report/push_loop.sh`(rebase→test_build→build --strict→site_push, exit 3이면 최대 5회 반복) 실행 중 — 로그 report/site_pub.log, 한 회 약 40~45분

## 남은 일(순서)
1. push 확인(`git -C /home/claude/site-reg1126 fetch -q origin main && git -C /home/claude/site-reg1126 log origin/main --oneline | grep laes-2026-11-7`, 없으면 `bash /home/claude/laes1126/report/push_loop.sh` 다시) → `python3 tools/llm_judge.py laes-2026-11-7 --wait 10` 맞는 지적만 반영
2. `sh tools/wait_live.sh laes-2026-11-7` → `python3 video/mk_meta.py` → yt_api_upload.py 롱폼(video/) → `python3 shorts/mk_meta.py <롱폼ID>` → 쇼츠 업로드 → series_playlist·captions 확인
3. 썸네일 thumbnails.set 1회씩(롱폼 video/thumb/LAES_thumbnail.jpg, 쇼츠 shorts/cover.jpg) → 429면 review/thumb_backup/pending/<id>.jpg 복사 + thumb_history.json pending + 커밋(18:30Z 예약 재시도)
4. 사이트: 리포트 youtube_id + `KW_QUEUE=/home/claude/site-reg1126/social/queue python3 sns/mk_queue.py 2026-11-26T21:35:00-05:00` + static/social/laes-2026-11-7/(LAES_shorts.mp4·cover_ig.jpg) → queue_check → test_build·build --strict → site_push(반복)
5. 블로거(blogger-guide 2-1) · 기록: experiments(125 B, 시험 A 회차표 밖), ad_conv --add(H1, 광고 시작 약 376초), pred_ledger --extract·--score laes-2026-11-7, followups(11-27·12-02·12-09·12-15·12-17·12-24), improvements(네 지표·AI 느낌·토큰), sub_test(구독 문장 A 정체형), thumb_history, predictions/LAES.md 한 줄, STATE 완료
6. 정리: production/wip/LAES 지우기, worktree 제거, /dev/shm/laes1126 제거

## 막힌 것
- 디스크 / 여유 약 1GB(98%): 오래된 site-design·fx·seo·slides·sns·wk·x8 worktree(모두 origin/main에 포함·변경 없음, 약 6GB)와 /tmp/kws-* 삭제가 권한 거부 → 운영자 정리 필요. 렌더는 /dev/shm로 우회.
- site_push exit 3 반복(다른 세션의 LEU 리포트·social/queue·워크플로 변경 유입) — test_build 한 회 40분 넘음.
