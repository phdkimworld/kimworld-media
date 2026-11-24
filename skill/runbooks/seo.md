# 검색 노출(SEO) 점검표 — drkimworld.com

출처: ECC `skills/seo/SKILL.md`(github.com/affaan-m/ECC, MIT, affaan-m) 참고·각색. 운영자 2026-11-24 "알아서 적용해".
원본은 일반 웹사이트용 영어 점검표다. 여기서는 우리 사이트(정적 빌드 `build.py` + GitHub Pages + Cloudflare, 한국어 단일 언어, 네이버·구글·다음·빙)에 맞는 항목만 남겼다. 원본의 상품(Product·Offer) 스키마·키워드 조사 절차는 뺐다. 원본 코드는 가져오지 않았다.

**우선순위**: 사이트 `AGENTS.md`(검색 노출 줄)와 SKILL R1.2(제목·summary)가 이 문서보다 앞선다. 이 문서는 '무엇을 어디서 확인하나'를 모은 점검표이고, 규칙의 원문은 그쪽에 둔다.
**자동 검사**: 아래 ✅ 항목은 사이트 `build.py`의 `seo_audit()`가 빌드마다 본다(`--strict`면 배포 전에 막힘, 검사 자체는 `tests/test_build.py` 13절). 사람이 볼 것은 ☐.
**원칙(원본에서)**: 기술적 막힘을 먼저 고친다 → 한 주소에 한 검색 의도 → 꼼수(키워드 반복·보이지 않는 스키마) 금지 → 휴대폰 기준 → 모든 지적은 '어느 화면·어느 파일'까지.

## 1. 기술 SEO (수집·색인)

| 항목 | 우리 기준 | 어디서 | 확인 |
| --- | --- | --- | --- |
| robots.txt | 중요 화면 허용, `/admin/ /dm/ /settings/ /search/<스팸>` 차단, 일반 검색엔진은 `/r/*.md` 차단, AI 수집기 이름으로 허용, Sitemap·RSS 줄 | `build.py` robots 부분 | 기존 검사(13·15절) |
| noindex | 종목 리포트 1개뿐인 종목·리포트 없는 테마·검색·설정·쪽지·프로필·404는 noindex. 그 밖의 중요한 화면이 실수로 noindex가 아닐 것 | 각 템플릿 `block robots` | ✅ 사이트맵에 noindex 화면 없음 |
| canonical | 색인 대상 화면마다 자기 주소(https, 끝 `/`). 404는 canonical 없음 | `base.html` `block canonical` | ✅ |
| 사이트맵 | 공개 리포트·종목(2편+)·테마(리포트 있음)·소개 등·전체 목록·성적표·용어. 리포트는 대표 이미지 포함 | `build.py` urls | ✅ 주소마다 파일 있음 |
| lastmod | **내용이 바뀐 날만**: 리포트=updated/date, 홈·전체 목록=가장 최근 리포트 날, 용어=보이는 예문 리포트 중 최근 날, 소개 등=머리말 `updated`, 성적표=`as_of`. 빌드 날짜로 다 찍으면 구글이 lastmod를 무시한다 | `build.py` urls | ✅ 미래 날짜 없음·80% 넘게 오늘이면 경고 |
| hreflang | 한국어 단일 언어라 **쓰지 않는다**(넣으면 오히려 오류 보고) | — | ☐ 다국어를 만들 때만 다시 봄 |
| 리디렉트 | 끝 `/` 없는 주소 → 301 한 번(GitHub Pages). http→https, www→맨 도메인은 Cloudflare에서 301 한 번. 두 번 넘게 이어지지 않게 | Cloudflare | ☐ `curl -sI http://drkimworld.com/`·`https://www.drkimworld.com/`가 301 |
| 404 | 없는 주소는 상태 코드 404 + noindex + 검색창 | `templates/404.html` | ☐ curl로 404 확인 |
| 주소(slug) | **바꾸지 않는다**. 바꾸면 쌓인 색인·링크를 잃는다 | — | 금지 |
| 클릭 깊이 | 리포트는 홈·종목·테마·전체 목록(`/reports/`)에서 2번 안에 | 템플릿 | ☐ |

## 2. 화면 메타 (제목·설명·공유)

| 항목 | 우리 기준 | 확인 |
| --- | --- | --- |
| `<title>` | 리포트 `'<이름>(<티커>) 주가 분석 — <훅 첫 마디> \| 김박사 월드'`(`seo_fields`). 원본은 50~60자를 권하나 한글은 폭이 넓어 **앞 30자 안에 이름·티커·주가**가 핵심(R1.2). 사이트 전체에서 중복 금지 | ✅ 하나·중복 없음 |
| meta description | 1~160자(리포트는 `seo_desc` 120자 안: 첫 문장 숫자 + 마지막 질문). 종목 화면은 최신 리포트의 `seo_desc`를 붙여 160자에서 자름 | ✅ 1~160자 |
| summary(원재료) | 120자 안팎·첫머리 `<이름>(<티커>) 주가`(R1.2, easy_check) | 기존 |
| h1 | 화면마다 하나. h2·h3는 실제 내용 순서 | ✅ h1 하나 |
| og·twitter | og:title(공유 제목 한 줄)·og:description(무료 안내)·og:image 1200×630 PNG·alt, `summary_large_image` | 기존(16절) |
| 대표 이미지 | 리포트마다 `/og/<slug>.png` 1200×630, 사이트맵 image:image | ☐ 새 그림 틀을 만들면 크기 확인 |
| robots meta | 기본 `max-image-preview:large`(디스커버) | 기존 |

## 3. 구조화 데이터(JSON-LD)

| 화면 | 스키마 | 비고 |
| --- | --- | --- |
| 홈 | WebSite(+SearchAction) · Organization(로고·sameAs: 유튜브·Threads·인스타·텔레그램) | 페이스북 주소가 생기면 `site.yaml`만 채우면 자동 |
| 리포트 | Article(headline·날짜 ISO+시간대·image·author 편집팀·publisher·citation·isAccessibleForFree) · BreadcrumbList(홈›테마›종목›리포트) · FAQPage | ✅ Article·BreadcrumbList 필수 |
| FAQPage | **화면에 보이는 것만**: '짧은 답' 절(제목 질문) + '자주 묻는 질문'(blog_faq). 이야기형처럼 '짧은 답'이 없어도 보이는 FAQ가 있으면 만든다 | ✅ 보이는 FAQ ↔ FAQPage. 구글은 2023년부터 FAQ 리치 결과를 정부·건강 사이트에만 보여 주므로 효과는 네이버·AI 답변 쪽 |
| 종목·테마 | BreadcrumbList · ItemList | 기존 |
| 용어 | DefinedTerm | 기존 |
| 공통 | JSON-LD가 JSON으로 읽힐 것 | ✅ |

쓰지 않는 것: NewsArticle(뉴스 발행처 아님 — Article 유지), Product·Offer(몰은 별도 사이트), Review·Rating(지어낸 평점 금지).
확인 도구: 구글 리치 결과 테스트(search.google.com/test/rich-results), 스키마 검사기(validator.schema.org).

## 4. Core Web Vitals (휴대폰 기준)

목표: LCP < 2.5초, INP < 200ms, CLS < 0.1.

| 항목 | 우리 상태·기준 | 확인 |
| --- | --- | --- |
| 그림 자리 예약 | 모든 `<img>`에 width·height(CLS) | ✅ |
| 지연 로드 | 본문 차트·영상 썸네일은 `loading="lazy"`(`chart_img_attrs`), 첫 화면 로고·아이콘(svg)은 즉시 | ☐ 첫 화면 그림에 lazy를 달지 않기(LCP 늦어짐) |
| 광고 자리 | 높이 예약 이미 있음(광고 틀 min-height) | 기존 |
| 글꼴 | Pretendard CSS preload 후 늦게 붙임(시스템 글꼴 먼저) | 기존 |
| 무거운 스크립트 | 광고·분석 스크립트는 async. 새 스크립트를 head에 동기로 넣지 않기 | ☐ |
| 실측 | 서치 콘솔 'Core Web Vitals' 보고서, PageSpeed Insights(pagespeed.web.dev) 휴대폰 탭 | ☐ 운영자 월 1회 |

## 5. 내부 링크

| 연결 | 어디 | 기준 |
| --- | --- | --- |
| 같은 종목 | 리포트 → `/t/<티커>/`(이동 경로·종목 칩), 종목 화면 → 리포트 전부 | 기존 |
| 같은 테마 | 리포트 → `/theme/<slug>/`, 테마 → 리포트 | 기존 |
| 함께 읽기 | 본문 중간 '함께 읽기'(`insert_mid_next`)·끝 추천 | 기존 |
| 새 리포트 → 옛 리포트 | 직전 리포트 잇기(SKILL 3.4.1) | 제작 규칙 |
| 앵커 글 | '여기'·'더 보기' 대신 '<이름> 지난 리포트: <훅>'처럼 내용이 보이게 | ☐ |
| 깨진 링크 | 내부 href/src가 파일을 가리킴 | 기존(빌드 검사) |

## 6. 콘텐츠 품질(원본의 반대 패턴)

- 키워드 반복 금지(제목·설명에 '주가' 한 번). 사람이 읽는 문장이 먼저.
- 거의 같은 얇은 화면 금지: 리포트 1개뿐인 종목 화면은 noindex(이미 적용), 예문 2개 미만 용어는 화면을 만들지 않음(이미 적용).
- 화면에 없는 내용을 스키마에 넣지 않는다(FAQPage는 보이는 FAQ만).
- 한 주소에 한 검색 의도: 같은 종목 후속편은 훅이 달라야 하고(제목 중복 검사), 종목 화면이 '<이름> 주가' 대표 주소다.

## 7. 운영자 할 일(서치 콘솔 등) — 정확한 메뉴

**구글 서치 콘솔**(search.google.com/search-console)
1. 속성 확인: 왼쪽 위 속성 선택 → 'drkimworld.com'(도메인 속성)이 있는지. 없으면 '속성 추가' → '도메인' → DNS TXT를 Cloudflare 'DNS → Records'에 추가.
2. 사이트맵: 왼쪽 '색인 생성 → Sitemaps' → '새 사이트맵 추가'에 `sitemap.xml` → 제출. (RSS `rss.xml`도 같은 곳에 추가 가능)
3. 색인 상태: '색인 생성 → 페이지'에서 '발견됨 - 현재 색인이 생성되지 않음'·'중복' 사유 확인.
4. 새 리포트 빨리: 맨 위 'URL 검사'에 리포트 주소 → '색인 생성 요청'(하루 몇 건 한도).
5. 구조화 데이터: '개선사항(Enhancements)'의 '탐색경로(Breadcrumbs)' 오류 확인.
6. 속도: '환경(Experience) → Core Web Vitals' 휴대기기 탭.

**네이버 서치어드바이저**(searchadvisor.naver.com → 오른쪽 위 '웹마스터 도구')
1. 사이트 목록에서 drkimworld.com 선택(없으면 '사이트 등록' → 메타 태그 확인, 값은 `site.yaml`).
2. '요청 → 사이트맵 제출'에 `https://drkimworld.com/sitemap.xml`.
3. '요청 → RSS 제출'에 `https://drkimworld.com/rss.xml`.
4. '검증 → robots.txt'에서 수집 허용 확인, '검증 → 웹 페이지 최적화'에 리포트 주소 하나.
5. '리포트 → 검색 반영'·'콘텐츠 노출/클릭' 주 1회 확인.

**빙 웹마스터 도구**(bing.com/webmasters): 'Sitemaps' → `sitemap.xml` 제출(또는 'Import'로 구글 서치 콘솔에서 가져오기). IndexNow는 배포 때 자동.
**다음 웹마스터도구**(webmaster.daum.net): 등록됨(robots.txt PIN). RSS는 '사이트 수집 요청'에 `rss.xml`.

**Cloudflare**(dash.cloudflare.com → drkimworld.com)
- 'SSL/TLS → Edge Certificates → Always Use HTTPS' 켜기(http 주소가 200으로 열리면 중복).
- www: 'DNS → Records'에 `www` CNAME → `drkimworld.com`(프록시 켬), 'Rules → Redirect Rules → 템플릿 Redirect from WWW to Root'(301). 지금 www는 522 오류.

## 8. 점검 순서(새 템플릿·큰 개편 뒤)

1. `python3 build.py --out /tmp/x` → '검색 기본기' 경고가 없는지.
2. 리포트 3편(최신·이야기형·FAQ 있는 것)·홈·종목 화면을 이 표 1~5절로 본다. 결과는 미디어 `review/seo_audit.md`에 `[심각도] 문제 / 위치 / 영향 / 고칠 곳` 형식으로.
3. 고칠 수 있는 것은 고치고, 다시 생기지 않게 `seo_audit()`나 `tests/test_build.py`에 검사를 더한다.
