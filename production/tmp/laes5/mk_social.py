import json, sys, datetime as dt
base = dt.datetime.fromisoformat(sys.argv[1])
S = "laes-2026-11-2"; U = f"https://drkimworld.com/r/{S}/"
OUT = "/home/user/kimworld-site/social/queue"
ut = lambda src, c=None: f"{U}?utm_source={src}&utm_medium=social&utm_campaign={S}" + (f"&utm_content={c}" if c else "")
cards = [f"static/social/{S}/cards/card-{i:02d}.jpg" for i in range(1, 9)]
iso = lambda h: (base + dt.timedelta(hours=h)).isoformat(timespec='seconds')
th1 = {"text": "실스크(LAES) 주가가 11월 5일 하루 14.0% 빠져 1.23달러로 마감했다. 9월 말 한 주당 현금 약 2.07달러의 59%다.\n\n숫자로 보면:\n· 같은 날 아이온큐 -10.5%, 디웨이브 -12.8%\n· 모회사, 11월 3일 1억 달러 증권 신고서\n· 함께 빠진 날 11번 중 한 달 뒤 위는 4번\n\n지난 예측(10월 30일): 적중 1 · 진행 중 5 — '현금 아래 방치' 진단은 맞았다. 12월 4일 실스크는 어느 쪽일까?",
       "channels": ["threads"], "poll": ["업종과 함께 회복", "첫날만 반등", "하락 뒤 회복", "하락이 이어짐"],
       "replies": [{"text": "투표하신 시나리오의 판정 기준은 리포트 5부 표에 있다. 함께 빠진 날 11번의 다음 날·20거래일 뒤 기록은 3부 기록표, 한 주당 현금 계산은 1부 표에 정리했다.\n" + U + "\n\n김박사 월드 앱(홈 화면 설치)에서 실스크를 팔로우하면 새 리포트 알림을 받을 수 있다.\n\n※ 공개 자료를 정리한 교육용 분석이며 매수·매도 권유가 아님"}],
       "publish_at": iso(0.05), "topic_tag": "주식"}
th2 = {"text": "실스크(LAES) 주가 1.23달러, 한 주당 현금 2.07달러.\n\n금고와 주가의 거리, 양자주 동반 급락, 모회사 신고서, 함께 빠진 날 11번의 기록까지 8장으로 정리했다.\n\n가장 큰 이유는? 업종 매도 / 주식 공급 걱정 / 현금 불신 중 하나만 댓글로.",
       "channels": ["threads"], "threads_media": {"paths": cards}, "topic_tag": "주식",
       "replies": [{"text": "함께 빠진 날 11번의 다음 날·20거래일 뒤 숫자는 리포트 3부 기록표에 있다.\n" + ut("threads")}], "publish_at": iso(2)}
th3 = {"text": "실스크(LAES)가 아이온큐(IONQ)와 함께 크게 빠진 다음 날은 11번 중 8번 올랐다.\n\n그런데 한 달 뒤까지 반등이 남은 건 4번뿐이고, 그중 3번은 업종이 강하게 살아난 때였다.\n\n이번에도 업종이 끌어올려 줄까? 그렇게 보는 근거 하나만 댓글로.",
       "channels": ["threads"], "topic_tag": "주식",
       "replies": [{"text": "네 가지 시나리오와 가능성 구간은 리포트 5부 표에 정리했다.\n" + ut("threads")}], "publish_at": iso(5)}
body = "· 11월 5일 종가 1.23달러(-14.0%), 2024년 12월 이후 최저\n· 9월 말 한 주당 현금 약 2.07달러\n· 함께 빠진 날 11번 중 20거래일 뒤 더 높았던 건 4번\n\n12월 4일, 여러분은 몇 번? 댓글에 번호 하나\n① 업종과 함께 회복 ② 첫날만 반등 ③ 첫날 하락 뒤 회복 ④ 하락이 이어짐\n\n"
cap = "📊 6장 기록과 7장 시나리오까지 넘겨 보세요 👉\n\n" + body + "날짜별 기록표는 무료 리포트에 있습니다. 프로필 링크(drkimworld.com) 첫 화면에서 '실스크' 바로 보기\n🔖 저장해 두고 11월 6일 첫 반응 때 다시 보세요\n\n※ 공개 공시·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#실스크 #LAES #양자보안 #양자컴퓨터 #미국주식"
ig = {"text": cap, "channels": ["instagram"], "media": {"type": "carousel", "paths": cards}, "publish_at": iso(0.1)}
igr_cap = "주가 1.23달러, 한 주당 현금 2.07달러. 실스크(LAES)는 왜 현금보다 훨씬 아래로?" + cap[cap.index("\n\n"):]
igr = {"text": igr_cap, "channels": ["instagram"], "media": {"type": "reels", "path": f"static/social/{S}/LAES_shorts.mp4", "cover": f"static/social/{S}/cover.jpg"}, "publish_at": iso(3)}
fbc_t = "실스크(LAES) 주가가 현금의 59%까지, 함께 무너진 뒤 한 달은 어땠나? 8장 넘겨 보기\n\n" + body + "이 리포트에서 확인할 수 있는 것: 함께 빠진 날 11번, 다음 날과 20거래일 뒤 기록표(3부)\n무료 리포트: " + ut("facebook", "cards_caption") + "\n\n※ 공개 공시·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#실스크 #LAES #양자보안 #미국주식"
fbc = {"text": fbc_t, "channels": ["facebook"], "media": {"type": "carousel", "paths": cards}, "channel_text": {"facebook": fbc_t}, "publish_at": iso(6)}
fbt = "주가 1.23달러, 한 주당 현금 2.07달러. 실스크는 왜 현금보다 훨씬 아래로 내려왔나?\n\n실스크(LAES), 해킹을 막는 보안 칩과 양자내성 암호 칩을 만드는 스위스 보안 반도체 회사.\n11월 5일 양자 관련주 다섯 종목이 모두 10% 넘게 빠졌고, 그 이틀 전 모회사는 최대 1억 달러 증권 신고서를 냈습니다.\n\n※ 공개 공시·시세를 정리한 교육용 분석이며 매수·매도 권유가 아닙니다.\n함께 빠진 날 11번의 다음 날과 20거래일 뒤는 리포트 3부 기록표에 정리했습니다.\n이 리포트에서 확인할 수 있는 것: 함께 빠진 날 11번, 다음 날과 20거래일 뒤 기록표(3부)\n무료 리포트: " + ut("facebook", "reels_caption") + "\n\n#실스크 #LAES #김박사월드"
fb = {"text": fbt, "poll": ["업종 매도", "주식 공급 걱정", "현금 불신"],
      "replies": [{"text": "실스크가 아이온큐와 함께 크게 빠진 날 11번의 다음 날·20거래일 뒤 기록표를 무료 리포트 3부에 정리했습니다.\n" + ut("facebook", "reels_comment")}],
      "channels": ["facebook"], "media": {"type": "reels", "path": f"static/social/{S}/LAES_shorts.mp4", "cover": f"static/social/{S}/cover.jpg"}, "publish_at": iso(0.15)}
for n, d in ((S, th1), (S + "-th2", th2), (S + "-th3", th3), (S + "-cards", ig), (S + "-igreels", igr), (S + "-reels", fb), (S + "-fbcards", fbc)):
    json.dump(d, open(f"{OUT}/{n}.json", "w"), ensure_ascii=False, indent=1)
print('ok')
