# HANDOFF — CLSK 11-25 요청 1편 (clsk1125, 122회차 A그룹) · 2단계 갱신 2026-11-25 23:10Z

## 지금 상태: ② 리포트 발행·녹음 끝 → 합성(chain_long) 진행 중
- 11/25 종가 **5.18**(+1.3%): 야후 regularMarketPrice(21:00:02Z) = 나스닥 info 'Closed at 4:00 PM' 5.18, 1분봉 15:59 5.17·16:00 뒤 5.23(시간외). historical 11/25 행은 16:12 ET에 없음. 칸 = 4.89~5.63(갈래 2). 같은 무리 QQQ 633.93·IREN 12.85·APLD 12.29·CORZ 10.82(표엔 안 넣음). EDGAR 11/24 3건 뒤 새 제출 없음 → research/events.md 6절
- 매매 질문 H1 그대로(11/25 > 4.60이라 E8 조건 아님). 제목 `클린스파크(CLSK) 지금 팔아야 될까? 실적 다음 날 5.18달러, 같은 날 판매 창구를 열었다 #CLSK` ANGLE_TITLE_OK
- 리포트 https://drkimworld.com/r/clsk-2026-11/ — 사이트 main 4601090(모델 심사 10개 중 맞는 지적 반영: 내부 용어·공시 표현·22억 7,600만 통일·위험 문단). EASY_OK·CLOSE_OK. 사이트 worktree /home/claude/site-clsk
- 대본 9.50KB GROUP_OK A(안내 p10 — 안내 문단을 공사비 문단 뒤로 옮김, ADMID), PRE_OK 13, 맥 TTS 111_kwa_clsk1125_tts1(510초) → 소리에서 9·10문단 맞바꿈(bin/swap_p9p10.py), st_redo 문단 20·5·4 → ASR_OK(asr_check2.log), 남은 문단 4 '팔' 인식 한계는 video/asr_check.ok, TTS_FRESH_OK, check_slides OK(anim 15/25, 본문 65%)
- 영양제 H3 289초(57%), 안내 185·194초(36~38%), 구독 문장 B(p19)
- 썸네일 video/thumb/CLSK_thumbnail.jpg(V7 a, BIZ_OK·NAME_OK·FIT_OK) · 쇼츠 7장면 SHORTS_OK(음성 맥) · SNS sns/mk_queue.py(queue_dry OK) · 메타 video/mk_meta.py·shorts/mk_meta.py · bin/record.py(기록)·bin/publish_loop.sh

## 진행 중
- `bash bin/after_tts.sh` → video/after.log 끝에 AFTER_CHAIN_OK(chain_long: debreath·검사·합성·쇼츠·plain_check). 실패면 `tail video/chain.log`

## 남은 일 (AFTER_CHAIN_OK 뒤)
1. 확인: slides_out/brand_intro 프레임, chain.log의 video_check long/shorts·ad_gap_check --strict·midroll_check·hero_check
2. `bash bin/publish_loop.sh`(백그라운드): wait_live → 롱폼 업로드(썸네일 한 번만, 429면 record.py가 review/thumb_backup/pending/<ID>.jpg + thumb_history pending) → youtube_id 연결 push → SNS 대기열(queue_check) → 쇼츠 업로드 → angle_log H1·pred_ledger·record.py·media 커밋
3. 요청 완료 답글(150자, 링크 포함): `python3 tools/yt_reply.py --reply UgxJ7XlKj9zWiD-RZa94AaABAg --text-file <f> --kind request` 본문:
   `@이준호-c3o 요청하신 클린스파크 영상과 리포트를 올렸습니다. 전환 진행은 리포트 끝 '데이터센터 전환 진행' 표에 있어요. 텍사스도 궁금하세요?` + 줄바꿈 `https://youtu.be/<ID>` + 줄바꿈 `https://drkimworld.com/r/clsk-2026-11/`
   → requests.md CLSK 행 '완료(clsk-2026-11, <ID>)' + 결과 칸 '완료 답글 <답글ID>(11-25)' (앞 행과 '||'로 붙은 줄은 줄바꿈으로 고침)
4. 정리: `git rm -r production/wip/CLSK` 커밋, `git -C /home/user/kimworld-site worktree remove --force /home/claude/site-clsk`

## 재시작 복구
- 작업 폴더가 없으면 `bash tools/wip_restore.sh CLSK` → 중계에서 raw.flac·raw_timing.json 다시 받기(`python3 /home/user/kimworld-relay/tools/mac.py get 111_kwa_clsk1125_tts1 raw.flac <video>/raw.flac` 등) → wav 변환 → `bin/swap_p9p10.py` → 문단별 분할 후 st_redo 4·5·20 → after_tts.sh

## 막힌 것
- BLS CPI·고용 일정 403 — '확인 안 됨'
- thumbnails.set 한도(11-25 18:30Z 이동 창) — 새 회차 썸네일은 한 번만 시도, 429면 pending(11-26 18:30Z 예약 재시도)
