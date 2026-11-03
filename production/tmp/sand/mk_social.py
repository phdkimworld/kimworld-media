import json, sys, datetime as dt
base = dt.datetime.fromisoformat(sys.argv[1])
S = "sand-2026-11"; U = f"https://drkimworld.com/r/{S}/"
OUT = "/home/user/kimworld-site/social/queue"
ut = lambda src, c=None: f"{U}?utm_source={src}&utm_medium=social&utm_campaign={S}" + (f"&utm_content={c}" if c else "")
cards = [f"static/social/{S}/cards/card-{i:02d}.jpg" for i in range(1, 10)]
iso = lambda h: (base + dt.timedelta(hours=h)).isoformat(timespec='seconds')
th1 = {"text": "샌드박스(SAND)는 10월 2일 유의 해제 날 하루 +53.3%. 그런데 11월 2일 60.2원, 해제 전날보다 낮다.\n\n숫자로 보면:\n· 해제 날 거래대금 평소의 76.3배\n· 8.24 업비트 -22.0%, 해외 -7.0%\n· 남은 토큰 해제 0개\n\n업비트 하루 +30% 급등 15번 중 6번은 30일 안에 제자리였다. 12월 2일까지 샌드박스는 어느 쪽일까?",
       "channels": ["threads"], "poll": ["다시 불붙는다", "반짝 뒤 원위치", "조용히 바닥", "신저가로 간다"],
       "replies": [{"text": "투표하신 시나리오의 판정 기준은 리포트 5부 표에 있다. 답은 리포트 3부 '하루 +30% 넘게 오른 15번' 기록표, 유의 기간 업비트·크라켄 비교는 2부 표다.\n" + U + "\n\n유튜브 시청자 요청으로 만든 리포트다. 다음 분석 원하는 종목은 댓글로.\n\n김박사 월드 앱(홈 화면 설치)에서 샌드박스를 팔로우하면 12월 판정 뒤 새 리포트 알림을 받을 수 있다.\n\n※ 공개 자료를 정리한 교육용 분석이며 매수·매도 권유가 아님"}],
       "publish_at": iso(0.05), "topic_tag": "코인"}
th2 = {"text": "샌드박스(SAND) 유의 해제 날 +53.3%, 한 달 뒤 제자리.\n\n연결 다리 사고, 한국만 더 빠진 날, 해제 날 거래대금, 급등 15번 기록까지 9장으로 정리했다.\n\n제일 큰 이유는? 하루짜리 재료 / 한국 쏠림 수급 / 수요 감소 중 하나만 댓글로.",
       "channels": ["threads"], "threads_media": {"paths": cards}, "topic_tag": "코인",
       "replies": [{"text": "급등 15번의 날짜별 30일 뒤 숫자는 답은 리포트 3부 기록표에 있다.\n" + ut("threads")}], "publish_at": iso(2)}
th3 = {"text": "샌드박스(SAND)가 업비트에서 하루 30% 넘게 오른 15번 중 6번은 30일 안에 급등 전날 가격 아래로 돌아왔다.\n\n2021년 10월 30일 +52.3%는 30일 뒤 +526.5%였고, 이번 10월 2일 +53.3%는 +0.3%였다.\n\n이번엔 다시 오를까? 그렇게 보는 근거 하나만 댓글로.",
       "channels": ["threads"], "topic_tag": "코인",
       "replies": [{"text": "네 가지 시나리오와 가능성 구간은 답은 리포트 5부 표에 있다.\n" + ut("threads")}], "publish_at": iso(5)}
body = "· 10월 2일 유의 해제 날 하루 +53.3%, 거래대금 평소의 76.3배\n· 11월 2일 60.2원, 해제 전날 61.4원 아래\n· 업비트 하루 +30% 급등 15번 중 6번이 30일 안에 제자리\n\n12월 2일, 여러분은 몇 번? 댓글에 번호 하나\n① 다시 불붙는다 ② 반짝 뒤 원위치 ③ 조용히 바닥 다지기 ④ 새 최저로 간다\n\n"
cap = "📊 7장 기록과 8장 투표까지 넘겨 보세요 👉\n\n" + body + "날짜별 기록표는 무료 리포트에 있습니다. 프로필 링크(drkimworld.com) 첫 화면에서 '샌드박스' 바로 보기\n🔖 저장해 두고 12월 2일 판정 때 다시 보세요\n\n※ 공개 보도·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#샌드박스 #SAND #메타버스코인 #업비트 #코인공부"
ig = {"text": cap, "channels": ["instagram"], "media": {"type": "carousel", "paths": cards}, "publish_at": iso(0.1)}
fbc_t = "샌드박스(SAND) 유의 해제 날 +53.3%인데 한 달 만에 제자리? 9장 넘겨 보기\n\n" + body + "이 리포트에서 확인할 수 있는 것: 하루 +30% 넘게 오른 15번 기록표(3부)\n무료 리포트: " + ut("facebook", "cards_caption") + "\n\n※ 공개 보도·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#샌드박스 #SAND #메타버스코인 #업비트 #코인공부"
fbc = {"text": fbc_t, "channels": ["facebook"], "media": {"type": "carousel", "paths": cards}, "channel_text": {"facebook": fbc_t}, "publish_at": iso(6)}
fbt = "유의 해제 날 +53.3%, 한 달 뒤엔 해제 전날보다 낮다?\n\n시청자 질문에서 시작한 리포트입니다.\n샌드박스(SAND), 메타버스 게임 '더 샌드박스'에서 쓰는 코인.\n8월 22일 연결 다리(브릿지) 사고로 국내 세 거래소가 유의 종목으로 지정했고, 10월 2일 해제 날 업비트 거래대금은 평소의 76.3배였습니다.\n11월 2일 종가 60.2원은 해제 전날 61.4원보다 낮습니다.\n\n※ 공개 보도·시세를 정리한 교육용 분석이며 매수·매도 권유가 아닙니다.\n답: 리포트 3부 '하루 +30% 넘게 오른 15번' 기록표\n이 리포트에서 확인할 수 있는 것: 하루 +30% 넘게 오른 15번 기록표(3부)\n무료 리포트: " + ut("facebook", "reels_caption") + "\n\n#샌드박스 #SAND #메타버스코인 #김박사월드"
fb = {"text": fbt, "poll": ["하루짜리 재료", "한국 쏠림 수급", "수요 감소"],
      "replies": [{"text": "하루 +30% 넘게 오른 15번의 30일 뒤 기록표를 무료 리포트 3부에 정리했습니다.\n" + ut("facebook", "reels_comment")}],
      "channels": ["facebook"], "media": {"type": "reels", "path": f"static/social/{S}/SAND_shorts.mp4", "cover": f"static/social/{S}/cover.jpg"}, "publish_at": iso(0.15)}
for n, d in ((S, th1), (S + "-th2", th2), (S + "-th3", th3), (S + "-cards", ig), (S + "-reels", fb), (S + "-fbcards", fbc)):
    json.dump(d, open(f"{OUT}/{n}.json", "w"), ensure_ascii=False, indent=1)
print('ok')
