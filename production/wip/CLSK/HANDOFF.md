# HANDOFF — CLSK 11-25 요청 1편 (clsk1125, 122회차 A그룹) · 2단계 갱신 2026-11-25 23:10Z

## 지금 상태: ③ 업로드·답글·기록 끝 → 사이트 push(youtube_id·SNS 대기열) 진행 중
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
- 사이트 0556efd: youtube_id(BruKjg6tsA0) 연결 + SNS 대기열 4건 push 완료
- 운영자 11-26 광고 분리 지시: 아직 안 나간 Threads 둘째 글(publish_at 11-25 22:04 ET = 11-26 03:04Z)의 💊 블록을 '— 광고 —' 구분선·빈 줄로 링크 목록과 떼고 쿠팡 파트너스 고지 한 번 넣음(QUEUE_OK). **site-clsk 로컬 커밋 b4262a3(origin/main 3abf976 위), 아직 push 안 됨** — 원격에 빌드 관련 변경이 계속 들어와 site_push.sh가 exit 3 → 재검사를 되풀이하다 백그라운드 시간 제한으로 끊김. 남은 일: `cd /home/claude/site-clsk && bash /home/claude/clsk1125/bin/site_pub.sh "재시도" social/queue/clsk-2026-11-th2.json`(test_build 약 35분) — 03:04Z 전에 못 올라가면 둘째 글은 옛 형식(💊 자기 문단, 가이드 링크)으로 게시됨(공개 뒤에는 고치지 않음).
  - 직접 상품 링크: health/catalog.json `best`가 비어 있고, probiotics 후보 이름에 '비피더스균 락티스'가 확인되는 상품이 없어 가이드 링크 유지(검증 안 된 상품 링크를 넣지 않음). 롱폼·쇼츠 설명란·고정댓글은 이미 공개 → 손대지 않음. 영상 합성도 끝나 광고 앞뒤 쉼은 다음 회차부터.
- 그 뒤 정리: `cd /home/user/kimworld-media && git rm -rq production/wip/CLSK && git -c user.name=phdkimworld commit -m "CLSK wip 정리" && git push origin HEAD:claude/kim-world-stock-studio-laes-ovy09b`, `git -C /home/user/kimworld-site worktree remove --force /home/claude/site-clsk`

## 재시작 복구
- 작업 폴더가 없으면 `bash tools/wip_restore.sh CLSK` → 중계에서 raw.flac·raw_timing.json 다시 받기(`python3 /home/user/kimworld-relay/tools/mac.py get 111_kwa_clsk1125_tts1 raw.flac <video>/raw.flac` 등) → wav 변환 → `bin/swap_p9p10.py` → 문단별 분할 후 st_redo 4·5·20 → after_tts.sh

## 막힌 것
- BLS CPI·고용 일정 403 — '확인 안 됨'
- thumbnails.set 한도(11-25 18:30Z 이동 창) — 새 회차 썸네일은 한 번만 시도, 429면 pending(11-26 18:30Z 예약 재시도)
