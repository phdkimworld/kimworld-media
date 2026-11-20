#!/bin/bash
# 사이트(main) 안전 push (2026-11-20 운영자 "해결해")
# 문제: test_build가 약 20분 걸리는 사이 원격에 봇 커밋(하루 40건 이상: social/posted·open·llm·telegram, health 등)이
#   들어와 push가 거절되고, 다시 test_build를 돌리는 사이 또 들어와 영상 ID 연결이 2시간 늦어졌다(ENVX 11-20).
# 해법: 검사를 통과한 뒤 원격에서 새로 들어온 변경이 '빌드·검사와 무관한 기록 경로'뿐이면 다시 검사하지 않고
#   rebase 후 곧바로 push한다. 그 밖의 경로(코드·템플릿·리포트·social/queue·mall 등)가 바뀌었으면 exit 3 → test_build 다시.
# 사용: (사이트 저장소나 worktree 안에서, test_build·build --strict 통과 직후) bash /home/user/kimworld-media/tools/site_push.sh
set -u
SAFE='^(social/(posted|open|llm|telegram|blogger|replies|site_replies|insights)/|health/|stats/)'
for try in 1 2 3 4 5; do
  git fetch -q origin main || { sleep 5; continue; }
  base=$(git merge-base HEAD origin/main)
  incoming=$(git diff --name-only "$base" origin/main)
  if [ -n "$incoming" ]; then
    unsafe=$(printf '%s\n' "$incoming" | grep -Ev "$SAFE" || true)
    if [ -n "$unsafe" ]; then
      echo "RETEST: 원격에 빌드 관련 변경이 있음 → git pull --rebase 후 test_build 다시"
      printf '%s\n' "$unsafe" | head -10
      exit 3
    fi
    git rebase -q origin/main || { git rebase --abort; echo "REBASE_CONFLICT"; exit 4; }
  fi
  if git push -q origin HEAD:main; then echo "PUSHED (원격 새 변경: 기록 경로 $(printf '%s\n' "$incoming" | grep -c . ) 파일)"; exit 0; fi
  sleep $((try * 3))
done
echo "PUSH_FAILED"; exit 1
