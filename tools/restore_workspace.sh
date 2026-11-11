#!/usr/bin/env bash
# 컨테이너 재시작 대비(2026-11-11 재시작으로 /home/claude 전체 유실 → RUM 76회차 작업물 소실 뒤, 운영자 "이런일 없도록 해").
# /home/claude 를 재시작에도 남는 /home/user/claude_ws 로 가는 링크로 만든다. 그러면 SKILL·도구의 /home/claude/... 경로가 모두 보존된다.
# 매시간 hourly.py·prod_check.py 가 링크가 아니면 자동으로 이 스크립트를 부른다. 손으로: bash tools/restore_workspace.sh
set -e
S=/home/user/kimworld-site; M=/home/user/kimworld-media; W=/home/user/claude_ws
mkdir -p $W/bin $W/tts /home/user/work
if [ -d /home/claude ] && [ ! -L /home/claude ]; then
  cp -an /home/claude/. $W/ 2>/dev/null || true   # 재시작 뒤 새로 생긴 것이 있으면 옮겨 둔다
  rm -rf /home/claude
fi
ln -sfn $W /home/claude
for k in slidekit thumbkit midroll cardnews shorts charts; do rm -rf $W/$k; cp -r $S/tools/$k $W/$k; done
ln -sfn $S/tools/tts $W/tts/st
ln -sfn $S $W/kimworld-site
ln -sfn $M $W/kimworld-media
ln -sf $M/tools/wait_live.sh $W/bin/wait_live.sh
ln -sf $M/tools/yt_api_upload.py $W/yt_api_upload.py
[ -f $W/bin/hero_check.py ] || printf 'import sys\nprint("HERO_SKIP (도구 유실, 눈으로 확인)")\n' > $W/bin/hero_check.py
# 파이썬 패키지(재시작 뒤 빠져 있던 것, 76회차)
pip install -q google-auth google-auth-oauthlib google-api-python-client playwright markdown pyyaml jinja2 fonttools >/dev/null 2>&1 || true
# 한글 글꼴: apt 먼저, 미러 장애면 npm Noto Sans KR 로 같은 파일 이름을 만든다(사이트 deploy.yml 과 같은 방식)
if [ ! -f /usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc ]; then
  apt-get install -y -q fonts-noto-cjk >/dev/null 2>&1 || true
fi
if [ ! -f /usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc ]; then
  mkdir -p /tmp/fnt /usr/share/fonts/opentype/noto && (cd /tmp/fnt && npm pack -q @expo-google-fonts/noto-sans-kr@0.4.4 >/dev/null && tar xzf *.tgz) && python3 -c "
from fontTools.ttLib import TTFont, TTCollection
for w,f in [('Regular','400Regular/NotoSansKR_400Regular'),('Medium','500Medium/NotoSansKR_500Medium'),('Bold','700Bold/NotoSansKR_700Bold'),('Black','900Black/NotoSansKR_900Black')]:
    c=TTCollection(); src='/tmp/fnt/package/'+f+'.ttf'; c.fonts=[TTFont(src),TTFont(src)]; c.save('/usr/share/fonts/opentype/noto/NotoSansCJK-'+w+'.ttc')" || echo "글꼴 대체 실패"
fi
echo "RESTORED /home/claude -> $W"
