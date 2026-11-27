# 디자인 관련 스킬 정리 (11-27 기준)

운영자가 공유한 디자인 스킬과 김박사 월드 반영 상태를 한곳에 모았다. 외부 코드는 설치하거나 실행하지 않고, 규칙만 옮긴다.

## 반영함
| 스킬 | 무엇 | 라이선스 | 우리 쪽 위치 |
|---|---|---|---|
| impeccable (pbakaus) | 웹 디자인 다듬기·검토 명령, AI 티 디자인 규칙 | Apache-2.0 | taste.md 13절 체크리스트, tools/thumb_taste_check.py |
| unslop (heydamir) | AI 같은 화면의 티 목록, 고치는 순서 | CC BY 4.0 | taste.md 13절(테두리+그림자 카드, 색 바탕 위 회색, 크기 위계) |
| 대형 채널 연구(11-24) | 썸네일·슬라이드·SNS 디자인 | — | review/design_study.md, slide_design_study.md, sns_design_study.md, thumbkit V5.7·slidekit 개편 |

## 진행 중(사이트 스타일 시안 A·B에 참고로 넘김)
| 스킬 | 무엇 | 반영 방식 |
|---|---|---|
| frontend-design (anthropics/skills) | 뻔한 AI 화면 피하기: 분명한 미적 방향, 개성 있는 글꼴, 일관된 색 | 시안 원칙 |
| ui-ux-pro-max (nextlevelbuilder) | 글자 크기 단계·간격·대비·금융·데이터 화면 패턴 | 시안 규칙 |
| Claude 디자인 세트(Brutalism·Nature Distilled 등) | 이름 붙은 스타일로 같은 내용을 다시 디자인 | 시안 A 브루탈리즘 / B 에디토리얼 |
| brandkit·brandkit-sync·theme-factory | 색·글꼴·크기를 한 파일로, 여러 곳에서 재사용 | 시안의 브랜드 값 파일 하나, 슬라이드·썸네일과 다른 값 목록 |

## 다음에 쓸 것
| 스킬 | 언제 |
|---|---|
| design-motion·animate·taste-skill | 슬라이드 '움직임이 짧다' 숙제를 고칠 때 점검 기준으로 |
| playwright-mcp 방식(브라우저로 보며 고치기) | 이미 Playwright 스크린샷으로 확인 중 — 그대로 |
| slide-decks·hi-fi-mockups | 필요할 때 Artifact 슬라이드·디자인 유형으로 대신 |

## 쓰지 않음
| 스킬 | 이유 |
|---|---|
| nano-banana·banana-claude(이미지 생성) | 외부 서비스로 보내야 하고, 썸네일은 실제 숫자 중심 |
| remotion·claude-remotion·blender-motion·ae-motion | 영상 도구를 바꾸면 위험이 큼(지금: 슬라이드 렌더링 + ffmpeg) |
| figma-mcp·figma-implement | 피그마를 쓰지 않음 |
| canvas-design·algorithmic-art·generative-ui | 금융 리포트 브랜드와 맞지 않음 |
| unslop·impeccable의 웹 전용 항목(보라 그라데이션, Inter 등 글꼴, 제목 굵기 400~500) | 우리는 네온 + 900 굵기 |

## 같이 쓰는 글쓰기 쪽(디자인 아님, 참고)
im-not-ai·humanizer → tools/ai_tells.py, taste.md 13절 · content-skills 5종 → taste.md 14절(김박사 목소리)
