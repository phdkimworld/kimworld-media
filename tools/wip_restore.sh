#!/usr/bin/env bash
# 재시작 뒤 이어서 만들 때: production/wip/<티커>/ 를 작업 폴더로 되살린다. 사용: bash tools/wip_restore.sh <티커> [작업폴더]
set -e
T=$(echo "$1" | tr a-z A-Z); t=$(echo "$1" | tr A-Z a-z); D=${2:-/home/claude/$t}; W=/home/user/kimworld-media/production/wip/$T
[ -d $W ] || { echo "WIP_NONE $T"; exit 0; }
mkdir -p "$D" && cp -rn $W/. "$D"/ && echo "WIP_RESTORED $T → $D (저장 $(cat $W/.saved_at 2>/dev/null))"; cat $W/.notes 2>/dev/null | tail -3
