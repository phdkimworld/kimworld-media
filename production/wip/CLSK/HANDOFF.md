# HANDOFF — CLSK 11-25 요청 1편 (clsk1125, 122회차 A그룹) · 2단계 갱신 2026-11-25 23:10Z

## 지금 상태: ② 리포트 발행·녹음 끝 → 합성(chain_long) 진행 중
- 11/25 종가 **5.18**(+1.3%): 야후 regularMarketPrice(21:00:02Z) = 나스닥 info 'Closed at 4:00 PM' 5.18, 1분봉 15:59 5.17·16:00 뒤 5.23(시간외). historical 11/25 행은 16:12 ET에 없음. 칸 = 4.89~5.63(갈래 2). 같은 무리 QQQ 633.93·IREN 12.85·APLD 12.29·CORZ 10.82(표엔 안 넣음). EDGAR 11/24 3건 뒤 새 제출 없음 → research/events.md 6절
- 매매 질문 H1 그대로(11/25 > 4.60이라 E8 조건 아님). 제목 `클린스파크(CLSK) 지금 팔아야 될까? 실적 다음 날 5.18달러, 같은 날 판매 창구를 열었다 #CLSK` ANGLE_TITLE_OK
- 리포트 https://drkimworld.com/r/clsk-2026-11/ — 사이트 main 4601090(모델 심사 10개 중 맞는 지적 반영: 내부 용어·공시 표현·22억 7,600만 통일·위험 문단). EASY_OK·CLOSE_OK. 사이트 worktree /home/claude/site-clsk
- 대본 9.50KB GROUP_OK A(안내 p10 — 안내 문단을 공사비 문단 뒤로 옮김, ADMID), PRE_OK 13, 맥 TTS 111_kwa_clsk1125_tts1(510초) → 소리에서 9·10문단 맞바꿈(bin/swap_p9p10.py), st_redo 문단 20·5·4 → ASR_OK(asr_check2.log), 남은 문단 4 '팔' 인식 한계는 video/asr_check.ok, TTS_FRESH_OK, check_slides OK(anim 15/25, 본문 65%)
- 영양제 H3 289초(57%), 안내 185·194초(36~38%), 구독 문장 B(p19)
- 썸네일 video/thumb/CLSK_thumbnail.jpg(V7 a, BIZ_OK·NAME_OK·FIT_OK) · 쇼츠 7장면 SHORTS_OK(음성 맥) · SNS sns/mk_queue.py(queue_dry OK) · 메타 video/mk_meta.py·shorts/mk_meta.py · bin/record.py(기록)·bin/publish_loop.sh

## 완료 (2026-11-26 00:30Z)
- 롱폼 **BruKjg6tsA0**(공개·첫 댓글·한국어 자막·재생목록) · 쇼츠 **VyvLuKKhd38**(공개·첫 댓글·자막) — 둘 다 썸네일 429 → review/thumb_backup/pending/<ID>.jpg + thumb_history pending(media 42e58a7·15fc840)
- 검사: GROUP_OK A · PRE_OK 13 · EASY_OK · CLOSE_OK · num_check OK · prev_calls OK · ASR(재녹음 4·5·20 + asr_check.ok) · check_slides OK · still OK · video_check long(최장 정지 15초)·shorts(3.0초) · ad_gap_check --strict AD_GAP_OK · MIDROLL_OK(58%) · PLAIN_OK · QUEUE_OK · COVER_OK · hero_check 도구 없음(접촉 시트 눈 확인)
- 요청 완료 답글 UgxJ7XlKj9zWiD-RZa94AaABAg.AdcTTVtXl3nAdeHH6CrHaL(150자, 링크 포함) · requests.md 완료(media 42e58a7)
- 기록 media d28f6b6: STATE·experiments 122·thumb_history·improvements·sub_test(B 393초)·followups(12-02·12-23)·ad_log H3 290초·angle_log H1·ledger·predictions/CLSK.md·sector_map CLSK·filings S-3ASR

## 진행 중 (마지막)
- 사이트 push: worktree /home/claude/site-clsk 로컬 커밋 2개(youtube_id 연결 38caeca + SNS 대기열 4건 static/social/clsk-2026-11·social/queue/clsk-2026-11*.json)를 `bin/site_pub.sh`가 test_build·build --strict 뒤 site_push.sh 중 → report/site_pub3.log 끝 SITE_PUSHED 확인
  - 끊겼으면: `cd /home/claude/site-clsk && bash /home/claude/clsk1125/bin/site_pub.sh "SNS 대기열·youtube_id" social/queue` (커밋 없음이면 그대로 테스트·push). worktree가 사라졌으면 새 worktree에서 youtube_id: "BruKjg6tsA0" 넣고, `KW_QUEUE=<worktree>/social/queue python3 sns/mk_queue.py <ET 지금>` + static/social/clsk-2026-11/(CLSK_shorts.mp4·cover.jpg·cover_ig.jpg는 shorts/ 또는 wip) → queue_check → push
- 그 뒤 정리: `cd /home/user/kimworld-media && git rm -rq production/wip/CLSK && git -c user.name=phdkimworld commit -m "CLSK wip 정리" && git push origin HEAD:claude/kim-world-stock-studio-laes-ovy09b`, `git -C /home/user/kimworld-site worktree remove --force /home/claude/site-clsk`

## 재시작 복구
- 작업 폴더가 없으면 `bash tools/wip_restore.sh CLSK` → 중계에서 raw.flac·raw_timing.json 다시 받기(`python3 /home/user/kimworld-relay/tools/mac.py get 111_kwa_clsk1125_tts1 raw.flac <video>/raw.flac` 등) → wav 변환 → `bin/swap_p9p10.py` → 문단별 분할 후 st_redo 4·5·20 → after_tts.sh

## 막힌 것
- BLS CPI·고용 일정 403 — '확인 안 됨'
- thumbnails.set 한도(11-25 18:30Z 이동 창) — 새 회차 썸네일은 한 번만 시도, 429면 pending(11-26 18:30Z 예약 재시도)
