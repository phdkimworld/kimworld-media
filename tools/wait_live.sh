#!/usr/bin/env bash
# 리포트 주소가 실제로 열렸는지(200 + 종목명 포함) 최대 40분 확인. 사용: wait_live.sh <slug> <종목명>
slug=$1; name=$2; url="https://drkimworld.com/r/$slug/"
for i in $(seq 1 80); do
  body=$(curl -s -A 'Mozilla/5.0 research' "$url?t=$(date +%s)")
  if [ -n "$body" ] && echo "$body" | grep -q "$name"; then echo "LIVE $url"; exit 0; fi
  sleep 30
done
echo "NOT_LIVE $url"; exit 1
