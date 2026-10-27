#!/bin/sh
# 롱폼 제작의 긴 단계를 끊김 없이 잇는다(운영자 지시 2026-10-20 "이런 일 없게 해" — TTS가 끝났는데 25분 멈춰 있었음).
# 사용: sh tools/chain_long.sh <작업 폴더(video)> [쇼츠 폴더]
#   TTS 끝 대기 → check_slides·still_check·num_check·prev_calls_check·thumb_biz_check·thumb_name_check·hero_check → 롱폼 합성 → video_check long
#   (쇼츠 폴더가 있으면) shorts_check → 쇼츠 TTS → 렌더 → video_check shorts 를 이어서 돌린다.
# 반드시 세션 도구의 '백그라운드 실행(완료 알림)'으로 부른다. nohup 만으로 띄우고 끝내지 않는다.
set -u
V=$1; S=${2:-}
until grep -q "^done" "$V/tts.log" 2>/dev/null; do
  grep -q "Traceback\|Error" "$V/tts.log" 2>/dev/null && { echo "CHAIN_FAIL tts"; tail -5 "$V/tts.log"; exit 1; }
  sleep 15
done
echo "TTS 끝: $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V/raw.wav")초"
if [ -n "$S" ] && [ -f "$S/narration.txt" ]; then
  python3 /home/user/kimworld-media/tools/shorts_check.py "$S" || { echo "CHAIN_FAIL shorts_check(쇼츠 문장·장면 수)"; exit 1; }
  # 이미 녹음된 쇼츠 음성(대본보다 새 wav + tts.log 'done')은 다시 녹음하지 않는다(10-27 XNDU: 재실행마다 쇼츠 TTS가 다시 돌아 기다림이 꼬임)
  if [ -f "$S/shorts_raw.wav" ] && [ "$S/shorts_raw.wav" -nt "$S/narration.txt" ] && grep -q "^done" "$S/tts.log" 2>/dev/null; then
    echo "쇼츠 TTS 건너뜀: 기존 음성 사용"
  else
    (cd /home/claude/tts/st && python3 st_tts.py "$S/narration.txt" "$S/shorts_raw.wav" 6 1.15 10 > "$S/tts.log" 2>&1) &
  fi
fi
cd "$V"
python3 /home/claude/slidekit/check_slides.py . > check_slides.log 2>&1; tail -1 check_slides.log | grep -q OK || { echo "CHAIN_FAIL check_slides"; grep -v "^ad " check_slides.log | tail -8; exit 1; }
python3 /home/user/kimworld-media/tools/still_check.py . || { echo "CHAIN_FAIL still_check(합성 전 정지 화면 위험)"; exit 1; }
R=$(ls ../report/*-20*.md 2>/dev/null | head -1)
if [ -n "$R" ]; then
  python3 /home/user/kimworld-media/tools/num_check.py slides.json "$R" > num_check.log 2>&1 || { echo "CHAIN_FAIL num_check(화면 숫자가 리포트에 없음·계산 불일치)"; cat num_check.log | tail -10; exit 1; }
  tail -1 num_check.log
else
  echo "num_check 건너뜀: ../report/*.md 없음"
fi
if [ -n "$R" ]; then
  RS="/home/user/kimworld-site/content/reports/$(basename "$R")"; [ -f "$RS" ] || RS="$R"
  python3 /home/user/kimworld-media/tools/prev_calls_check.py . "$RS" || { echo "CHAIN_FAIL prev_calls_check(지난 예측 성적표·시나리오 가능성, 운영자 지시 10-25)"; exit 1; }
fi
python3 /home/user/kimworld-media/tools/thumb_biz_check.py thumb/custom || { echo "CHAIN_FAIL thumb_biz_check(썸네일에 사업 시각화 없음, 운영자 지시 10-24)"; exit 1; }
python3 /home/user/kimworld-media/tools/thumb_name_check.py thumb/custom || { echo "CHAIN_FAIL thumb_name_check(썸네일 회사명 72px·티커 60px 이상, 운영자 지시 10-27)"; exit 1; }
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
