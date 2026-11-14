#!/bin/sh
# 롱폼 제작의 긴 단계를 끊김 없이 잇는다(운영자 지시 2026-10-20 "이런 일 없게 해" — TTS가 끝났는데 25분 멈춰 있었음).
# 사용: sh tools/chain_long.sh <작업 폴더(video)> [쇼츠 폴더]
#   TTS 끝 대기 → tts_asr_check → check_slides·still_check·num_check·prev_calls_check·thumb_biz_check·chart_check·thumb_name_check·hero_check → 롱폼 합성 → video_check long
#   (쇼츠 폴더가 있으면) shorts_check → 쇼츠 TTS → 렌더 → video_check shorts 를 이어서 돌린다.
# 반드시 세션 도구의 '백그라운드 실행(완료 알림)'으로 부른다. nohup 만으로 띄우고 끝내지 않는다.
set -u
# 합성의 numpy 효과음 섞기가 다른 제작과 겹치면 OpenBLAS 스레드가 서로 기다려 50분 넘게 멈춤(74회차 PLUG, 평소 4분) → 한 스레드로
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
V=$1; S=${2:-}
until grep -q "^done" "$V/tts.log" 2>/dev/null; do
  grep -q "Traceback\|Error" "$V/tts.log" 2>/dev/null && { echo "CHAIN_FAIL tts"; tail -5 "$V/tts.log"; exit 1; }
  sleep 15
done
# 녹음 파일이 실제로 있나(80회차 CBRS: 맥 작업이 'venv 없음'으로 실패했는데 mac.py wait가 0으로 끝나 tts_mac.sh가 tts.log에 done을 적음 → 빈 녹음으로 다음 단계)
[ -s "$V/raw.wav" ] || { echo "CHAIN_FAIL tts_missing(tts.log는 done인데 raw.wav 없음 — mac_wait.log 확인 뒤 클라우드 TTS: cd /home/claude/tts/st && python3 st_tts.py narration.txt raw.wav 6 1.15 10)"; grep -h "✗\|exit" "$V/mac_wait.log" 2>/dev/null | tail -2; exit 1; }
echo "TTS 끝: $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V/raw.wav")초"
# 녹음이 지금 대본에서 나왔나(53회차 PLUG: TTS 시작 뒤 대본을 고쳐 다시 녹음) — 옛 녹음 + 새 slides.json 합성을 막는다
python3 /home/user/kimworld-media/tools/tts_fresh_check.py "$V" || { echo "CHAIN_FAIL tts_fresh_check(녹음과 대본 불일치 — st_redo 또는 TTS 재실행)"; exit 1; }
# E12 녹음 길이(BTQ 49회차: B그룹 녹음 9분 50초를 합성 뒤에야 알아 보강·재녹음). video 폴더에 group 파일(A|B)이 있으면 녹음 직후 확인
if [ -f "$V/group" ]; then
  G=$(tr -d ' \n' < "$V/group"); D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V/raw.wav" | cut -d. -f1)
  if [ "$G" = "B" ] && [ "$D" -lt 600 ]; then echo "CHAIN_FAIL tts_length(E12 B 녹음 ${D}초, 600초 이상 — 문단 보강 뒤 st_redo)"; exit 1; fi
  if [ "$G" = "A" ] && [ "$D" -gt 600 ]; then echo "CHAIN_FAIL tts_length(E12 A 녹음 ${D}초, 약 8분 목표 — 600초 이하)"; exit 1; fi
fi
if [ -n "$S" ] && [ -f "$S/narration.txt" ]; then
  python3 /home/user/kimworld-media/tools/shorts_check.py "$S" || { echo "CHAIN_FAIL shorts_check(쇼츠 문장·장면 수)"; exit 1; }
  python3 /home/user/kimworld-media/tools/script_audio_check.py "$S/narration.txt" || { echo "CHAIN_FAIL script_audio_check(쇼츠 대본 귀로 듣는 말)"; exit 1; }
  # 이미 녹음된 쇼츠 음성(대본보다 새 wav + tts.log 'done')은 다시 녹음하지 않는다(10-27 XNDU: 재실행마다 쇼츠 TTS가 다시 돌아 기다림이 꼬임)
  if [ -f "$S/shorts_raw.wav" ] && [ "$S/shorts_raw.wav" -nt "$S/narration.txt" ] && grep -q "^done" "$S/tts.log" 2>/dev/null; then
    echo "쇼츠 TTS 건너뜀: 기존 음성 사용"
  else
    (cd /home/claude/tts/st && python3 st_tts.py "$S/narration.txt" "$S/shorts_raw.wav" 6 1.15 10 > "$S/tts.log" 2>&1) &
  fi
fi
cd "$V"
# 녹음 숫자 듣기 검사(2026-10-29 CBRS '약 스물한 배'가 뭉개짐): 고칠 문단은 st_redo.py로 다시 녹음, 인식기 한계로 판단해 넘기면 asr_check.ok에 이유
if [ -f raw_timing.json ] && [ ! -f asr_check.ok ]; then
  python3 /home/user/kimworld-media/tools/tts_asr_check.py narration.txt raw.wav raw_timing.json > asr_check.log 2>&1 || { echo "CHAIN_FAIL tts_asr_check(녹음에서 숫자가 안 들림)"; grep -v LIMIT asr_check.log | tail -6; exit 1; }
  tail -1 asr_check.log
fi
python3 /home/claude/slidekit/check_slides.py . > check_slides.log 2>&1; tail -1 check_slides.log | grep -q OK || { echo "CHAIN_FAIL check_slides"; grep -v "^ad " check_slides.log | tail -8; exit 1; }
python3 /home/user/kimworld-media/tools/still_check.py . || { echo "CHAIN_FAIL still_check(합성 전 정지 화면 위험)"; exit 1; }
python3 /home/user/kimworld-media/tools/poll_sync_check.py . "$S" || { echo "CHAIN_FAIL poll_sync_check(투표 보기 25바이트·롱폼=쇼츠, 72회차 LCID 교훈)"; exit 1; }
# SNS 대기열 미리 검사(73회차 NBIS: queue_check 8건이 업로드 뒤에야 걸림) — ../sns/mk_queue.py가 있으면 가짜 폴더에서 queue_check
[ -f ../sns/mk_queue.py ] && { python3 /home/user/kimworld-media/tools/queue_dry.py ../sns/mk_queue.py || { echo "CHAIN_FAIL queue_dry(SNS 대기열 문구, 73회차 NBIS 교훈)"; exit 1; }; }
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
T=$(python3 -c "import json;print(json.load(open('slides.json'))['ticker'])"); if [ -f ../report/chart.json ] && [ -f ../research/$T.json ]; then python3 /home/user/kimworld-media/tools/chart_check.py ../report/chart.json ../research/$T.json || { echo "CHAIN_FAIL chart_check(차트 날짜·종가·거래일 라벨 ↔ 시세 원자료, 42회차 교훈)"; exit 1; }; fi
python3 /home/user/kimworld-media/tools/thumb_name_check.py thumb/custom || { echo "CHAIN_FAIL thumb_name_check(썸네일 회사명 72px·티커 60px 이상, 운영자 지시 10-27)"; exit 1; }
python3 /home/user/kimworld-media/tools/thumb_overflow_check.py thumb/custom || { echo "CHAIN_FAIL thumb_overflow_check(썸네일 글자 상자가 1280×720 밖, 82회차 ASST)"; exit 1; }
python3 /home/claude/bin/hero_check.py . | tail -1
T=$(python3 -c "import json;print(json.load(open('slides.json'))['ticker'])")
nice -n 10 python3 /home/claude/slidekit/make_slide_video.py slides.json raw.wav "${T}_slide_video.mp4" > synth.log 2>&1 || { echo "CHAIN_FAIL synth"; tail -5 synth.log; exit 1; }
tail -1 synth.log
# video_check 결과의 ✗를 CHAIN_FAIL로 올린다(11-05 IREN 58회차: 쇼츠 mk_meta.py가 없어 검사가 건너뛰어졌고, 정지 4.2초 쇼츠가 그대로 올라감)
[ -f mk_meta.py ] || { echo "CHAIN_FAIL long mk_meta.py 없음(video_check를 못 함)"; exit 1; }
python3 mk_meta.py > /dev/null && VC=$(python3 /home/user/kimworld-media/tools/video_check.py long "${T}_slide_video.mp4" slides.json upload_meta.json 2>&1); echo "$VC" | tail -3
echo "$VC" | grep -q "✗" && { echo "CHAIN_FAIL video_check long"; exit 1; }
if [ -n "$S" ]; then
  wait
  cd "$S" && python3 /home/user/kimworld-site/tools/shorts/make_shorts.py shorts.json shorts_raw.wav "${T}_shorts.mp4" > render.log 2>&1; tail -1 render.log
  [ -f mk_meta.py ] || { echo "CHAIN_FAIL shorts mk_meta.py 없음(쇼츠 video_check를 못 함 — 업로드 전에 만들 것)"; exit 1; }
  python3 mk_meta.py PLACEHOLDER > /dev/null && VC=$(python3 /home/user/kimworld-media/tools/video_check.py shorts "${T}_shorts.mp4" shorts.json upload_meta.json 2>&1); echo "$VC" | tail -2
  echo "$VC" | grep -q "✗" && { echo "CHAIN_FAIL video_check shorts"; exit 1; }
fi
echo CHAIN_DONE
