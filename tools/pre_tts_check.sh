#!/bin/sh
# 녹음과 상관없는 기계 검사를 TTS(맥) 제출 전에 한 번에 돌린다(11-16 토큰 측정: chain_long이 TTS 20~40분 뒤 첫 실패에서 멈춰
# 고치고 다시 기다리는 왕복이 캐시 재생성까지 불러 회차 비용의 큰 몫). 첫 실패에서 멈추지 않고 전부 돌려 실패 이름만 한 줄로.
# 사용: sh tools/pre_tts_check.sh <video 폴더> [쇼츠 폴더]   → PRE_OK n개 | PRE_FAIL a,b,…(자세한 건 <video>/pre_check.log)
# 녹음이 있어야 하는 검사(debreath·tts_asr_check·check_slides·still_check·hero_check·합성)는 chain_long.sh가 그대로 한다.
V=$(cd "$1" && pwd); S=${2:-}; [ -n "$S" ] && S=$(cd "$S" && pwd)
M=/home/user/kimworld-media/tools; L="$V/pre_check.log"; : > "$L"; F=""; N=0
c() { n=$1; shift; N=$((N+1)); echo "== $n" >> "$L"; "$@" >> "$L" 2>&1 || F="$F${F:+,}$n"; }
if [ -n "$S" ] && [ -f "$S/narration.txt" ]; then
  c shorts_check python3 $M/shorts_check.py "$S"
  c script_audio_check python3 $M/script_audio_check.py "$S/narration.txt"
fi
cd "$V"
c poll_sync_check python3 $M/poll_sync_check.py . "$S"
[ -f ../sns/mk_queue.py ] && c queue_dry python3 $M/queue_dry.py ../sns/mk_queue.py
R=$(ls ../report/*-20*.md 2>/dev/null | head -1)
if [ -n "$R" ]; then
  c prev_score_sync python3 $M/prev_score_sync_check.py .. "$R"
  c num_check python3 $M/num_check.py slides.json "$R"
  RS="/home/user/kimworld-site/content/reports/$(basename "$R")"; [ -f "$RS" ] || RS="$R"
  c prev_calls_check python3 $M/prev_calls_check.py . "$RS"
fi
c krw_unit_check python3 $M/krw_unit_check.py .
c thumb_biz_check python3 $M/thumb_biz_check.py thumb/custom
T=$(python3 -c "import json;print(json.load(open('slides.json'))['ticker'])" 2>/dev/null)
[ -f ../report/chart.json ] && [ -f "../research/$T.json" ] && c chart_check python3 $M/chart_check.py ../report/chart.json "../research/$T.json"
c thumb_name_check python3 $M/thumb_name_check.py thumb/custom
c thumb_overflow_check python3 $M/thumb_overflow_check.py thumb/custom
[ -z "$F" ] && { echo "PRE_OK ${N}개"; exit 0; }
echo "PRE_FAIL $F (자세한 건 $L — 해당 '== 이름' 아래만 grep -A8로 본다)"; exit 1
