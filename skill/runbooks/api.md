# Anthropic API 크레딧 쓰는 법 (모든 세션·에이전트 공통, 운영자 지시 2026-11-17 "다른 세션에서도 쓰게")

목적: 세션 토큰을 아끼기 위해, 규칙 검사로 결과를 거를 수 있는 기계적 LLM 일은 API 크레딧(저가 모델)으로 돌린다. 세션은 결과 파일만 읽는다.

## 1. 키는 어디에 있나
- 사이트 저장소 GitHub Actions 비밀값 `ANTHROPIC_API_KEY`(와 Cloudflare 워커)에만 있다. 세션 컨테이너에는 없다. `python3 scripts/llm.py status`가 `키: 없음(no_key)`이면 정상이다.
- 키를 세션·맥·다른 저장소로 옮기거나 출력하지 않는다. 그래서 API 호출은 **사이트 저장소 워크플로를 실행**하는 방식으로만 한다.

## 2. 지금 쓸 수 있는 것 (MCP `actions_run_trigger`, run_workflow, phdkimworld/kimworld-site, ref main)
| 워크플로 | 하는 일 | 입력 | 결과 읽기 |
|---|---|---|---|
| `judge.yml` | 발행 전 리포트 심사(가독성·AI 느낌). 리포트를 main에 push하면 자동 | `{slug}`(다시 심사할 때만) | 사이트 `social/llm/judge/<slug>.md`, 미디어 `python3 tools/llm_judge.py <slug> --wait 10` |
| `comment-ai.yml` | 유튜브·Threads·페이스북 첫 댓글 중 질문·의견에 답글(리포트 근거, 규칙 검사 통과분만 게시) | 없음(`max`, `dry`는 선택) | 사이트 `social/llm/comments/state.json`: posted는 hourly.py가 건너뛰고 left는 세션에 넘김 |
| `weekly-ai.yml` | 월요일 주간 분석 | 없음 | 커밋된 주간 메모 |
| `anthropic-check.yml` | 키·크레딧 상태 | 없음 | 실행 요약 `STATUS=ok / no_credit / no_key` |
| `extract.yml` | (11-27) 공시·IR 페이지 → 숫자 표 JSON(doc·date·form·item·amount·unit·shares·price·quote≤15단어·url, `quote_found`로 원문 대조) | `{slug, urls(https 쉼표 ≤6), preset:"filing", focus?}` | 사이트 `social/llm/extract/<slug>.json` |
| `sns-draft.yml` | (11-27) 리포트 → Threads th1/th2(+관찰 글)·인스타/페북 릴스 캡션 초안, queue_check T20·S1·AD2·self_reply 사본(`scripts/sns_rules.py`) 검사, 걸리면 한 번 고쳐 받음 | `{slug, facts?, observe?:"1"}` | 사이트 `social/llm/sns/<slug>.json`(`files`·`problems`) — 대기열 아님 |
| `blogger-draft.yml` | (11-27) 리포트 → 머리말 `blog_slug`·`blog_intro`·`blog_faq` 초안, K10·v2.9 금지어·lint·지어낸 숫자·본문 700자 검사 | `{slug}` | 사이트 `social/llm/blogger/<slug>.md` |
| `llm-task.yml` | (11-27) 다른 세션 공용 범용 작업(저가 모델 1회) | `{task, prompt(≤4,000자) 또는 prompt_path(llm-tasks/…), schema_path?, max_tokens≤4000, caller?}` | 사이트 `social/llm/tasks/<task>-<run_id>.json` |
- 위 넷은 모두 `dry: "1"`(모의 응답, 커밋 없음, 크레딧 0)이 있다. 하루 호출 상한 extract 10 · sns 8 · blogger 8 · shared 20(모든 세션 합), 실행당 1·2·2·1회. 기록 `social/llm/runs/<UTC 날짜>/`.
- **2026-11-27 운영자 "다 옮겨. 다른 세션에서도 좀 쓰게 접근 지침 작성해"**: 세션 토큰을 많이 쓰던 공시 표 뽑기·SNS 초안·블로거 머리말 초안을 API로 옮기고 공용 통로(llm-task)를 열기로 운영자가 승인함(예산 추가 포함).
- GitHub 예약 실행은 몇 시간씩 밀린다(comment-ai는 매시 예약인데 실제 6~10시간 간격). 그래서 매시 댓글 점검이 3시간마다 `comment-ai.yml`도 실행 요청한다. 제작 에이전트는 리포트 push 뒤 judge 결과를 `llm_judge.py --wait`로 받아 반영한다.
- 실행 요청 뒤 기다릴 때는 결과 파일을 `git pull`로 확인하고, 270초 단위로 끊어 기다린다(`tools/wait_short.sh`).

## 2-1. 운영 숫자는 요약 한 장부터 (2026-11-17 "주간한도 사용을 줄여")
- 사이트 통계·수익·실험 현황이 필요하면 비공개 저장소 `phdkimworld/kimworld`(ops-data) **`stats/digest.md`** 를 먼저 읽는다. `analytics-report.yml` 실행 때마다 LLM 없이 스크립트(`scripts/ops_digest.py`)가 만든다(7일 핵심·채널·투표·애드핏·쿠팡 하위 ID·유튜브 쿠팡 실험·블로거 비교 글·애드센스 기준·이상 신호).
- `stats/analytics.json` 같은 큰 JSON은 요약에 없는 값이 꼭 필요할 때만 jq로 그 값만 뽑는다.

## 3. 예산 (사이트 `scripts/llm.py` BUDGETS, 월 단위)
- comments 40 · judge 25 · weekly 10 · extract 15 · sns 10 · blogger 5 · shared 20달러(11-27 운영자 승인으로 넷 추가) · 전체 상한 120달러 그대로(기능별 합 125가 넘어도 120에서 모두 멈춤). 사이트 '리포트에 질문하기'는 워커가 따로 관리(월 80달러).
- 현황: 사이트 저장소에서 `git pull` 뒤 `python3 scripts/llm.py status`. 예산을 넘으면 그 기능만 건너뛰고(status budget) 세션이 예전 방식으로 처리한다.
- 예산 숫자는 운영자 지시가 있을 때만 바꾼다.

## 4. 새 기능을 API로 옮길 때
- 맡겨도 되는 일: 분류·검출·초안처럼 **결과를 규칙 검사로 거를 수 있는 일**(예: 발행 전 심사, 정해진 형식의 짧은 답글 초안, 긴 원문에서 정해진 항목 찾기).
- 맡기지 않는 일: 대본·리포트 본문 집필, 숫자·사실의 최종 판단, 투표·종목 요청·대댓글·AI 질문 답글, 인스타 댓글, 비밀값이 필요한 일.
- 만드는 법: `llm.ask("<기능>", system=..., user=..., tier="cheap"|"judge", schema=...)`. BUDGETS에 기능을 추가하고, 워크플로 하나(`workflow_dispatch` 포함)를 만들고, 결과는 저장소 파일로 커밋(`python3 scripts/llm.py commit`). 키·크레딧·예산이 없으면 실패가 아니라 건너뜀으로 끝낸다. `python3 tests/test_llm.py`(모의 응답)와 사이트 test_build·build --strict 통과 뒤 push.
- 모델 이름은 코드(`scripts/llm.py` MODELS)에만 둔다. 공개 글·커밋 메시지에 쓰지 않는다.

## 5. 제작자가 쓰는 법 (11-27, 단계마다 한 줄 — production.md 4) 제작에도 같은 줄)
- 조사: 공시·IR 원문을 세션에서 통째로 읽기 전에 `extract.yml {slug, urls}` → `jq -r '.rows[]|[.date,.form,.item,.amount,.unit,.shares,.price,.quote_found]|@tsv' social/llm/extract/<slug>.json`으로 표만 읽고, 핵심 숫자 2~3개(특히 `quote_found:false`)는 원문에서 grep으로 직접 확인한다.
- 리포트 발행 뒤 SNS: `sns-draft.yml {slug}`(관찰 글이 필요하면 `observe:"1"`) → `jq '.status,.problems'` 확인 → `jq '.files["<파일>"]'`로 꺼내 검토·💊 광고 문단(tools/product_link.py)·th1/릴스 `publish_at` 채움 → `social/queue/`로 옮기고 `tools/queue_check.py` 전체 통과(사본 검사는 부분집합).
- 블로거: `blogger-draft.yml {slug}` → `social/llm/blogger/<slug>.md`의 yaml 블록을 검토해 리포트 머리말에 붙이고 easy_check K10 통과(공개 뒤 blog_slug 변경 금지).
- 결과가 `no_key`·`no_credit`·`budget`·`daily_cap`이면 지금처럼 세션이 직접 쓴다.

## 6. 다른 세션에서 쓰는 법 (healthworld·다른 팀 공통, 전문: 사이트 저장소 [`docs/LLM_ACCESS.md`](https://github.com/phdkimworld/kimworld-site/blob/main/docs/LLM_ACCESS.md) — 미디어 저장소가 없는 세션은 그 파일만 읽으면 된다)
- 준비: GitHub MCP 도구(`actions_run_trigger`·`get_file_contents`)와 `phdkimworld/kimworld-site` 접근. 저장소가 없으면 `add_repo {"owner":"phdkimworld","repo":"kimworld-site","access":"push"}`(미리 curl로 확인하지 말 것, 거절 사유는 그대로 운영자에게). 키는 세션에 없는 것이 정상.
- 실행 요청(ref 는 언제나 main):
  `{"method":"run_workflow","owner":"phdkimworld","repo":"kimworld-site","ref":"main","workflow_id":"llm-task.yml","inputs":{"task":"hw-faq-tone","prompt":"…","max_tokens":"800","caller":"healthworld"}}`
  긴 프롬프트·JSON 답은 `llm-tasks/<task>.md`(+ `llm-tasks/<task>.schema.json`, 모든 object에 `additionalProperties:false`)를 main에 커밋하고 `"prompt_path":"llm-tasks/<task>.md","schema_path":"llm-tasks/<task>.schema.json"`.
- 결과: 1~3분 뒤 한 번(짧은 간격 확인 금지) `git pull -q --rebase origin main` → `jq -r '.status,.error,.text' social/llm/tasks/<task>-<run_id>.json`(JSON 답은 `.json`). 복제본이 없으면 `get_file_contents`로 그 파일만. run_id 는 `actions_list list_workflow_runs resource_id llm-task.yml perPage 3`.
- 예산·상한: shared 20달러/월, 하루 20회(모든 세션 합), 실행당 1회, max_tokens ≤4000. 현황 `python3 scripts/llm.py status`, 오늘 횟수 `ls social/llm/runs/$(date -u +%F)/`.
- 보내면 안 되는 것: 비밀값(키·토큰·비밀번호 — 모양이 보이면 워크플로가 `refused`로 막음), 개인정보(실명·이메일·전화·주민번호·환자/고객 기록·운영자 신상·종목 보유), 공개 전 민감한 숫자, 남의 유료 리포트 원문. 결과는 저장소에 커밋되어 남는다.
- 비용 예절: 작은 질문은 묶어서 한 번에, 자료는 필요한 부분만, 같은 요청 되풀이 금지(결과 파일 다시 읽기), 처음 쓰는 형식은 `dry:"1"`로 먼저, 예산이 모자라면 숫자를 고치지 말고 운영자에게 보고.
