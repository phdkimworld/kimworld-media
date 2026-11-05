import json, sys, datetime as dt
base = dt.datetime.fromisoformat(sys.argv[1])
S = "iren-2026-11"; U = f"https://drkimworld.com/r/{S}/"
OUT = "/home/user/kimworld-site/social/queue"
ut = lambda src, c=None: f"{U}?utm_source={src}&utm_medium=social&utm_campaign={S}" + (f"&utm_content={c}" if c else "")
cards = [f"static/social/{S}/cards/card-{i:02d}.jpg" for i in range(1, 10)]
iso = lambda h: (base + dt.timedelta(hours=h)).isoformat(timespec='seconds')
th1 = {"text": "아이렌(IREN)은 실적 하루 전인 11월 4일 21.71달러로 52주 최저 종가를 찍었다. 10월 28일 28.84달러에서 5거래일 만에 -24.7%, 그동안 회사 공시는 0건.\n\n숫자로 보면:\n· 같은 기간 코어위브 -24.3%, 비트코인 -1.0%\n· 실적 9번 중 떨어진 채 맞은 4번\n· 그중 3번은 다음 날 상승\n\n지난 예측(10월 29일): 적중 1 · 부분 적중 2 · 빗나감 1 · 진행 중 2 — 되돌림은 실적 전에 왔다. 11월 19일 아이렌은 어느 쪽일까?",
       "channels": ["threads"], "poll": ["안도 반등 지속", "첫날만 반등", "실망 추가 하락", "조달 겹친 하락"],
       "replies": [{"text": "투표하신 시나리오의 판정 기준은 리포트 5부 표에 있다. 실적 9번의 발표 전 5거래일과 다음 날 기록은 3부 기록표, 5거래일 업종 비교는 2부에 정리했다.\n" + U + "\n\n김박사 월드 앱(홈 화면 설치)에서 아이렌을 팔로우하면 실적 뒤 새 리포트 알림을 받을 수 있다.\n\n※ 공개 자료를 정리한 교육용 분석이며 매수·매도 권유가 아님"}],
       "publish_at": iso(0.05), "topic_tag": "주식"}
th2 = {"text": "아이렌(IREN) 실적 하루 전 5거래일 -24.7%, 회사 공시 0건.\n\n마이크로소프트 발표 다음 날 -9.0%, 업종 동반 하락, 텍사스 선거 보도, 실적 9번의 다음 날 기록까지 9장으로 정리했다.\n\n가장 큰 이유는? 투자 속도 / 업종 의심 / 규제 걱정 중 하나만 댓글로.",
       "channels": ["threads"], "threads_media": {"paths": cards}, "topic_tag": "주식",
       "replies": [{"text": "실적 9번의 발표 전 5거래일·다음 날·20거래일 뒤 숫자는 리포트 3부 기록표에 있다.\n" + ut("threads")}], "publish_at": iso(2)}
th3 = {"text": "아이렌(IREN)이 이번처럼 5거래일에 20% 넘게 빠진 채 실적을 맞은 것은 2026년 2월 한 번뿐이다.\n\n그때 발표 전 5거래일 -33.5%, 다음 날 +5.1%, 20거래일 뒤에는 발표 날보다 -7.8%.\n\n이번 첫날 반등이 한 달을 갈까? 그렇게 보는 근거 하나만 댓글로.",
       "channels": ["threads"], "topic_tag": "주식",
       "replies": [{"text": "네 가지 시나리오와 가능성 구간은 리포트 5부 표에 정리했다.\n" + ut("threads")}], "publish_at": iso(5)}
body = "· 10월 28일 28.84달러 → 11월 4일 21.71달러(-24.7%), 회사 공시 0건\n· 같은 기간 코어위브 -24.3%, 비트코인 -1.0%\n· 떨어진 채 맞은 실적 4번 중 3번은 다음 날 상승\n\n11월 19일, 여러분은 몇 번? 댓글에 번호 하나\n① 안도 반등 지속 ② 첫날만 반등 ③ 실적 실망 추가 하락 ④ 실적과 조달이 겹친 하락\n\n"
cap = "📊 6장 기록과 8장 투표까지 넘겨 보세요 👉\n\n" + body + "날짜별 기록표는 무료 리포트에 있습니다. 프로필 링크(drkimworld.com) 첫 화면에서 '아이렌' 바로 보기\n🔖 저장해 두고 11월 6일 첫 반응 때 다시 보세요\n\n※ 공개 공시·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#아이렌 #IREN #AI데이터센터 #네오클라우드 #미국주식"
ig = {"text": cap, "channels": ["instagram"], "media": {"type": "carousel", "paths": cards}, "publish_at": iso(0.1)}
fbc_t = "아이렌(IREN) 실적 하루 전 5거래일 -24.7%, 떨어진 채 맞은 실적의 다음 날은? 9장 넘겨 보기\n\n" + body + "이 리포트에서 확인할 수 있는 것: 실적 9번, 발표 전 5거래일과 다음 날 기록표(3부)\n무료 리포트: " + ut("facebook", "cards_caption") + "\n\n※ 공개 공시·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#아이렌 #IREN #AI데이터센터 #미국주식"
fbc = {"text": fbc_t, "channels": ["facebook"], "media": {"type": "carousel", "paths": cards}, "channel_text": {"facebook": fbc_t}, "publish_at": iso(6)}
fbt = "실적 하루 전 5거래일 만에 -24.7%, 아이렌은 왜 빠졌나?\n\n아이렌(IREN), 그래픽 처리 장치 연산을 빌려주는 AI 클라우드로 옮겨 가는 데이터센터 회사.\n10월 28일 마이크로소프트가 외부 데이터센터 용량 인도가 늦어졌다고 설명한 다음 날 -9.0%, 이후 업종과 함께 내려 11월 4일 21.71달러로 52주 최저 종가를 찍었습니다. 회사 공시는 0건이었습니다.\n\n※ 공개 공시·시세를 정리한 교육용 분석이며 매수·매도 권유가 아닙니다.\n떨어진 채 맞은 실적 4번의 다음 날과 한 달 뒤는 리포트 3부 기록표에 정리했습니다.\n이 리포트에서 확인할 수 있는 것: 실적 9번, 발표 전 5거래일과 다음 날 기록표(3부)\n무료 리포트: " + ut("facebook", "reels_caption") + "\n\n#아이렌 #IREN #김박사월드"
fb = {"text": fbt, "poll": ["투자 속도", "업종 의심", "규제 걱정"],
      "replies": [{"text": "아이렌 실적 9번의 발표 전 5거래일·다음 날·20거래일 뒤 기록표를 무료 리포트 3부에 정리했습니다.\n" + ut("facebook", "reels_comment")}],
      "channels": ["facebook"], "media": {"type": "reels", "path": f"static/social/{S}/IREN_shorts.mp4", "cover": f"static/social/{S}/cover.jpg"}, "publish_at": iso(0.15)}
for n, d in ((S, th1), (S + "-th2", th2), (S + "-th3", th3), (S + "-cards", ig), (S + "-reels", fb), (S + "-fbcards", fbc)):
    json.dump(d, open(f"{OUT}/{n}.json", "w"), ensure_ascii=False, indent=1)
print('ok')
