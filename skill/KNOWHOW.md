# 김박사 월드 제작 노하우 지도 (2026-11-20 운영자 "컨텐츠 제작과 관련된 모든 노하우에 접근할수 있는 지침 작성")

이 문서는 **노하우가 어디에 있는지**를 알려 주는 색인이다. 규칙 자체는 각 원문에 있다. 새 세션·에이전트는 이 문서를 먼저 읽고, 맡은 일에 해당하는 줄의 문서만 골라 읽는다(토큰 절약). 원문끼리 다르면 **검사 도구가 강제하는 쪽(SKILL.md + tools/*_check) → 최신 운영자 지시(날짜가 늦은 쪽)** 순서로 따른다.

저장소 두 곳:
- 미디어 `phdkimworld/kimworld-media` (브랜치 `claude/kim-world-stock-studio-laes-ovy09b`) — 지침·도구·기록·예측 장부·이북 재료. 로컬 `/home/user/kimworld-media`
- 사이트 `phdkimworld/kimworld-site` (main, push = 배포) — 리포트·SNS 대기열·워크플로·영상/썸네일 키트. 로컬 `/home/user/kimworld-site`. 사이트 규칙 최종 기준은 그 저장소 `AGENTS.md`
- 비공개 통계 `phdkimworld/kimworld` ops-data 브랜치 → `/home/claude/kimworld-ops`(tools/report_perf.py가 자동으로 받음)

## 1. 먼저 읽을 것 (모든 작업 공통, 5분)
| 문서 | 담긴 것 |
|---|---|
| `skill/SKILL.md` 앞부분(채널 정체성·0장·0.2) | 통섭 마스터마인드 정체성, 자산별 극대화 지표(제목·썸네일 CTR, 설명·고정댓글 전환, 대본·리포트 체류), 가독성 원칙 |
| `skill/SKILL.md` 5장 | 공통 금지 표현(투자 권유·수익 암시·긴급성·보유 여부·AI 언급·회원 가입·베팅) |
| `review/predictions/README.md` 맨 위 "핵심 통찰 6" | 예측이 틀리는 이유와 고정 규칙(기저율 출발, 유력 갈래 ≤40%, 사건/반응 분리, 악재 처음 알려진 날) |
| `review/insights.md` 맨 끝 두 절 | 가장 최근 채널 통찰(지금 무엇이 먹히는가) |

## 2. 작업별로 읽을 곳
| 하려는 일 | 읽을 문서(절) | 강제하는 도구 |
|---|---|---|
| **오늘 무엇을 만들까(선정)** | `skill/runbooks/production.md` R1′(핵심 후속편·두 층·탐색 종목·72시간), `review/core_tickers.md`(★ 매일 갱신), `review/selection.md`(지난 판단), `review/requests.md`(시청자 요청) | `tools/prod_check.py`, `core_weekly.py --apply`, `trending.py`(후보 찾기만), `request_rank.py`, `unified_rank.py` |
| 조사 | SKILL 3장(출처 규칙·병렬 조사·숫자 단일 원천 3.5·직전 리포트 잇기 3.4.1·**시장·거시·정책 층 3.6**), MASTER_SOP 1장(수급 세 지표·용어 병기), `review/sector_map.md`(티커 → 업종 ETF·정책 검색어), `review/macro_ctx_sample.md`(SLDP 시험) | `tdays.py`(거래일), `verified_table.py`, `biz_digest.py`, `macro_ctx.py`(시황·금리·달러·유가·VIX·평소 민감도로 예상 vs 실제·다음 FOMC/PCE/CPI·10-K 정책 키워드 → research/macro.md), `macro_check.py`(리포트·대본·쇼츠·Threads 거시 층, 11-23~) |
| 예측·시나리오 | `review/predictions/README.md` + `<티커>.md`, SKILL 3.4.1·R3 5.6 | `pred_ledger.py --judge --report --ticker T`, `prev_calls_check.py`(prob_basis.md 기저율·틀린다면), `prev_score_sync_check.py` |
| 사이트 리포트 | SKILL R장(R0.1 이야기형, R1.5 쓰면서 멈칫할 곳 없애기, 그림 4~6개), production.md ⑧, 사이트 `AGENTS.md` | `easy_check.py`(EASY_OK), `chart_check.py`, `llm_judge.py`, 사이트 `tests/test_build.py`·`build.py --strict`, push는 `tools/site_push.sh` |
| 롱폼 대본 | SKILL V장(V1~V3 훅·열린 고리·재훅, V2.x 숫자 읽기), MASTER_SOP v2.8, `skill/VIDEO_GUIDE_v1.md` | `group_check.py`, `num_speak_check.py`, `josa_check.py`, `krw_unit_check.py`, `close_check.py`, `ai_feel_check.py`, `pre_tts_check.sh` |
| 녹음(TTS) | SKILL V6.3, production.md(맥 중계 kwrt) | `tts_asr_check.py`, `tts_fresh_check.py`, `debreath.py`, `script_audio_check.py`, `st_redo.py` |
| 슬라이드·애니메이션·합성 | SKILL V6.4~V6.7(효과음), VIDEO_GUIDE_v1, `skill/runbooks/taste.md`(AI 티 점검), 사이트 `tools/slidekit/`(slide.html·make_slide_video.py·anim 틀 v_*) | `slides_pre_check.py`, `taste_check.py`, `still_check.py`, `video_check.py`, `chain_long.sh`(TTS 뒤 자동 연결) |
| 브랜드 인트로·엔드카드(롱폼 0초 2.4초 인트로 + 회차 질문 한 줄·outro 홍보 칸, 쇼츠 끝 워드마크) | SKILL V6.7 '브랜드 인트로·엔드카드', 사이트 `tools/slidekit/brand.py`·`brand/`(intro.mp4·endcard.html), `review/experiments.md` 채널 시험(0~5초 유지율 판정) | check_slides BRAND·OUTRO_PROMO, `brand_shift.py`(챕터), video_check(챕터 밀림) |
| 썸네일·사이트 디자인 | SKILL V5(**V5.7 원리판 = 현행**, V5.0 사업 시각화·시안 3장), `review/design_study.md`(대형 채널·금융 사이트에서 배운 원리 표, 11-24), `skill/runbooks/taste.md` 4절, 미디어 `thumb_history.json`, 사이트 `tools/thumbkit/`(make_v7.py) | `thumb_biz_check.py`, `thumb_name_check.py`, `thumb_overflow_check.py` |
| **매매 질문 고르기(앵글, 11-22)** — 지금 사도 될까·팔아야 될까·버틸까·물타기·실적 전/뒤 등 47개, 회차마다 회전 | `skill/runbooks/angles.md`(처지별 묶음·제목 틀·답 뼈대·금지 변형), production.md '앵글 선회' 줄, SKILL V4 00번·R2, `review/angle_log.md`(사용 기록), `review/experiments.md` Q1 | `angle_pick.py <T> --event …`(후보 3개)·`--add`·`--check`(video_check long 안), 사이트 slidekit `brand.py` 인트로 질문 줄 |
| 제목·설명·고정댓글 | SKILL V4(제목 A/B 시험 R3·설명 링크 6개 상한), K2(고정댓글 첫 세 줄), V3.9-M(김박사 몰), F9(구독 문장), 성적표 줄 | `plain_check.py`, `ab_group_check.py`, `shop_sync_check.py`, `upload_guard.py` |
| 광고 자리 늘리기·UX 한도 | `review/ads_max.md`(노출면 감사·한도·운영자 할 일), `review/ads_max_slidekit_todo.md`(slidekit 대기안), `skill/runbooks/ads_access.md` 5.5 | `ad_gap_check.py`(롱폼 간격·총량·미드롤 권장 시각), 사이트 `build.py` AD_GAP_CHARS·`ops_digest.py` 광고 UX 가드 |
| 영양제 중간광고 | `skill/runbooks/health_midroll.md`·`skill/runbooks/marketing.md`(설득 기법·대본 틀·A/B, 근거: 비공개 phdkimworld/healthworld-ops `research/`, 사이트 `health/health.yaml`, 법: `skill/health/HEALTH_CHANNEL.md` 2장) | `midroll_check.py`(네 문장·광고 문단 quote 금지·banned·drop_words·거짓 긴급성·지어낸 후기, pre_tts_check 편입), `plain_check.py`, `taste_check.py` |
| 업로드·자막 | SKILL V7(V7.A API 업로드), production.md 흐름 줄 | `yt_api_upload.py`(업로드 뒤 `yt_captions.py` 한국어 자막 자동), `wait_live.sh`(리포트 열림 확인) |
| 쇼츠 | SKILL K9(0초 표지 완성), 사이트 `tools/shorts/` | `shorts_check.py` |
| Threads·인스타·페이스북·카드뉴스 | SKILL K8·K9.1, `skill/runbooks/taste.md` 8·9절, `skill/instagram/INSTAGRAM.md`, production.md 흐름(11-20: 인스타·페북 릴스만, Threads 2글) | `queue_check.py`, `queue_dry.py`, `poll_sync_check.py` |
| 블로거 | 사이트 `docs/blogger-guide.md`, production.md 0장 | 사이트 blogger.yml |
| **영상 안 화면 디자인(11-24)** — 슬라이드·anim·쇼츠 색 체계(상자 없음·강조색 하나·큰 글자는 숫자만·브랜드 위 오른쪽) | `review/slide_design_study.md`(대형 채널 90프레임·전/후), SKILL V6.4 '화면 디자인 체계'·V6.5 디자인 토큰, `skill/runbooks/taste.md` 5절, `review/experiments.md` V1 | 사이트 `tools/slidekit/slide.html`·`templates/anim/lib/kit.css`, check_slides·taste_check |
| **SNS 디자인(11-24)** — Threads 첫 줄·문단, 릴스 격자 표지, 체험 릴스 끔, 텔레그램 버튼, 블로거 머리·버튼 | `review/sns_design_study.md`(채널별 패턴·근거·전/후), SKILL K8.4, `review/experiments.md` S1 | `queue_check.py` [S1], 사이트 `tools/shorts/reel_cover.py`, `scripts/telegram_post.py`·`blogger_post.py` |
| 검색 노출(SEO) 점검·서치 콘솔 할 일 | `skill/runbooks/seo.md`(기술 SEO·메타·구조화 데이터·CWV·내부 링크·네이버/구글 메뉴, ECC skills/seo 참고), `review/seo_audit.md`(11-24 감사), 사이트 `AGENTS.md` 검색 노출 줄 | 사이트 `build.py` `seo_audit()`(빌드마다, --strict), `tests/test_build.py` 13절 |
| 댓글 답글 | `skill/runbooks/comments.md`(투표·요청·대댓글·스팸·23시 점검), `skill/runbooks/api.md`(AI 답글 크레딧) | `tools/hourly.py`, `yt_reply.py`, `site_comments.py` |
| 회차 후 복기·개선 | SKILL 8장(8.0 개선 하나 이상·통합 인사이트·AI 느낌 제거·토큰 절약), `review/improvements.md`, `review/experiments.md`, `review/learning.md`, `review/report_learning.md` | `insights.py`, `report_perf.py`, `theme_perf.py`, `episode_check.py` |
| 통계 보기 | 사이트 `docs/analytics-guide.md`, `stats_snapshots.jsonl`(3시간마다), `review/sub_test.md`(구독 시험). 분석 자료는 사이트 yt-analytics.yml → ops stats/yt_analytics.json(새 키, 컨테이너 키와 무관) | `yt_stats.py`, `yt_subs.py`, `insights.py`, `traffic_cut.py`, `yt_analytics_read.py` |
| 이북 재료 | `ebook/WRITING_GUIDE.md`·`TOC_DRAFT.md`·`ASSETS.md`, `ebook/materials/` | `ebook_materials.py --add/--sync/--status` |

## 3. 운영·접근 (키·권한·막힐 때)
| 문서 | 담긴 것 |
|---|---|
| `skill/runbooks/channel_access.md` | 유튜브·Threads·인스타·페이스북·블로거·텔레그램 키 위치, 재발급, 사이트로 키 옮기기(yt-secrets-sync.yml), GH_SECRETS_PAT |
| `skill/runbooks/ads_access.md` | 쿠팡·김박사 몰·애드핏·애드센스·유료 표시 |
| `skill/health/HEALTH_CHANNEL.md` | **김박사 건강월드**(영양제 유튜브, 채널 UCNh9…)·김박사 건강몰(health.drkimworld.com) 원문 지침: 정체성·키(`HEALTH_YT_*`, 본 채널 키와 분리·채널 ID 확인)·식품표시광고법 가드레일·기둥·퍼널·측정 |
| `skill/runbooks/api.md` | API 크레딧(사이트 워크플로로만 사용) |
| `skill/runbooks/production.md` 지연 금지·재시작 복구 | 컨테이너 재시작·에이전트 이어 가기, 디스크 정리, 업로드 한도 초과 대처 |
| `review/pending_feedback.md`, `review/followups.md` | 운영자 피드백 처리 상태, 날짜가 정해진 판정 일정 |
| 사이트 `docs/ops-log.md` | 사이트 운영 기록 |

## 4. 지금 살아 있는 핵심 결정 (요약 — 원문이 우선)
- **광고·판매의 철학(11-24 최상위): 수요와 공급을 잇는다** — 어떤 조건·상황의 사람에게 어떤 조건·특성의 제품이 맞는지를 딥 리서치와 논리·감성 설득으로. 모든 광고 문단·설명란·고정댓글·SNS·몰 줄·건강 채널이 "누구 → 제품 조건 → 왜 → 행동"을 갖춘다(health_midroll.md 0절, HEALTH_CHANNEL.md 0.1).
- **광고 구분 + 제품 직접 링크(11-26 운영자 "광고는 시각적으로나 호흡으로나 딱 구분되는게 더 이목을 끌거 같아. 링크는 이제 몰이 아니라 제품 링크를 바로 달기로 했어.")** — 💊 링크는 조건 맞는 쿠팡 제품(`tools/product_link.py`, 하위 ID md<성분><티커>), 구분선·빈 줄로 뗀 💊 구역 + 파트너스 문장, 영상은 slides.json `"kind": "ad"`(광고 화면·앞뒤 무음), 쇼츠 foot·띠는 초록 '광고' 칩(health_midroll.md 10절).
- 롱폼은 핵심 종목 후속편 중심(R1′). 상위 넷 PLUG·JOBY·LAES·SLDP 우선, IREN·SMR·BTQ는 쇼츠·리포트·Threads 중심. 핵심에 새 사건이 없을 때만 탐색 종목 1편. 하루 기본 2편, 상한 3편. 같은 종목 롱폼 72시간 간격.
- 모든 자산은 통섭: 패턴 이름·다른 종목 기저율·정체성 문장, 영상·리포트에 교차 링크.
- 모든 설명란에 '📊 예측 성적표' 줄, 실시간 알림 문장(인스타그램 '참여'·앱 설치).
- 김박사 몰이 회차별 쿠팡 상품을 대신한다(11-23 쿠팡 판정).
- 롱폼·숏폼 최대한 애니메이션, 쇼츠는 0초 표지 완성. 업로드 뒤 한국어 자막 자동.
- 맥은 TTS만. 키는 GitHub Secrets·클라우드 환경에만.
- 오답노트 시리즈 폐기(1편만 공개 유지).

## 5. 고칠 때
노하우를 새로 얻으면 원문(SKILL.md·runbooks·review)에 넣고, 이 지도에는 **새 문서나 새 도구가 생겼을 때만** 한 줄 추가한다(규칙을 여기에 복사하지 않는다 — 두 곳이 달라지는 것을 막기 위해).
