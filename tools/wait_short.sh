#!/bin/sh
# 4분 30초 안에서만 기다린다(11-16 토큰 측정: 5분 넘게 놀면 프롬프트 캐시가 식어 문맥 전체 약 35~50만 토큰을 다시 씀 — 회차 비용의 30~36%).
# 사용: sh tools/wait_short.sh '<끝났는지 판정하는 셸 조건>' [최대초=270]
#   예: sh tools/wait_short.sh 'grep -qE "CHAIN_DONE|CHAIN_FAIL" video/chain.log'
# 출력 한 줄: DONE(조건 참, exit 0) 또는 PENDING(시간 다 됨, exit 3 — 같은 명령을 곧바로 다시 부른다)
C=$1; M=${2:-270}; T0=$(date +%s)
until sh -c "$C" >/dev/null 2>&1; do
  [ $(( $(date +%s) - T0 )) -ge "$M" ] && { echo "PENDING $(( $(date +%s) - T0 ))s"; exit 3; }
  sleep 10
done
echo "DONE $(( $(date +%s) - T0 ))s"
