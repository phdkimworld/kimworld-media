# 광고·제휴 수익 접근 지침 (모든 세션용)

운영자 지시 2026-11-19 "모든 광고 관련 접근 지침 작성". 김박사 월드의 광고·제휴 수익원(쿠팡 파트너스·김박사 몰·카카오 애드핏·구글 애드센스·데이블·유튜브 유료 광고 표시)을 세션이 **키 없이** 읽고 고치는 길, 하면 안 되는 것, 막혔을 때 할 일을 한곳에 모은다.
채널(유튜브·SNS·블로거·텔레그램) 키와 만료는 `channel_access.md`, Cloudflare 워커·D1은 스킬 `kimworld-cloudflare`가 기준이다. 이 문서와 다르면 사이트 저장소 `AGENTS.md`(광고 장)가 이긴다.

## 0. 한눈에

| 수익원 | 지금 상태(2026-11-19) | 숫자 보는 곳(비공개) | 바꾸는 곳 | 키(값 출력 금지) |
|---|---|---|---|---|
| 쿠팡 파트너스(전체) | 켜짐 — 실적 숫자는 비공개 ops-data에서만 본다 | ops-data `stats/coupang.json`(하위 ID별 `by_sub`, 링크 종류 `click_addtags_by_sub`, 주문 상세 `orders_detail` — 주문번호 없음), `stats/digest.md` 쿠팡 줄 | 아래 1장 | `COUPANG_ACCESS_KEY`·`COUPANG_SECRET_KEY`(사이트 저장소 Secrets) |
| 김박사 몰 | 11-19 개설 https://mall.drkimworld.com | digest '김박사 몰' 줄(쿠팡 `mall…` + 사이트 `/mall/` 랜딩 채널별) | 사이트 저장소 `mall/mall.yaml`·`scripts/mall_build.py`·`mall.yml` | 쿠팡 키 + `CLOUDFLARE_API_TOKEN`·`CLOUDFLARE_ACCOUNT_ID` |
| 카카오 애드핏(사이트) | 켜짐, 단위 7개(`ads.yaml adfit.units`) | ops-data `stats/analytics.json` `adfit`(일별), digest 애드핏 줄 | 사이트 `ads.yaml` | `ADFIT_INGEST_KEY`(실적 받기), `ADFIT_SIGN_SEED`(전달 앱 서명) |
| 카카오 애드핏(블로거) | **꺼짐**(11-15 블로그 매체 심사 보류 → 운영자 "블로거에선 애드핏 제거", 165글에서 뺌) | — | `blogger.yml` 비밀값 `BLOGGER_ADFIT_UNIT`이 비어 있으면 꺼짐 | — |
| 구글 애드센스 | 계정 `ca-pub-7488269227696808`, **사이트 승인 전**(재신청 기준 3/5 → 11-22 뒤 4/5, 남은 것 '하루 세션 100') · 자동 광고 꺼둠 · `in_article` 슬롯 | digest '애드센스 재신청' 줄(5개 기준) | 사이트 `ads.yaml adsense` | 없음(공개값) — 콘솔은 운영자만 |
| 데이블 | 꺼짐(번호 없음) | — | `ads.yaml dable` | — |
| 유튜브 | YPP 없음(운영자 2026-11-15 "YPP는 불가능해 보여" — YPP 전제 작업 보류) · 영상 속 광고는 김박사 몰 안내만 | biz_digest·vidIQ | 제작 지침 SKILL V3.9-M | `YT_*`(미디어·사이트 저장소 Secrets, 2026-11-20부터 둘 다) |
| 직접 협찬 | 보류(운영자 결정 '직접 판매 광고 보류') | — | 운영자 결정 전 아무것도 안 함 | — |

공통: GitHub는 REST만(`gh api …`, 워크플로 실행 `gh api -X POST repos/<저장소>/actions/workflows/<파일>/dispatches -f ref=main -f "inputs[이름]=값"`). 결과는 실행 주석(`check-runs/<job>/annotations`)과 ops-data로 읽는다. 셸은 drkimworld.com·쿠팡·카카오·Azure에 닿지 않는다.

## 1. 쿠팡 파트너스

**API 통로(사이트 저장소 Actions — 쿠팡 키는 여기에만)**

| 워크플로 | 하는 일 | 입력 |
|---|---|---|
| `coupang-stats.yml` | 매일 실적(클릭·주문·취소·수수료) → D1·비공개 `stats/coupang.json` | `probe=1`이면 필드 이름도 남김 |
| `mall.yml` | 김박사 몰 진열 받기(오늘의 특가·카테고리 베스트) + 배포 + 도메인 | `fetch=0`이면 저장된 진열로만 다시 올림 |
| `coupang-deeplink.yml` | 쿠팡 주소 → 하위 ID 붙은 단축 링크(주석으로) | `urls`, `subid` |
| `coupang-link-check.yml` | 단축 링크가 어느 하위 ID·lptag로 가는지 확인(서버 열기는 클릭으로 안 셈 — 11-18 확인) | `url` |
| `ad-report.yml` | 검색어별 노출·클릭·주문(2주마다) | — |
| `blogger.yml` | 블로거 글·비교 글·기존 글 백필(`ads_backfill=1`, `ads_backfill_n`) | — |
| `yt-shop.yml` | (11-19로 끝남 — 영상은 김박사 몰 안내) | — |

- **한도**: 검색 API 시간당 10회(사이트 동기화·블로거 비교 글과 나눔). 특가·베스트·딥링크는 몰이 하루 약 12회. 새 작업은 검색을 최소로.
- **하위 ID 규칙**(실적을 나눠 보는 유일한 열쇠 — 새 링크에는 반드시): `mall…`(몰: mallgo 입구·mallgb 특가·mallfood 등 카테고리), `bg…`(블로거 비교 글), `tgcheer`(텔레그램 예전 응원), `yt<카테고리><티커>`(예전 영상 실험), `deal`·`banner`(예전 사이트), 빈 값 = 운영자의 예전 수동 링크. 새 접두어를 만들면 `scripts/coupang_daily.py where()`와 이 표를 같은 커밋에서 고친다.
- **24시간 쿠키**: 링크를 누른 뒤 24시간 안의 쿠팡 구매가 모두 수수료. 그래서 '들어가는 문'(몰 입구)이 진열보다 중요하다(11-19 분석, 근거 숫자는 ops-log).
- **대가성 표시(공정위)**: 쿠팡 링크가 있는 모든 화면·글·설명란에 "쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다" + 링크 `rel="sponsored nofollow"`. 몰은 테스트(`tests/test_build.py` '김박사 몰')가 막는다.
- **사이트 본문에는 쿠팡 상품을 싣지 않는다**(11-16 '검색 자료실' 개편 결정, 애드센스 재신청 대비). 사이트에는 하단 메뉴 '김박사 몰'과 `/mall/` 넘겨주기(noindex)만.
- **금지**: 본인·가족 구매 유도, 클릭 유도 자동화(봇·서버에서 링크 열기로 실적 만들기), 효능 문구(건강기능식품은 이름만), "꼭·지금" 재촉, 수익 숫자를 공개 저장소·주석·커밋에 쓰기.

## 2. 김박사 몰 (https://mall.drkimworld.com)

- 구조: `mall/mall.yaml`(컨셉·카테고리 id·하위 ID·주소) → `scripts/mall_build.py --fetch --build dist-mall` → `mall.yml`이 매일 한국 07:10 Cloudflare 워커 정적 자산(`mall/wrangler.toml`, 이름 kimworld-mall)으로 배포. 토큰에 Pages 권한이 없어 워커로 올린다(11-19). 사용자 지정 도메인은 같은 단계가 붙인다.
- 채널 연결은 모두 고정 주소 `https://drkimworld.com/mall/?utm_source=<채널>&utm_medium=…&utm_content=mall` — 유튜브(새 롱폼 V3.9-M, 옛 영상 사이트 저장소 `yt-desc.yml` 하루 15편), 블로거(글 끝 한 줄, 기존 182건 백필), 텔레그램(새 리포트 🛒), Threads(끝 댓글), 페이스북(첫 댓글), 사이트 하단 메뉴. 인스타그램은 프로필 링크(운영자 몫).
- 고치기: 카테고리 바꾸기·순서·첫 화면 문구는 `mall.yaml`. 쿠팡 카테고리 id(예: 1012 식품, 1014 생활, 1013 주방, 1015 홈인테리어, 1016 가전디지털, 1017 스포츠, 1019 도서, 1018 자동차, 1002 남성패션, 1024 헬스·건강식품, 1029 반려동물). 고친 뒤 `python3 scripts/mall_build.py --build /tmp/m`과 `tests/test_build.py`.
- **추적(2026-11-20)**: 채널별 깔때기(입구 도착 → 몰 화면 → 쿠팡 클릭)·화면·칸·입구 세부를 워커 `/v1/mall`(D1 `mall_ev`)이 하루 합계로 모으고, 비공개 ops-data `stats/mall/summary.md`(요약·관찰)와 `stats/mall/history.json`(날짜별 누적)에 매일 쌓인다. 읽기: `gh api "repos/phdkimworld/kimworld/contents/stats/mall/summary.md?ref=ops-data" -H "Accept: application/vnd.github.raw"`. 새 채널은 `/mall/?utm_source=<채널>&utm_campaign=<세부>`. 검색: 빙·네이버는 mall.yml IndexNow(매일), 구글은 서치 콘솔 도메인 속성 `sc-domain:drkimworld.com`(algotraz.channel 계정)에 몰 사이트맵 제출됨(11-21, 하위 도메인은 따로 확인 불필요).
- 판정: 매일 점검이 digest '김박사 몰' 줄로 본다. 첫 판정 12-03(클릭 나는 채널·칸은 늘리고 0인 칸은 바꾼다).

## 3. 카카오 애드핏

- **사이트 단위**: `ads.yaml adfit.units`(DAN-… 공개값 7개)와 `placements`. 한 페이지 4개 초과 금지(빌드가 막음), 동적 반복 로드 금지, 실수 클릭 유도 금지(애드핏 정책 — AGENTS 광고 장).
- **실적 받기**: 운영자 휴대폰 '애드핏 전달' 앱(`android/adfit-forwarder`, 카카오톡 '카카오애드핏' 실적 알림만 골라) → 워커 `POST /v1/ingest/adfit?k=<열쇠>` → D1 `adfit_daily` → 비공개 `analytics.json adfit`. 열쇠는 운영 통계 화면 '열쇠 만들기'(운영자 로그인) 또는 `ADFIT_INGEST_KEY`. 앱 빌드 `android.yml`(서명 `ADFIT_SIGN_SEED`).
- **이상 신호**: digest '애드핏 기록이 이틀 넘게 끊김' → 운영자에게 "휴대폰 애드핏 전달 앱이 켜져 있는지(알림 접근 권한)" 한 줄. 세션이 카카오에 직접 로그인하지 않는다.
- **블로거**: 꺼짐. 다시 켜려면 운영자 결정 + 블로그 매체 승인 + `BLOGGER_ADFIT_UNIT` 비밀값(운영자가 넣음). 그 전에는 넣지 않는다.

## 4. 구글 애드센스

- 사이트 코드: `ads.yaml adsense.client`(공개값)·`slots`, `ads.txt` 자동. 자동 광고는 꺼둠(자리 통제·비교 목적).
- 재신청: digest '애드센스 재신청 a/5'(공개 6주 11-22 이후 · 공개 리포트 150+ · 하루 세션 100+ · 검색 세션 7일 20+ · 정책 페이지·noindex). 5/5가 되면 매일 점검이 운영자에게 푸시("애드센스 > 사이트 > drkimworld.com > '문제를 해결했음을 확인' 체크 후 검토 요청"). **검토 요청 버튼은 운영자만** 누른다.
- 재신청 전까지 지킬 것: 사이트 본문에 제휴 상품 다시 넣지 않기, 얇은 페이지 늘리지 않기(종목·테마 목록 noindex 유지), 정책 페이지(편집 원칙·업데이트·소개·개인정보·연락처) 지우지 않기.
- 콘솔(수익·정책 알림)은 세션이 볼 수 없다. 운영자가 메일로 받은 정책 알림은 Gmail 커넥터가 있는 세션만 읽고, 고칠 것은 `ads.yaml`·템플릿에서.

## 5. 유튜브 수익 표시

- YPP 없음 → 영상 광고 수익 없음, YPP 전제 작업 금지.
- 영상에 김박사 몰(쿠팡) 안내가 있으면 업로드 때 `paid_promo: true`(→ API `paidProductPlacementDetails.hasPaidProductPlacement`) + 설명란 끝 대가성 줄. 옛 영상은 `yt-desc.yml`이 대가성 줄을 함께 넣는다(유료 프로모션 체크는 옛 영상에는 API로 안 바꿈).
- 유튜브 API 쿼터(하루 1만 단위, 업로드 1건 1,600): 설명란 고치기(약 50단위/편)는 하루 15편 이하.

## 6. 막혔을 때

| 증상 | 할 일 |
|---|---|
| 쿠팡 API 401/403 | 키 만료·IP 아님 — 운영자에게 "쿠팡 파트너스 > API 키 상태 확인" 한 줄. 다른 키로 우회 금지 |
| 쿠팡 429 | 시간당 한도. 다음 실행으로 미룸 |
| 쿠팡 실적에 새 하위 ID가 안 보임 | 보고서는 클릭이 있는 날만 줌. 서버에서 연 링크는 안 셈. 사람이 휴대폰으로 눌러야 확인 |
| 몰 배포 실패 | `mall.yml` 주석 → wrangler 오류. 권한 문제면 운영자에게 Cloudflare 토큰 권한(Workers Scripts 편집) 확인 요청 |
| 애드핏 기록 끊김 | 전달 앱(운영자 휴대폰) — 3장 |
| 애드센스 정책 알림 | 운영자에게 받은 내용대로 `ads.yaml`·템플릿 수정, 검토 요청은 운영자 |

## 7. 하지 않는 것(모든 수익원)

- 키·토큰·열쇠 값을 채팅·파일·커밋·주석에 쓰기, 사용자에게 붙여 달라고 하기(GitHub Secrets에만)
- 수익 금액·주문 상세를 공개 저장소(사이트·미디어)·주석·커밋 메시지에 쓰기 — ops-data에만
- 매수·매도·수익 암시, 재촉, 효능 문구, 대가성 문구 빼기, `rel="sponsored"` 빼기
- 운영자 보류 항목 건드리기: 직접 판매 광고(협찬), 트레이딩뷰, 카카오 채널 운영, YPP 전제, 이메일 수집, 네이버 원탭 게시
- 광고 계정 설정·결제·약관 동의·검토 요청 — 운영자 몫

이 문서는 공개 저장소에 있다. 수익·클릭·주문 숫자, 상품명 단위 주문 내역은 여기에 적지 않는다(ops-data `ops-log.md`·`stats/`에만).
