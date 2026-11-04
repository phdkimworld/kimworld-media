import json, sys, datetime as dt
base = dt.datetime.fromisoformat(sys.argv[1])
S = "zs-2026-11"; U = f"https://drkimworld.com/r/{S}/"
OUT = "/home/user/kimworld-site/social/queue"
ut = lambda src, c=None: f"{U}?utm_source={src}&utm_medium=social&utm_campaign={S}" + (f"&utm_content={c}" if c else "")
cards = [f"static/social/{S}/cards/card-{i:02d}.jpg" for i in range(1, 10)]
iso = lambda h: (base + dt.timedelta(hours=h)).isoformat(timespec='seconds')
th1 = {"text": "지스케일러(ZS)는 올해 AI가 보안 소프트웨어를 대체한다는 공포에 4월 118.05달러까지 내렸다가, AI 위협이 보안 예산을 늘린다는 기대에 10월 260.45달러를 찍었다. 11월 3일 종가는 225.09달러, 연초와 같은 자리.\n\n숫자로 보면:\n· 연간 반복 매출 37억 7,100만 달러(+25%)\n· 2027 회계연도 매출 전망 +16.6~17.5%\n· 1분기 매출 전망 9억 3,500만~9억 3,900만 달러\n\n상장 뒤 1분기 실적 8번 중 20거래일 뒤 높았던 건 3번. 12월 23일 지스케일러는 어느 쪽일까?",
       "channels": ["threads"], "poll": ["상단 넘고 전망 상향", "상단 넘었지만 전망 유지", "못 미쳤지만 전망 상향", "둘 다 못 미침"],
       "replies": [{"text": "투표하신 시나리오의 판정 기준은 리포트 5부 표에 있다. 답은 리포트 3부 '1분기 실적 여덟 번' 기록표, 올해 주가를 움직인 날은 2부 표다.\n" + U + "\n\n유튜브 시청자 요청으로 만든 리포트다. 다음 분석 원하는 종목은 댓글로.\n\n김박사 월드 앱(홈 화면 설치)에서 지스케일러를 팔로우하면 12월 판정 뒤 새 리포트 알림을 받을 수 있다.\n\n※ 공개 자료를 정리한 교육용 분석이며 매수·매도 권유가 아님"}],
       "publish_at": iso(0.05), "topic_tag": "주식"}
th2 = {"text": "지스케일러(ZS) AI 공포에 118달러, AI 기대에 260달러, 지금은 연초 자리.\n\n회사 소개, 엇갈린 AI 반응, 1분기 전망, 실적 8번 기록, 네 가지 시나리오까지 9장으로 정리했다.\n\n1분기 실적에서 주가를 가를 것은? 매출 상단 / 연간 전망 / 업종 분위기 중 하나만 댓글로.",
       "channels": ["threads"], "threads_media": {"paths": cards}, "topic_tag": "주식",
       "replies": [{"text": "1분기 실적 8번의 첫날·20거래일 뒤 숫자는 답은 리포트 3부 기록표에 있다.\n" + ut("threads")}], "publish_at": iso(2)}
th3 = {"text": "지스케일러(ZS) 1분기 실적 8번 중 첫날 오른 건 3번. 최근 5번 중 4번은 첫날 내렸다.\n\n지난해 11월에는 매출이 26% 늘었는데도 다음 날 -13.0%였다.\n\n이번엔 다를까? 그렇게 보는 근거 하나만 댓글로.",
       "channels": ["threads"], "topic_tag": "주식",
       "replies": [{"text": "네 가지 시나리오와 가능성 구간은 답은 리포트 5부 표에 있다.\n" + ut("threads")}], "publish_at": iso(5)}
body = "· 4월 10일 118.05달러 → 10월 26일 260.45달러 → 11월 3일 225.09달러\n· 연간 반복 매출 37억 7,100만 달러, 1년 전보다 +25%\n· 1분기 실적 8번 중 20거래일 뒤 높았던 건 3번\n\n12월 23일, 여러분은 몇 번? 댓글에 번호 하나\n① 상단 넘고 전망 상향 ② 상단 넘었지만 전망 유지 ③ 못 미쳤지만 전망 상향 ④ 둘 다 못 미침\n\n"
cap = "📊 7장 기록과 8장 투표까지 넘겨 보세요 👉\n\n" + body + "날짜별 기록표는 무료 리포트에 있습니다. 프로필 링크(drkimworld.com) 첫 화면에서 '지스케일러' 바로 보기\n🔖 저장해 두고 12월 23일 판정 때 다시 보세요\n\n※ 공개 공시·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#지스케일러 #ZS #사이버보안 #미국주식 #실적발표"
ig = {"text": cap, "channels": ["instagram"], "media": {"type": "carousel", "paths": cards}, "publish_at": iso(0.1)}
fbc_t = "지스케일러(ZS) AI 공포에 118달러, AI 기대에 260달러? 9장 넘겨 보기\n\n" + body + "이 리포트에서 확인할 수 있는 것: 1분기 실적 여덟 번 기록표(3부)\n무료 리포트: " + ut("facebook", "cards_caption") + "\n\n※ 공개 공시·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#지스케일러 #ZS #사이버보안 #미국주식 #실적발표"
fbc = {"text": fbc_t, "channels": ["facebook"], "media": {"type": "carousel", "paths": cards}, "channel_text": {"facebook": fbc_t}, "publish_at": iso(6)}
fbt = "AI 공포에 118달러, AI 기대에 260달러. 지금은 연초 자리?\n\n시청자 질문에서 시작한 리포트입니다.\n지스케일러(ZS), 직원과 기기, AI 에이전트의 접속을 클라우드 검문소로 거치게 하는 보안 회사.\n올해 주가는 4월 10일 118.05달러까지 내렸다가 10월 26일 260.45달러를 찍었고, 11월 3일 225.09달러로 연초와 거의 같습니다.\n곧 1분기(8~10월) 실적이 나옵니다.\n\n※ 공개 공시·시세를 정리한 교육용 분석이며 매수·매도 권유가 아닙니다.\n답: 리포트 3부 '1분기 실적 여덟 번' 기록표\n이 리포트에서 확인할 수 있는 것: 1분기 실적 여덟 번 기록표(3부)\n무료 리포트: " + ut("facebook", "reels_caption") + "\n\n#지스케일러 #ZS #사이버보안 #김박사월드"
fb = {"text": fbt, "poll": ["매출 상단", "연간 전망", "업종 분위기"],
      "replies": [{"text": "1분기 실적 여덟 번의 첫날·20거래일 뒤 기록표를 무료 리포트 3부에 정리했습니다.\n" + ut("facebook", "reels_comment")}],
      "channels": ["facebook"], "media": {"type": "reels", "path": f"static/social/{S}/ZS_shorts.mp4", "cover": f"static/social/{S}/cover.jpg"}, "publish_at": iso(0.15)}
for n, d in ((S, th1), (S + "-th2", th2), (S + "-th3", th3), (S + "-cards", ig), (S + "-reels", fb), (S + "-fbcards", fbc)):
    json.dump(d, open(f"{OUT}/{n}.json", "w"), ensure_ascii=False, indent=1)
print('ok')
