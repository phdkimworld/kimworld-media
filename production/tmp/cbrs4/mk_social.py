import json, sys, datetime as dt
base = dt.datetime.fromisoformat(sys.argv[1])
S = "cbrs-2026-11"; U = f"https://drkimworld.com/r/{S}/"
OUT = "/home/user/kimworld-site/social/queue"
ut = lambda src, c=None: f"{U}?utm_source={src}&utm_medium=social&utm_campaign={S}" + (f"&utm_content={c}" if c else "")
cards = [f"static/social/{S}/cards/card-{i:02d}.jpg" for i in range(1, 9)]
iso = lambda h: (base + dt.timedelta(hours=h)).isoformat(timespec='seconds')
th1 = {"text": "세레브라스(CBRS)는 10월 28일 락업 해제 뒤 5거래일 동안 해제 전날 종가 대비 -18.0%. 11월 4일 91.85달러로 상장 뒤 최저 종가를 찍었다.\n\n숫자로 보면:\n· 해제일 당일 공매도 보고서(칩이 약 2년 만에 닳는다는 주장)\n· 같은 기간 반도체 ETF SOXX -13.7%\n· 해제일 9번 중 6번은 5거래일 뒤에도 더 낮았다\n\n지난 예측(10월 29일): 적중 2 · 부분 적중 1 · 빗나감 2 · 진행 중 3 — 108.37달러 방어는 빗나갔다. 11월 9일 마지막 해제 뒤 세레브라스는 어느 쪽일까?",
       "channels": ["threads"], "poll": ["공급 끝나 재평가", "실적에 실망", "해제 뒤 실적 반등", "이어진 하락"],
       "replies": [{"text": "투표하신 시나리오의 판정 기준은 리포트 5부 표에 있다. 해제일 9번의 당일·5거래일 뒤 기록은 3부 기록표, 5거래일 업종 비교는 2부에 정리했다.\n" + U + "\n\n김박사 월드 앱(홈 화면 설치)에서 세레브라스를 팔로우하면 실적 뒤 새 리포트 알림을 받을 수 있다.\n\n※ 공개 자료를 정리한 교육용 분석이며 매수·매도 권유가 아님"}],
       "publish_at": iso(0.05), "topic_tag": "주식"}
th2 = {"text": "세레브라스(CBRS) 락업 해제 5거래일 -18.0%, 상장 뒤 최저 종가 91.85달러.\n\n공매도 보고서, 반도체 업종 급락, UBS 목표가 인하, 해제일 9번의 기록까지 8장으로 정리했다.\n\n가장 큰 이유는? 공매도 보고서 / 업종 급락 / 해제 물량 중 하나만 댓글로.",
       "channels": ["threads"], "threads_media": {"paths": cards}, "topic_tag": "주식",
       "replies": [{"text": "해제일 9번의 당일·5거래일 뒤 숫자는 리포트 3부 기록표에 있다.\n" + ut("threads")}], "publish_at": iso(2)}
th3 = {"text": "세레브라스(CBRS) 해제일 9번 가운데 오른 날은 두 번뿐이다.\n\n9월 2일과 9월 16일. 둘 다 해제 전에 이미 6~8% 내려 있었고, 풀린 물량은 1,460만 주로 최근(1,940만 주)보다 작았다.\n\n11월 9일 마지막 해제는 어느 쪽에 가까울까? 그렇게 보는 근거 하나만 댓글로.",
       "channels": ["threads"], "topic_tag": "주식",
       "replies": [{"text": "네 가지 시나리오와 가능성 구간은 리포트 5부 표에 정리했다.\n" + ut("threads")}], "publish_at": iso(5)}
body = "· 10월 27일 119.31달러 → 11월 4일 91.85달러, 상장 뒤 최저 종가\n· 해제일 당일 공매도 보고서, 같은 기간 반도체 ETF -13.7%\n· 해제일 9번 중 6번은 5거래일 뒤에도 더 낮았다\n\n11월 13일, 여러분은 몇 번? 댓글에 번호 하나\n① 공급 종료 뒤 재평가 ② 해제는 넘기고 실적에 실망 ③ 해제에 밀리고 실적에 반등 ④ 해제와 실적이 이어진 하락\n\n"
cap = "📊 6장 기록과 7장 시나리오까지 넘겨 보세요 👉\n\n" + body + "날짜별 기록표는 무료 리포트에 있습니다. 프로필 링크(drkimworld.com) 첫 화면에서 '세레브라스' 바로 보기\n🔖 저장해 두고 11월 9일 마지막 해제 때 다시 보세요\n\n※ 공개 공시·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#세레브라스 #CBRS #AI반도체 #락업해제 #미국주식"
ig = {"text": cap, "channels": ["instagram"], "media": {"type": "carousel", "paths": cards}, "publish_at": iso(0.1)}
fbc_t = "세레브라스(CBRS) 락업 해제 5거래일 -18.0%, 정해진 물량인데 왜 더 빠졌나? 8장 넘겨 보기\n\n" + body + "이 리포트에서 확인할 수 있는 것: 락업 해제일 9번, 당일과 그 뒤 기록표(3부)\n무료 리포트: " + ut("facebook", "cards_caption") + "\n\n※ 공개 공시·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#세레브라스 #CBRS #AI반도체 #미국주식"
fbc = {"text": fbc_t, "channels": ["facebook"], "media": {"type": "carousel", "paths": cards}, "channel_text": {"facebook": fbc_t}, "publish_at": iso(6)}
fbt = "락업 해제 5거래일 만에 -18.0%, 세레브라스는 왜 더 빠졌나?\n\n세레브라스(CBRS), 반도체 원판 한 장을 통째로 칩 하나로 쓰는 인공지능 반도체 회사.\n10월 28일 해제일에 공매도 보고서가 나왔고, 반도체 업종 급락과 UBS 목표가 인하가 이어져 11월 4일 91.85달러로 상장 뒤 최저 종가를 찍었습니다.\n\n※ 공개 공시·시세를 정리한 교육용 분석이며 매수·매도 권유가 아닙니다.\n해제일 9번의 당일과 5거래일 뒤는 리포트 3부 기록표에 정리했습니다.\n이 리포트에서 확인할 수 있는 것: 락업 해제일 9번, 당일과 그 뒤 기록표(3부)\n무료 리포트: " + ut("facebook", "reels_caption") + "\n\n#세레브라스 #CBRS #김박사월드"
fb = {"text": fbt, "poll": ["공매도 보고서", "업종 급락", "해제 물량"],
      "replies": [{"text": "세레브라스 해제일 9번의 당일·5거래일 뒤 기록표를 무료 리포트 3부에 정리했습니다.\n" + ut("facebook", "reels_comment")}],
      "channels": ["facebook"], "media": {"type": "reels", "path": f"static/social/{S}/CBRS_shorts.mp4", "cover": f"static/social/{S}/cover.jpg"}, "publish_at": iso(0.15)}
for n, d in ((S, th1), (S + "-th2", th2), (S + "-th3", th3), (S + "-cards", ig), (S + "-reels", fb), (S + "-fbcards", fbc)):
    json.dump(d, open(f"{OUT}/{n}.json", "w"), ensure_ascii=False, indent=1)
print('ok')
