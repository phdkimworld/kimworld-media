#!/usr/bin/env bash
# 리포트 주소가 실제로 열렸는지(HTTP 200 + 종목명 포함) 최대 40분 확인. 사용: wait_live.sh <slug> <종목명>
# 11-28: 404 페이지 본문에도 종목명이 들어 있어 LIVE로 잘못 판정 → HTTP 코드를 함께 본다
slug=$1; name=$2; url="https://drkimworld.com/r/$slug/"
t=$(mktemp)
for i in $(seq 1 80); do
  code=$(curl -s -o "$t" -w '%{http_code}' -A 'Mozilla/5.0 research' "$url?t=$(date +%s)")
  if [ "$code" = 200 ] && grep -q "$name" "$t"; then rm -f "$t"; echo "LIVE $url"; exit 0; fi
  sleep 30
done
rm -f "$t"; echo "NOT_LIVE $url (last HTTP $code)"; exit 1
