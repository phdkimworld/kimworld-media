# 유튜브 채널 접근 권한 지침 (2026-11-19 운영자 지시 "유튜브 채널 접근 권한 지침 작성")

모든 세션과 에이전트가 유튜브 채널(@drkimworld)에 어떤 권한으로 접근하는지, 키를 어디에 두는지, 권한을 넓히거나 다시 발급할 때 무엇을 하는지 적은 문서다. 키 값은 이 문서와 채팅, 커밋, 로그 어디에도 적지 않는다.

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
