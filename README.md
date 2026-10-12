# kimworld-media

종목별 폴더(`<티커>/`)에 영상·썸네일 원본을 두고, `tools/yt_upload.py`로 유튜브에 올립니다.

## 유튜브 업로드 준비

환경변수 세 개만 있으면 됩니다(값은 절대 저장소에 커밋하지 않습니다).

| 이름 | 내용 |
|---|---|
| `YT_CLIENT_ID` | OAuth 클라이언트 ID |
| `YT_CLIENT_SECRET` | OAuth 클라이언트 보안 비밀 |
| `YT_REFRESH_TOKEN` | `youtube.upload` + `youtube.force-ssl` 권한으로 받은 refresh token |

- GitHub Actions: 저장소 Settings → Secrets and variables → Actions 에 위 세 이름으로 등록
- claude.ai/code 환경: 환경 설정의 Environment variables 에 `이름=값` 형식으로 등록

```
pip install google-api-python-client google-auth
```

## 영상 하나 바로 올리기

```
python tools/yt_upload.py --video inj/inj_slide_video.mp4 --title "제목" \
  --description "설명" --tags "주식,INJ" --privacy private \
  --thumbnail inj/inj_thumbnail.jpg --comment "첫 댓글"
```

- `--privacy`: `private`(기본) / `unlisted` / `public`
- `--thumbnail`, `--comment`는 빼도 됩니다.
- API 감사를 통과하기 전에는 공개로 올려도 YouTube가 비공개로 잠급니다.

## 폴더 단위 자동 업로드 (GitHub Actions)

`<티커>/upload.json`을 푸시하면 `.github/workflows/youtube-upload.yml`이 올리고 결과를 `<티커>/upload_result.json`에 남깁니다.

```json
{"title":"...", "description":"...", "tags":["..."], "categoryId":"27", "privacy":"public",
 "video":"inj_slide_video.mp4", "thumbnail":"inj_thumbnail.jpg", "first_comment":"...",
 "madeForKids":false, "publishAt":""}
```

`publishAt`(UTC, 예: `2026-10-13T00:00:00Z`)을 넣으면 비공개로 올린 뒤 그 시각에 공개됩니다.
