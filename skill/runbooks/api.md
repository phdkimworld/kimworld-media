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
- GitHub 예약 실행은 몇 시간씩 밀린다(comment-ai는 매시 예약인데 실제 6~10시간 간격). 그래서 매시 댓글 점검이 3시간마다 `comment-ai.yml`도 실행 요청한다. 제작 에이전트는 리포트 push 뒤 judge 결과를 `llm_judge.py --wait`로 받아 반영한다.
- 실행 요청 뒤 기다릴 때는 결과 파일을 `git pull`로 확인하고, 270초 단위로 끊어 기다린다(`tools/wait_short.sh`).

## 3. 예산 (사이트 `scripts/llm.py` BUDGETS, 월 단위)
- comments 40달러 · judge 25달러 · weekly 10달러 · 전체 상한 120달러. 사이트 '리포트에 질문하기'는 워커가 따로 관리(월 80달러).
- 현황: 사이트 저장소에서 `git pull` 뒤 `python3 scripts/llm.py status`. 예산을 넘으면 그 기능만 건너뛰고(status budget) 세션이 예전 방식으로 처리한다.
- 예산 숫자는 운영자 지시가 있을 때만 바꾼다.

## 4. 새 기능을 API로 옮길 때
- 맡겨도 되는 일: 분류·검출·초안처럼 **결과를 규칙 검사로 거를 수 있는 일**(예: 발행 전 심사, 정해진 형식의 짧은 답글 초안, 긴 원문에서 정해진 항목 찾기).
- 맡기지 않는 일: 대본·리포트 본문 집필, 숫자·사실의 최종 판단, 투표·종목 요청·대댓글·AI 질문 답글, 인스타 댓글, 비밀값이 필요한 일.
- 만드는 법: `llm.ask("<기능>", system=..., user=..., tier="cheap"|"judge", schema=...)`. BUDGETS에 기능을 추가하고, 워크플로 하나(`workflow_dispatch` 포함)를 만들고, 결과는 저장소 파일로 커밋(`python3 scripts/llm.py commit`). 키·크레딧·예산이 없으면 실패가 아니라 건너뜀으로 끝낸다. `python3 tests/test_llm.py`(모의 응답)와 사이트 test_build·build --strict 통과 뒤 push.
- 모델 이름은 코드(`scripts/llm.py` MODELS)에만 둔다. 공개 글·커밋 메시지에 쓰지 않는다.
