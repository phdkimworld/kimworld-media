# 채널 접근 권한 지침 — 유튜브·Threads·인스타그램·페이스북·블로거·텔레그램 (2026-11-19 운영자 "유튜브 채널 접근 권한 지침 작성" → "모든 sns 채널 다 포함")

모든 세션과 에이전트가 각 채널에 어떤 권한으로 접근하는지, 키를 어디에 두는지, 권한을 넓히거나 다시 발급할 때 무엇을 하는지 적은 문서다. 키 값은 이 문서와 채팅, 커밋, 로그 어디에도 적지 않는다.

## 0. 한눈에 보기
| 채널 | 비밀값(GitHub Secrets, 값은 출력 금지) | 쓰는 곳 | 만료·갱신 | 자세히 |
|---|---|---|---|---|
| 유튜브 @drkimworld | `YT_CLIENT_ID`·`YT_CLIENT_SECRET`·`YT_REFRESH_TOKEN` (media·site 저장소 + 클라우드 환경 변수) | 업로드·답글·재생목록·통계(미디어 tools/yt_*.py, 사이트 comment-ai·weekly-ai·yt-shop) | 갱신 토큰은 오래 감. 동의 화면 '테스트'면 7일 | 아래 1~6장 |
| Threads | `THREADS_ACCESS_TOKEN`·`THREADS_USER_ID` (site) | 게시·댓글 목록·답글(social.yml·social-comments.yml·comment-ai.yml·weekly-ai.yml) | 장기 토큰 60일 → `token-refresh.yml`이 매달 1·15일 자동 갱신 | 7장 |
| Threads 두 번째(@drkimworld, 2026-11-25) | `DRKIM_THREADS_ACCESS_TOKEN` (site) | 토큰 확인·한 글 게시(`threads-drkim.yml` mode ping/post) — 용도(어떤 글을 올릴지)는 운영자가 정한 뒤 붙인다 | 60일 → `token-refresh.yml`이 같이 갱신 | 7장 |
| 인스타그램 | `IG_ACCESS_TOKEN`·`IG_USER_ID` (site) | 릴스·카드 게시·댓글(social.yml·social-comments.yml·weekly-ai.yml), 권한 확인 `ig-perm-check.yml` | 60일 → 같은 자동 갱신 | 7장 |
| 페이스북 페이지 | `FB_PAGE_TOKEN`·`FB_PAGE_ID` (site) | 릴스·카드 게시·댓글(social.yml·social-comments.yml·comment-ai.yml·weekly-ai.yml) | 시스템 사용자(kimworld-bot) 토큰 — 만료 없음 | 7장 |
| 블로거 | `BLOGGER_REFRESH_TOKEN`·`BLOGGER_CLIENT_SECRET`(또는 `GOOGLE_CLIENT_ID`·`GOOGLE_CLIENT_SECRET`) (site) | 리포트 게시(blogger.yml) | Google 갱신 토큰(유튜브와 같은 규칙) | 8장, 사이트 docs/blogger-guide.md |
| 텔레그램 @drkimworld | `TELEGRAM_BOT_TOKEN` (site) | 새 리포트 게시(telegram.yml) | 만료 없음(BotFather에서 폐기 전까지) | 9장 |
| 자동 갱신 도구 | `GH_SECRETS_PAT` (site) | token-refresh.yml이 비밀값을 바꿀 때 | 운영자가 정한 만료일 — 만료되면 Threads·인스타 자동 갱신이 멈춤 | 7장 |

**광고·제휴 수익원**(쿠팡 파트너스·김박사 몰·애드핏·애드센스·데이블·유튜브 유료 표시)의 접근·키·금지는 `ads_access.md`(2026-11-19).

**확인 필요(2026-11-19)**: 사이트 저장소 Actions에서 유튜브 키를 읽는 스크립트(yt_comments.available())가 '키 없음'을 냈다 — 사이트 저장소 Secrets에 `YT_*` 세 개가 없거나 이름이 다를 수 있다(미디어 저장소 youtube-upload.yml은 같은 날 성공). 그래서 유튜브 API가 필요한 새 작업은 미디어 저장소 워크플로로 돌린다: `yt-desc.yml`(main 브랜치, 옛 영상 설명란 링크 — plan·apply·revert). 사이트 comment-ai.yml·weekly-ai.yml·yt-shop.yml의 유튜브 부분도 같은 이유로 건너뛰고 있을 수 있으니, 운영자가 사이트 저장소 Settings → Secrets에 `YT_CLIENT_ID`·`YT_CLIENT_SECRET`·`YT_REFRESH_TOKEN`이 있는지 확인한다(1장 '세 곳의 값은 항상 같아야 한다').

**해결(2026-11-20)**: 사이트 저장소에 `GH_SECRETS_PAT`가 없던 것을 운영자가 넣었고(kimworld-site 전용, Secrets 읽기·쓰기), 세션이 yt-secrets-sync.yml(mode=pubkey → 세션에서 봉인 → mode=set, run 44770847041 성공)로 사이트 Secrets에 `YT_CLIENT_ID`·`YT_CLIENT_SECRET`·`YT_REFRESH_TOKEN`을 넣었다(클라우드 환경 값과 같음). 같은 때 token-refresh.yml 수동 실행 성공(run 44770906930). 유튜브 갱신 토큰을 새로 받으면 클라우드 환경·미디어 Secrets를 바꾼 뒤 세션이 같은 워크플로로 사이트에도 넣는다(평문은 세션 밖으로 나가지 않음).
**yt-desc 이전(2026-11-20)**: 사이트 저장소 plan 시험(run 44771640102)에서 키가 잡혀 옛 영상 설명란 링크 통로를 사이트 저장소 `yt-desc.yml`(main, 기록 `social/youtube/desc_log.json` — 미디어 review/yt_desc_log.json 30건 이어받음)로 옮겼다. 미디어 저장소 main의 yt-desc.yml은 더 쓰지 않는다(기록이 둘로 갈리면 같은 영상을 두 번 고를 수 있다).
**분석 권한 추가(2026-11-20 12:27 ET)**: 운영자가 kimworld 프로젝트에 웹 클라이언트 `kimworld-gh`(리디렉션 OAuth Playground)를 새로 만들고, 범위 youtube·youtube.force-ssl·youtube.upload·yt-analytics.readonly로 갱신 토큰을 받아 세 곳(사이트·미디어 Secrets, 클라우드 환경)의 `YT_*` 세 값을 모두 바꿨다. 확인: 사이트 yt-desc.yml `mode=check`(권한 범위 이름과 분석 API 응답 여부만 주석)에서 네 범위와 분석 API 응답 성공. 이제 `tools/yt_subs.py --report`로 영상별 구독 증가를 읽을 수 있다(구독 시험 A·B 비교). 예전 Desktop 클라이언트는 지우지 않았다(운영자 몫).

공통 규칙: 비밀값은 GitHub Secrets(와 유튜브만 클라우드 환경 변수)에만 둔다. 채팅·커밋·로그·맥으로 옮기지 않는다. 401·403은 다른 계정·키로 우회하지 않고 운영자에게 한 줄로 알린다. 사람에게 관리 권한을 줄 때는 각 플랫폼의 역할 초대를 쓰고 토큰을 건네지 않는다.

# 유튜브

## 1. 키 세 개와 둔 곳
| 이름 | 무엇 | 둔 곳 |
|---|---|---|
| `YT_CLIENT_ID` | Google Cloud OAuth 클라이언트 ID | 클라우드 세션 환경 변수, GitHub Secrets(kimworld-media·kimworld-site) |
| `YT_CLIENT_SECRET` | 같은 클라이언트의 시크릿 | 위와 같음 |
| `YT_REFRESH_TOKEN` | 채널 계정이 승인한 갱신 토큰(권한 범위가 여기에 묶임) | 위와 같음 |

- 세 곳의 값은 항상 같아야 한다. 하나만 바꾸면 그 쪽만 되고 나머지는 401·403으로 멈춘다.
- 맥 실행기와 다른 저장소로 옮기지 않는다. 맥에는 유튜브 키가 없다. 맥은 녹음만 맡는다.
- 출력 금지. 도구는 오류 종류와 짧은 메시지만 남긴다.

## 2. 지금 권한 범위(스코프)와 쓰는 곳
| 스코프 | 하는 일 | 쓰는 도구 |
|---|---|---|
| `youtube.upload` | 영상·쇼츠 올리기, 썸네일 | tools/yt_upload.py, yt_api_upload.py, upload_guard.py, 미디어 youtube-upload.yml |
| `youtube.force-ssl` | 댓글 읽기·답글·수정·숨김, 재생목록, 영상 정보 수정, 워터마크 | yt_reply.py, hourly.py, yt_stats.py(목록·조회), yt_subs.py --watermark, 사이트 yt_comments.py·comment_ai.py, comment-ai.yml·weekly-ai.yml·yt-shop.yml |
| (없음) `yt-analytics.readonly` | 영상별 구독 증가, 시청 지속, 유입 경로 | yt_subs.py --report, yt_stats.py 분석 부분 — 지금은 403이라 채널 전체 숫자로 대신함 |

- 공개 조회수·댓글 수는 `force-ssl`로 읽는다. 영상별 구독 기여·시청 지속시간은 분석 권한이 있어야 한다.
- **분석 자료는 사이트 yt-analytics.yml → ops stats/yt_analytics.json(새 키, 컨테이너 키와 무관)** — 2026-11-21부터. 읽기 `python3 tools/yt_analytics_read.py [--pull] [영상ID…|--sub-test]`(평균 시청 비율·시간·구독 증가·유입 경로). 이 컨테이너의 키는 분석 권한이 없어 위 표의 403이 계속될 수 있다.
- 수익(`yt-analytics-monetary.readonly`)은 YPP가 없어 쓰지 않는다.

## 3. 권한을 넓히거나 다시 발급하는 법(운영자가 브라우저에서, 약 15분)
권한 범위는 갱신 토큰에 묶여 있어서, 범위를 바꾸려면 토큰을 새로 받아야 한다. **기존 범위를 빠뜨리면 업로드·답글이 멈춘다.**
1. Google Cloud Console에서 지금 클라이언트가 있는 프로젝트를 연다. 'API 및 서비스 → 라이브러리'에서 **YouTube Data API v3**(이미 켜짐)와 **YouTube Analytics API**를 켠다.
2. https://developers.google.com/oauthplayground 의 톱니바퀴에서 'Use your own OAuth credentials'를 켜고 클라이언트 ID·시크릿을 넣는다. `redirect_uri_mismatch`가 나면 Console의 OAuth 클라이언트에 승인된 리디렉션 URI `https://developers.google.com/oauthplayground`를 추가한다.
3. 범위 칸에 아래 세 줄을 **모두** 넣고 **채널을 소유한 계정(브랜드 계정이면 그 채널 선택)**으로 승인한다.
   ```
   https://www.googleapis.com/auth/youtube.upload
   https://www.googleapis.com/auth/youtube.force-ssl
   https://www.googleapis.com/auth/yt-analytics.readonly
   ```
4. 'Exchange authorization code for tokens'를 눌러 나온 Refresh token을 1장의 세 곳에 모두 바꿔 넣는다: GitHub kimworld-site → Settings → Secrets, kimworld-media → Settings → Secrets, Claude 클라우드 환경 설정의 환경 변수.
5. 채팅에는 붙여 넣지 않고 "바꿨다"고만 알린다.
- OAuth 동의 화면이 '테스트' 상태면 갱신 토큰이 7일 뒤 만료된다. '프로덕션(게시)' 상태인지 확인한다.

## 4. 바꾼 뒤 확인(세션이 하는 일, 키는 출력하지 않음)
| 확인 | 명령 | 통과 기준 |
|---|---|---|
| 키·채널 연결 | `python3 tools/yt_subs.py` (옵션 없이: 채널 조회만) | channel_id·subscribers가 나오고 `error` 없음 |
| 댓글 권한 | `python3 tools/yt_reply.py --list --days 1` | JSON이 나오고 403 없음 |
| 분석 권한 | `python3 tools/yt_subs.py --report 7` | `analytics`에 영상별 숫자, 403 아님 |
| 사이트 쪽 | GitHub Actions `comment-ai.yml`·`yt-shop.yml` 한 번 실행 | 성공 |
결과는 review/sub_test.md '영상별 구독 읽기' 줄과 production/STATE 메모에 한 줄 남긴다.

## 5. 문제가 생겼을 때
| 증상 | 뜻 | 할 일 |
|---|---|---|
| `invalid_grant` | 갱신 토큰 만료·폐기(비밀번호 변경, 권한 해제, 테스트 앱 7일) | 3장대로 다시 발급, 세 곳 교체 |
| 403 `insufficientPermissions` | 범위 부족 | 그 범위를 넣어 3장 다시 |
| 403 `forbidden`(분석) | 분석 API 미사용 설정 또는 범위 없음 | 3장 1·3번 |
| `uploadLimitExceeded` | 하루 업로드 한도 | 30분마다 재시도(제작 지침), 권한 문제 아님 |
| `quotaExceeded` | API 하루 할당량 | 다음 날(태평양 자정) 재개, 비필수 호출부터 줄임 |
- 403을 돌아가려고 다른 계정·다른 키를 만들거나 우회하지 않는다. 운영자에게 한 줄로 알린다.

## 6. 사람 접근(Studio 권한)
- 다른 사람이 채널을 관리해야 하면 YouTube Studio → 설정 → 권한에서 필요한 최소 역할(보기 전용 → 편집자 → 관리자)로 초대한다. 갱신 토큰이나 클라이언트 시크릿을 사람에게 건네지 않는다.
- 세션·에이전트는 Studio 권한이 아니라 위 OAuth 키로만 접근한다.
- 권한을 거둘 때: Google 계정 → 보안 → 타사 액세스에서 앱 접근을 해제하면 갱신 토큰이 즉시 무효가 된다(그 뒤 3장 재발급 필요).

# Threads · 인스타그램 · 페이스북 (Meta)

## 7. 토큰과 갱신
- Threads·인스타 토큰은 **장기 토큰 60일**이다. 사이트 `token-refresh.yml`(scripts/token_refresh.py)이 매달 1일·15일에 갱신 API를 불러 새 토큰을 `GH_SECRETS_PAT`으로 GitHub 비밀값에 다시 쓴다. 손으로는 Actions 'Token refresh' 실행.
- 갱신이 실패로 표시되면: ① `GH_SECRETS_PAT` 만료 여부(Fine-grained, 저장소 kimworld-site만, 권한 Secrets: Read and write) ② 토큰이 이미 60일을 넘겼는지. 넘겼으면 갱신이 안 되므로 운영자가 Meta 개발자 앱에서 단기 토큰을 다시 받아 장기 토큰으로 교환한 뒤 비밀값을 바꾼다(사이트 social/README.md '토큰 갱신').
- 살아 있는지 확인: Actions `social.yml` mode=`ping`(매주 월요일 자동), 인스타 권한 목록은 `ig-perm-check.yml`.
- 페이스북 페이지 토큰은 시스템 사용자 토큰이라 만료가 없다. 페이지 역할에서 시스템 사용자를 빼거나 앱 권한을 거두면 즉시 무효다.
- 권한 범위: Threads는 `threads_basic`·`threads_content_publish`·`threads_manage_replies`·`threads_read_replies`, 인스타는 Instagram Login 방식의 게시·댓글 관리, 페이스북은 페이지 게시·댓글 관리. 범위를 넓히려면 Meta 앱 검토와 토큰 재발급이 필요하므로 운영자에게 먼저 알린다.
- 하지 않는 것: 인스타 DM 홍보(운영자 지시로 금지), 개인 계정 토큰 사용.

## 7-1. 두 번째 Threads 계정 @drkimworld (2026-11-25 연결, 운영자 "다른세션에 접근 지침 작성")
- **두 계정을 섞지 않는다.** @phdkimworld = 본 채널(리포트 자동 게시, `THREADS_*`, social.yml). @drkimworld = 두 번째 계정(`DRKIM_THREADS_ACCESS_TOKEN`). 다른 쪽 토큰으로 게시하지 않는다.
- **짝 인스타 = @drkimworld, 이미 연결돼 있다**: 사이트 `IG_ACCESS_TOKEN`·`IG_USER_ID`가 이 인스타 계정이다(리포트 릴스·카드가 instagram.com/drkimworld 로 올라감, 2026-11-25 social.yml ping 정상). 즉 본 채널 리포트는 Threads는 @phdkimworld, 인스타는 @drkimworld로 나간다. @drkimworld Threads 용도를 정할 때 이 인스타와 내용이 겹치는지 먼저 본다.
- 같은 Meta 앱 **phdkimworld-poster**(앱 ID 1668388958298068, Threads 앱 ID 2171942756723397, 개발 모드)의 **Threads 테스터**로 붙어 있다. 권한: threads_basic·content_publish·manage_insights·manage_replies·read_replies.
- 키: 사이트 저장소 비밀값 `DRKIM_THREADS_ACCESS_TOKEN`(장기 60일). `token-refresh.yml`이 매달 1·15일 @phdkimworld와 함께 갱신(없으면 경고만 내고 건너뜀). 사용자 ID 비밀값은 없다 — 워크플로가 `me`로 찾는다.
- **용도: 건강월드(영양제) 전용(2026-11-26 운영자 결정).** 형식은 운영자 승인(`skill/health/HEALTH_CHANNEL.md` 4.17), 이후 건강월드 하루 운영이 하루 1~2개 자동 게시(본문 + 내 답글 reply). 주식 리포트는 올리지 않는다(@phdkimworld 몫).
- 통로(사이트 저장소 `threads-drkim.yml`, REST dispatch):
  ```bash
  # 토큰 확인(결과는 주석 '토큰 정상: @drkimworld')
  gh api -X POST repos/phdkimworld/kimworld-site/actions/workflows/threads-drkim.yml/dispatches -f ref=main -f "inputs[mode]=ping"
  # 한 글 게시(500자 이내, 운영자가 본문을 승인한 글만)
  gh api -X POST repos/phdkimworld/kimworld-site/actions/workflows/threads-drkim.yml/dispatches -f ref=main -f "inputs[mode]=post" -f "inputs[text]=..." -f "inputs[reply]=..."   # reply(내 답글)는 비워도 됨
  # 예비: 건강몰 가이드로 자동 작성한 글 미리보기/게시(정기 실행 없음 — 정기 게시는 건강월드 매일 운영 4.17)
  gh api -X POST repos/phdkimworld/kimworld-site/actions/workflows/threads-drkim.yml/dispatches -f ref=main -f "inputs[mode]=preview"
  RID=$(gh api "repos/phdkimworld/kimworld-site/actions/workflows/threads-drkim.yml/runs?per_page=1" -q '.workflow_runs[0].id')
  for j in $(gh api repos/phdkimworld/kimworld-site/actions/runs/$RID/jobs -q '.jobs[].id'); do gh api repos/phdkimworld/kimworld-site/check-runs/$j/annotations -q '.[].message'; done
  ```
- 게시 규칙: 4.17 형식 안의 글은 승인 없이 자동 게시(운영자 2026-11-26 "형식만 승인, 이후 자동"), 형식 밖 글은 운영자에게 먼저 보여 준다. 영양제 글이면 건강월드 지침(`skill/health/HEALTH_CHANNEL.md` 2장 법·정책: 질병 예방·치료 암시 금지, 식약처 인정 문구만, 쿠팡 링크엔 대가성 문구)을 그대로 따른다. 링크에는 `utm_source=threads&utm_medium=post&utm_campaign=<주제>`.
- 401·`invalid_grant`·만료(60일 넘김)면 갱신으로는 안 살아난다 → 운영자에게 재발급 요청. **재발급 순서(실제로 해 본 길):**
  1. Meta 개발자 → phdkimworld-poster → 사용 사례 'Access the Threads API' → 설정 → **User Token Generator** → drkimworld **Generate Access Token**.
  2. 이 버튼은 **작은 팝업 창**에서 승인해야 토큰이 원래 화면에 뜬다. **휴대폰 브라우저·같은 탭 승인은 흰 화면만 나온다**(팝업과 원래 창이 이어져야 함). 데스크톱 크롬에서 할 것.
  3. 그 크롬의 Threads 웹이 **@drkimworld로 로그인**돼 있어야 한다(@phdkimworld면 다른 계정으로 승인됨). 크롬에 인스타 @drkimworld 세션이 있으면 Threads 로그인 화면의 drkimworld 버튼으로 비밀번호 없이 들어간다.
  4. 팝업 'Continue As drkimworld'는 세션이 누를 수 없다(확장 탭 묶음 밖 창) → 운영자가 누른다. 토큰 복사·GitHub 비밀값 붙여넣기도 운영자 몫(세션은 토큰을 입력·출력하지 않는다). GitHub 비밀값 화면이 404면 로그인이 안 된 것.
  5. 넣은 뒤 세션이 ping으로 확인.
- 운영자 맥 두 대 모두 Claude in Chrome이 붙어 있다(list_connected_browsers의 Browser 1·2). 운영자가 원격으로 보는 맥이 어느 쪽인지 먼저 확인하고 그 브라우저를 고른다(2026-11-25 Browser 1이 원격 화면 맥).

# 블로거

## 8. 토큰
- Google OAuth 갱신 토큰 방식(유튜브 3장과 같은 원리, 범위는 `https://www.googleapis.com/auth/blogger`). 클라이언트 비밀번호는 `BLOGGER_CLIENT_SECRET` 또는 `GOOGLE_CLIENT_SECRET` 중 맞는 쪽을 스크립트가 차례로 시도한다.
- `invalid_grant`면 사이트 docs/blogger-guide.md의 재발급 순서대로 운영자가 새 갱신 토큰을 받아 `BLOGGER_REFRESH_TOKEN`을 바꾼다. 하루 게시 한도(`BLOGGER_DAILY`, 기본 2)는 운영자 동의 없이 올리지 않는다.

# 텔레그램

## 9. 봇 토큰
- `TELEGRAM_BOT_TOKEN` 봇이 채널 @drkimworld의 관리자이며 '메시지 게시' 권한이 있어야 한다. 실패가 `403 not enough rights`면 채널 관리자 설정에서 봇 권한을 다시 켠다.
- 토큰이 새었으면 BotFather `/revoke`로 폐기하고 새 토큰을 비밀값에 넣는다.

# 점검 주기
- 매일: hourly.py가 유튜브·Threads·인스타·페이스북 댓글을 읽으면서 실패를 줄에 남긴다. '토큰 확인 실패'·401·403이 보이면 그 채널 장을 보고 운영자에게 알린다.
- 매주 월요일: social.yml ping(Threads·인스타).
- 매달 1·15일: token-refresh.yml 결과 확인(실패면 7장).
