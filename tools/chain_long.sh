#!/bin/sh
# 롱폼 제작의 긴 단계를 끊김 없이 잇는다(운영자 지시 2026-10-20 "이런 일 없게 해" — TTS가 끝났는데 25분 멈춰 있었음).
# 사용: sh tools/chain_long.sh <작업 폴더(video)> [쇼츠 폴더]
#   TTS 끝 대기 → check_slides·hero_check → 롱폼 합성 → video_check long
#   (쇼츠 폴더가 있으면) 쇼츠 TTS → 렌더 → video_check shorts 를 이어서 돌린다.
# 반드시 세션 도구의 '백그라운드 실행(완료 알림)'으로 부른다. nohup 만으로 띄우고 끝내지 않는다.
set -u
V=$1; S=${2:-}
until grep -q "^done" "$V/tts.log" 2>/dev/null; do
  grep -q "Traceback\|Error" "$V/tts.log" 2>/dev/null && { echo "CHAIN_FAIL tts"; tail -5 "$V/tts.log"; exit 1; }
  sleep 15
done
echo "TTS 끝: $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V/raw.wav")초"
if [ -n "$S" ] && [ -f "$S/narration.txt" ]; then
  (cd /home/claude/tts/st && python3 st_tts.py "$S/narration.txt" "$S/shorts_raw.wav" 6 1.15 10 > "$S/tts.log" 2>&1) &
fi
cd "$V"
python3 /home/claude/slidekit/check_slides.py . > check_slides.log 2>&1; tail -1 check_slides.log | grep -q OK || { echo "CHAIN_FAIL check_slides"; grep -v "^ad " check_slides.log | tail -8; exit 1; }
python3 /home/claude/bin/hero_check.py . | tail -1
T=$(python3 -c "import json;print(json.load(open('slides.json'))['ticker'])")
nice -n 10 python3 /home/claude/slidekit/make_slide_video.py slides.json raw.wav "${T}_slide_video.mp4" > synth.log 2>&1 || { echo "CHAIN_FAIL synth"; tail -5 synth.log; exit 1; }
tail -1 synth.log
python3 mk_meta.py > /dev/null && python3 /home/user/kimworld-media/tools/video_check.py long "${T}_slide_video.mp4" slides.json upload_meta.json 2>&1 | tail -3
if [ -n "$S" ]; then
  wait
  cd "$S" && python3 /home/user/kimworld-site/tools/shorts/make_shorts.py shorts.json shorts_raw.wav "${T}_shorts.mp4" > render.log 2>&1; tail -1 render.log
  python3 mk_meta.py PLACEHOLDER > /dev/null && python3 /home/user/kimworld-media/tools/video_check.py shorts "${T}_shorts.mp4" shorts.json upload_meta.json 2>&1 | tail -2
fi
echo CHAIN_DONE
