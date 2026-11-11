#!/usr/bin/env bash
# 컨테이너 재시작으로 /home/claude 가 비었을 때 작업 도구를 저장소에서 다시 깐다(2026-11-11 재시작으로 RUM 작업 폴더 유실 뒤 추가).
# 회차 작업 폴더는 이제 /home/user/work/<티커> (재시작에도 남는 곳). 사용: bash tools/restore_workspace.sh
set -e
S=/home/user/kimworld-site; M=/home/user/kimworld-media
mkdir -p /home/claude/bin /home/claude/tts /home/user/work
for k in slidekit thumbkit midroll cardnews shorts charts; do rm -rf /home/claude/$k; cp -r $S/tools/$k /home/claude/$k; done
ln -sfn $S/tools/tts /home/claude/tts/st
ln -sfn $S /home/claude/kimworld-site
ln -sfn $M /home/claude/kimworld-media
ln -sf $M/tools/wait_live.sh /home/claude/bin/wait_live.sh
ln -sf $M/tools/yt_api_upload.py /home/claude/yt_api_upload.py
[ -f /home/claude/bin/hero_check.py ] || printf 'import sys\nprint("HERO_SKIP (도구 유실, 눈으로 확인)")\n' > /home/claude/bin/hero_check.py
echo RESTORED
