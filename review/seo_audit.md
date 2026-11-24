# 검색 노출(SEO) 감사 — 2026-11-24

점검표: `skill/runbooks/seo.md`(ECC skills/seo (MIT, affaan-m) 참고·각색).
대상: 로컬 빌드(main ec73598, 리포트 194편, 색인 대상 412화면) 전체 자동 스캔 + 실제 사이트 curl.
표본: 리포트 3편 `/r/apld-2026-11/`(최신·이야기형), `/r/rgti-2026-10/`(짧은 답·FAQ), `/r/pattern-2026-11-22/`(연재), 홈 `/`, 종목 `/t/rgti/`, 테마 `/theme/ai-chips/`, 404.
형식: `[심각도] 문제 / 위치 / 영향 / 고칠 곳 / 상태`

## 발견 사항

1. **[HIGH] www 주소가 열리지 않음**
   위치: `https://www.drkimworld.com/` → Cloudflare 522
   영향: www를 붙여 들어오거나 www로 걸린 외부 링크가 오류. 링크 가치가 사라짐.
   고칠 곳: Cloudflare DNS에 www CNAME + www→맨 도메인 301(운영자, seo.md 7절). 상태: **운영자 할 일**

2. **[HIGH] http 주소가 https로 넘어가지 않음(200 응답)**
   위치: `http://drkimworld.com/` → 200(cf-ray 있음, 301 아님). https 쪽은 HSTS 있음.
   영향: 같은 내용이 http·https 두 주소로 열림(canonical은 https라 큰 손해는 아니나 수집 몫 낭비·보안 경고 가능).
   고칠 곳: Cloudflare 'Always Use HTTPS' 켜기(운영자). 상태: **운영자 할 일**(점검 컨테이너의 프록시를 거친 측정이라 운영자 브라우저로 한 번 더 확인)

3. **[MED] 사이트맵 lastmod가 빌드 날짜로 찍힘**
   위치: `build.py` 사이트맵 urls — 홈·전체 목록·성적표·용어 142개가 늘 '오늘'(실사이트 412개 중 157개가 2026-11-24)
   영향: 구글은 lastmod가 믿을 만할 때만 쓴다. 매일 다 바뀐다고 알리면 리포트의 진짜 갱신일도 무시될 수 있음.
   고친 것: 홈·전체 목록 = 가장 최근 리포트 날, 용어 = 화면에 보이는 예문 리포트 중 최근 날, 성적표 = `as_of`, 소개 등 = 머리말 `updated`, 테마 = 최근 리포트(갱신일 포함, 전에는 첫 리포트만). 이제 412개 모두 lastmod가 있고 '오늘'은 0개. 상태: **고침**

4. **[MED] 이야기형 리포트 37편에 FAQPage 없음**
   위치: `templates/report.html` — FAQPage를 '## 짧은 답' 절이 있을 때만 만들었음. 이야기형(`style: story`)은 그 절이 없지만 화면에 '자주 묻는 질문'(blog_faq)은 보임.
   영향: 네이버·AI 답변이 읽을 질문·답 구조가 최신 리포트들에서 빠짐(구글 FAQ 리치 결과는 2023년부터 정부·건강 사이트만이라 구글 노출 효과는 작음).
   고친 것: 보이는 FAQ가 있으면 그것만으로 FAQPage(짧은 답 질문은 있을 때만). 192/194편. 남은 2편(`aspi-2026-10` 등)은 짧은 답·FAQ가 모두 없어 스키마도 없음(맞음). 상태: **고침**

5. **[MED] 검색 설명이 160자를 넘는 화면 다수**
   위치: 종목 화면 37개(`ticker.html`: '분석 리포트 n개(날짜 최신). ' + 요약 전체, 최대 312자), 테마 화면(`theme.html`: 소개 + 종목 이름 전부, 최대 309자)
   영향: 네이버·구글 스니펫에서 잘려 끝 질문·핵심 숫자가 안 보임.
   고친 것: 종목 = 최신 리포트의 `seo_desc`(120자 안) 사용 + 158자에서 자름, 테마 = 158자에서 낱말 경계로 자름. 상태: **고침**

6. **[LOW] 404 화면 canonical이 `/404.html`**
   위치: `templates/404.html`(base의 canonical 그대로). 없는 주소 어디서나 이 canonical이 보임.
   고친 것: base에 `block canonical`, 404에서는 비움. 상태: **고침**

7. **[LOW] 리포트 `article:modified_time` 메타가 두 번(형식 다름)**
   위치: `templates/report.html` 머리(ISO+시간대 하나, 날짜만 하나)
   고친 것: 시간대 있는 것 하나만. 상태: **고침**

8. **[LOW] Organization sameAs가 유튜브 하나**
   위치: `templates/index.html`
   영향: 브랜드 지식 패널·채널 연결 신호 약함.
   고친 것: 유튜브·Threads·인스타·(페이스북 주소 생기면 자동)·텔레그램. 상태: **고침**

9. **[LOW] 설명이 짧은 화면 8개**
   위치: `/about/`(28자)·`/contact/`(10자)·`/disclaimer/`(29자)·`/privacy/`(15자) 등 소개·법적 화면, 옛 리포트 `anro-2026-10`(47자)·`ant-2026-10`(40자) summary
   영향: 작음(검색 유입 대상 화면이 아님). 리포트 2편은 스니펫이 빈약.
   고칠 곳: 법적 화면 문구는 운영자 확인 대상(AGENTS 1장)이라 그대로 둠. 옛 리포트 summary는 다음 갱신 때 R1.2(120자 안팎)로. 상태: 보류

10. **[INFO] 제목 길이**
    리포트 `<title>` 67~69자(브랜드 꼬리 포함). 원본 권장 50~60자보다 길지만, 한글은 폭이 넓어 앞 30자 안에 '이름(티커) 주가 분석'이 오도록 이미 설계됨(R1.2·AGENTS). 바꾸지 않음. 사이트 전체 제목 중복 0, 설명 중복 0.

## 문제없음(확인만)

- canonical: 색인 대상 412화면 모두 자기 주소. hreflang 없음(한국어 단일, 맞음).
- 끝 `/` 없는 주소 → 301 한 번(`/r/rgti-2026-10` → `/r/rgti-2026-10/`). 없는 주소 → 404 + noindex.
- 사이트맵 주소 412개 모두 파일 있음, noindex 화면 없음. robots.txt 사이트맵·RSS·차단 규칙 정상.
- 구조화 데이터 JSON 모두 읽힘. 리포트 Article·BreadcrumbList 194/194, 홈 WebSite+Organization(@graph), 종목·테마 BreadcrumbList·ItemList.
- og:image 1200×630 PNG 30~70KB, 선언 크기와 일치.
- 모든 `<img>` width·height 있음(CLS). lazy 아닌 것은 머리줄 로고·작은 svg 아바타뿐(첫 화면, 맞음).
- h1: 표본 화면 모두 하나. 내부 링크: 리포트당 리포트·종목·테마 링크 27~33개(함께 읽기·이동 경로·종목 칩).
- 응답: 0.25~0.6초, `cache-control: max-age=600`, HSTS.

## 다시 생기지 않게(자동 검사)

사이트 `build.py`의 `seo_audit()`가 빌드마다 위 3~7번과 기본기를 본다(`--strict`면 배포 전에 막힘): 색인 대상 화면의 제목 하나·중복 없음, 설명 1~160자, canonical = 자기 주소, h1 하나, 모든 화면 JSON-LD 읽힘·그림 width/height, 리포트 Article·BreadcrumbList·보이는 FAQ↔FAQPage, 사이트맵 주소↔파일·noindex 아님·lastmod 미래 아님·80% 넘게 오늘이면 경고. 검사 자체의 검사는 `tests/test_build.py` 13절.
