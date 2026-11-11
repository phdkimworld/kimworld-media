#!/usr/bin/env bash
# 회차 작업 중간 저장(컨테이너는 재시작되면 저장소를 새로 받아 오므로 디스크의 모든 것이 사라진다. 원격 git만 남는다 — 11-11 RUM 유실).
# 텍스트 산출물(조사·리포트 원고·차트 데이터·대본·slides.json·설명·첫 댓글·메타·쇼츠 대본)과 맥 TTS 작업 번호를
# 미디어 저장소 production/wip/<티커>/ 에 복사해 커밋·푸시한다. 큰 영상·음성은 넣지 않는다(음성은 중계 runs 브랜치에 남아 있음).
# 사용: bash tools/wip_save.sh <티커> [작업폴더(기본 /home/claude/<티커소문자>)] [메모]
set -e
T=$(echo "$1" | tr a-z A-Z); t=$(echo "$1" | tr A-Z a-z); D=${2:-/home/claude/$t}; NOTE=${3:-}
M=/home/user/kimworld-media; W=$M/production/wip/$T
[ -d "$D" ] || { echo "WIP_SKIP 폴더 없음 $D"; exit 0; }
mkdir -p $W
( cd "$D" && find . -type f \( -name '*.md' -o -name '*.txt' -o -name '*.json' -o -name '*.yaml' -o -name '*.svg' -o -name '*.html' \) \
    -size -2M -not -path './*/slides_out/*' -not -path './*/frames/*' -print0 | xargs -0 -I{} cp --parents {} $W/ )
date -u +%FT%TZ > $W/.saved_at; [ -n "$NOTE" ] && echo "$NOTE" >> $W/.notes
cd $M && git add production/wip/$T && git -c user.name=phdkimworld commit -q -m "WIP $T 중간 저장${NOTE:+: $NOTE}

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01DaUBsG9X6bLavyZrFguf5X" || { echo "WIP_NOCHANGE"; exit 0; }
for i in 1 2 3 4; do git pull -q --rebase --autostash origin claude/kim-world-stock-studio-laes-ovy09b && git push -q origin claude/kim-world-stock-studio-laes-ovy09b && break; sleep $((i*2)); done
echo "WIP_SAVED $T $(find $W -type f | wc -l) files"
