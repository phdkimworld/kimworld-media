import json, sys, datetime as dt
base = dt.datetime.fromisoformat(sys.argv[1])
S = "aehr-2026-11"; U = f"https://drkimworld.com/r/{S}/"
OUT = "/home/user/kimworld-site/social/queue"
ut = lambda src, c=None: f"{U}?utm_source={src}&utm_medium=social&utm_campaign={S}" + (f"&utm_content={c}" if c else "")
cards = [f"static/social/{S}/cards/card-{i:02d}.jpg" for i in range(1, 9)]
iso = lambda h: (base + dt.timedelta(hours=h)).isoformat(timespec='seconds')
th1 = {"text": "에어 테스트 시스템즈(AEHR) 주가가 실적 다음 날 26.5% 올랐다가, 3거래일 뒤 발표 날보다 4.5% 낮은 49.16달러로 마감했다.\n\n숫자로 보면:\n· 1분기 매출 3,300만 달러, 1년 전의 3배\n· 수주 4,670만 달러, 직전 분기보다 23% 감소\n· 다음 날 15%↑ 실적 7번은 3일째 모두 위\n\n지난 예측(10월 15일): 적중 2 · 부분 적중 1. 12월 1일 에어 테스트는 어느 쪽일까?",
       "channels": ["threads"], "poll": ["새 주문으로 회복", "주문 있어도 하락", "업종 회복", "조정이 이어짐"],
       "replies": [{"text": "투표하신 시나리오의 판정 기준은 리포트 5부 표에 있다. 분기별 수주와 매출은 2부 표, 다음 날 크게 오른 실적 7번은 3부 기록표에 정리했다.\n" + U + "\n\n김박사 월드 앱(홈 화면 설치)에서 에어 테스트를 팔로우하면 새 리포트 알림을 받을 수 있다.\n\n시청자 요청으로 만든 리포트다.\n\n※ 공개 자료를 정리한 교육용 분석이며 매수·매도 권유가 아님"}],
       "publish_at": iso(0.05), "topic_tag": "주식"}
th2 = {"text": "에어 테스트(AEHR) 수주 4,670만 달러, 실적 다음 날 +26.5%, 3거래일 뒤 -4.5%.\n\n분기별 수주, 증권사 목표가 하향, 다음 날 크게 오른 실적 7번의 기록까지 8장으로 정리했다.\n\n가장 큰 이유는? 배수 하락 / 주문 증가세 / 높았던 기대 중 하나만 댓글로.",
       "channels": ["threads"], "threads_media": {"paths": cards}, "topic_tag": "주식",
       "replies": [{"text": "분기별 수주와 매출은 리포트 2부 표, 실적 7번의 3거래일째·20거래일 뒤 숫자는 3부 기록표에 있다.\n" + ut("threads")}], "publish_at": iso(2)}
th3 = {"text": "에어 테스트(AEHR)는 수주가 늘어난 실적 뒤 한 달 동안 평균 22.9% 올랐고, 줄어든 실적 뒤에는 평균 9.4% 내렸다.\n\n이번 분기 수주는 사상 최대였던 직전 분기보다 줄었다.\n\n이번에도 한 달 뒤는 수주를 따라갈까? 그렇게 보는 근거 하나만 댓글로.",
       "channels": ["threads"], "topic_tag": "주식",
       "replies": [{"text": "네 가지 시나리오와 가능성 구간은 리포트 5부 표에 정리했다.\n" + ut("threads")}], "publish_at": iso(5)}
body = "· 1분기 매출 3,300만 달러, 1년 전의 3배\n· 수주 4,670만 달러, 직전 분기 6,070만 달러\n· 다음 날 +26.5%, 3거래일 뒤 발표 날 대비 -4.5%\n\n12월 1일, 여러분은 몇 번? 댓글에 번호 하나\n① 새 주문으로 회복 ② 주문에도 배수 부담 ③ 주문 없이 업종 회복 ④ 조정이 이어짐\n\n"
cap = "📊 4장 분기별 수주와 6장 기록까지 넘겨 보세요 👉\n\n" + body + "분기별 수주 표는 무료 리포트에 있습니다. 프로필 링크(drkimworld.com) 첫 화면에서 '에어 테스트' 바로 보기\n🔖 저장해 두고 새 주문 소식 때 다시 보세요\n\n※ 공개 공시·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#에어테스트 #AEHR #반도체장비 #AI반도체 #미국주식"
ig = {"text": cap, "channels": ["instagram"], "media": {"type": "carousel", "paths": cards}, "publish_at": iso(0.1)}
igr_cap = "실적 다음 날 +26.5%, 3거래일 뒤 -4.5%. 에어 테스트(AEHR) 상승분은 왜 사라졌나?" + cap[cap.index("\n\n"):]
igr = {"text": igr_cap, "channels": ["instagram"], "media": {"type": "reels", "path": f"static/social/{S}/AEHR_shorts.mp4", "cover": f"static/social/{S}/cover.jpg"}, "publish_at": iso(3)}
fbc_t = "에어 테스트(AEHR) 실적 다음 날 +26.5%, 3거래일 뒤엔 발표 날 아래로. 8장 넘겨 보기\n\n" + body + "이 리포트에서 확인할 수 있는 것: 분기별 수주와 매출 표(2부) · 다음 날 크게 오른 실적 7번(3부)\n무료 리포트: " + ut("facebook", "cards_caption") + "\n\n※ 공개 공시·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#에어테스트 #AEHR #반도체장비 #미국주식"
fbc = {"text": fbc_t, "channels": ["facebook"], "media": {"type": "carousel", "paths": cards}, "channel_text": {"facebook": fbc_t}, "publish_at": iso(6)}
fbt = "매출은 1년 만에 3배, 실적 다음 날 +26.5%. 그런데 에어 테스트는 왜 3거래일 만에 발표 날 아래로 내려왔나?\n\n에어 테스트 시스템즈(AEHR), 반도체가 출하 전에 고장 나지 않는지 열과 전압으로 미리 시험하는 장비 회사.\n1분기 수주는 4,670만 달러로 직전 분기보다 줄었고, 실적 뒤 증권사 두 곳이 목표가를 낮췄습니다.\n\n※ 공개 공시·시세를 정리한 교육용 분석이며 매수·매도 권유가 아닙니다.\n분기별 수주와 매출은 리포트 2부 표에 정리했습니다.\n이 리포트에서 확인할 수 있는 것: 분기별 수주와 매출 표(2부) · 다음 날 크게 오른 실적 7번(3부)\n무료 리포트: " + ut("facebook", "reels_caption") + "\n\n#에어테스트 #AEHR #김박사월드"
fb = {"text": fbt, "poll": ["배수 하락", "주문 증가세", "높았던 기대"],
      "replies": [{"text": "에어 테스트 분기별 수주 표와 실적 7번의 기록표를 무료 리포트 2부·3부에 정리했습니다.\n" + ut("facebook", "reels_comment")}],
      "channels": ["facebook"], "media": {"type": "reels", "path": f"static/social/{S}/AEHR_shorts.mp4", "cover": f"static/social/{S}/cover.jpg"}, "publish_at": iso(0.15)}
for n, d in ((S, th1), (S + "-th2", th2), (S + "-th3", th3), (S + "-cards", ig), (S + "-igreels", igr), (S + "-reels", fb), (S + "-fbcards", fbc)):
    json.dump(d, open(f"{OUT}/{n}.json", "w"), ensure_ascii=False, indent=1)
print('ok')
