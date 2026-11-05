import json, sys, datetime as dt
base = dt.datetime.fromisoformat(sys.argv[1])
S = "smr-2026-11"; U = f"https://drkimworld.com/r/{S}/"
OUT = "/home/user/kimworld-site/social/queue"
ut = lambda src, c=None: f"{U}?utm_source={src}&utm_medium=social&utm_campaign={S}" + (f"&utm_content={c}" if c else "")
cards = [f"static/social/{S}/cards/card-{i:02d}.jpg" for i in range(1, 9)]
iso = lambda h: (base + dt.timedelta(hours=h)).isoformat(timespec='seconds')
th1 = {"text": "뉴스케일 파워(SMR) 주가가 실적 날 4.41달러(-14.1%)로 내려와, 9월 말 한 주당 현금과 투자 자산 약 4.34달러와 거의 같아졌다.\n\n숫자로 보면:\n· 3분기 매출 28만 1,000달러, 새 주식 판매는 거의 없음\n· 같은 날 오클로 -12.3%, 나노 뉴클리어 -12.0%\n· 실적 17번 중 20거래일 뒤 더 높았던 건 7번\n\n지난 예측(10월 25일): 적중 3 · 빗나감 2 · 진행 중 1 — 3분기 주식 판매 예상은 빗나갔다. 12월 4일 뉴스케일은 어느 쪽일까?",
       "channels": ["threads"], "poll": ["현금 바닥 반등", "첫날만 반등", "하락 뒤 회복", "실망 이어진 하락"],
       "replies": [{"text": "투표하신 시나리오의 판정 기준은 리포트 5부 표에 있다. 실적 17번의 다음 날·20거래일 뒤 기록은 3부 기록표, 한 주당 현금 계산은 1부 표에 정리했다.\n" + U + "\n\n김박사 월드 앱(홈 화면 설치)에서 뉴스케일 파워를 팔로우하면 새 리포트 알림을 받을 수 있다.\n\n※ 공개 자료를 정리한 교육용 분석이며 매수·매도 권유가 아님"}],
       "publish_at": iso(0.05), "topic_tag": "주식"}
th2 = {"text": "뉴스케일 파워(SMR) 주가 4.41달러, 한 주당 현금과 투자 자산 4.34달러.\n\n금고의 크기, 업종 동반 급락, 증권사 하향, 실적 17번의 기록까지 8장으로 정리했다.\n\n가장 큰 이유는? 기다림의 비용 / 업종 매도 / 판매 계약 중 하나만 댓글로.",
       "channels": ["threads"], "threads_media": {"paths": cards}, "topic_tag": "주식",
       "replies": [{"text": "실적 17번의 다음 날·20거래일 뒤 숫자는 리포트 3부 기록표에 있다.\n" + ut("threads")}], "publish_at": iso(2)}
th3 = {"text": "뉴스케일 파워(SMR)의 최근 실적 5번은 한 달 뒤 4번이 발표 날보다 16% 넘게 낮았다.\n\n그런데 이번에는 3분기 새 주식 판매가 거의 없었고, 주가는 이미 한 주당 현금 수준이다.\n\n이번에도 한 달 뒤가 아래일까? 그렇게 보는 근거 하나만 댓글로.",
       "channels": ["threads"], "topic_tag": "주식",
       "replies": [{"text": "네 가지 시나리오와 가능성 구간은 리포트 5부 표에 정리했다.\n" + ut("threads")}], "publish_at": iso(5)}
body = "· 11월 5일 종가 4.41달러(-14.1%), 2024년 3월 이후 최저\n· 9월 말 한 주당 현금과 투자 자산 약 4.34달러\n· 실적 17번 중 20거래일 뒤 더 높았던 건 7번\n\n12월 4일, 여러분은 몇 번? 댓글에 번호 하나\n① 현금 바닥에서 반등 지속 ② 첫날만 반등 ③ 첫날 하락 뒤 회복 ④ 실망이 이어진 하락\n\n"
cap = "📊 6장 기록과 7장 시나리오까지 넘겨 보세요 👉\n\n" + body + "날짜별 기록표는 무료 리포트에 있습니다. 프로필 링크(drkimworld.com) 첫 화면에서 '뉴스케일' 바로 보기\n🔖 저장해 두고 11월 6일 첫 반응 때 다시 보세요\n\n※ 공개 공시·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#뉴스케일파워 #SMR #소형모듈원자로 #원전주 #미국주식"
ig = {"text": cap, "channels": ["instagram"], "media": {"type": "carousel", "paths": cards}, "publish_at": iso(0.1)}
fbc_t = "뉴스케일 파워(SMR) 주가가 한 주당 현금 수준까지, 실적 뒤 한 달은 어땠나? 8장 넘겨 보기\n\n" + body + "이 리포트에서 확인할 수 있는 것: 실적 17번, 다음 날과 20거래일 뒤 기록표(3부)\n무료 리포트: " + ut("facebook", "cards_caption") + "\n\n※ 공개 공시·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#뉴스케일파워 #SMR #원전주 #미국주식"
fbc = {"text": fbc_t, "channels": ["facebook"], "media": {"type": "carousel", "paths": cards}, "channel_text": {"facebook": fbc_t}, "publish_at": iso(6)}
fbt = "주가 4.41달러, 한 주당 현금 4.34달러. 뉴스케일 파워는 왜 현금 수준까지 내려왔나?\n\n뉴스케일 파워(SMR), 공장에서 만든 작은 원자로를 여러 대 묶어 발전소를 짓는 소형 모듈 원자로 설계 회사.\n확정 주문이 늦어지는 가운데 11월 5일 원전 개발사들이 함께 12% 넘게 빠졌고, 그날 밤 실적에서 현금과 투자 자산은 18억 6,410만 달러였습니다.\n\n※ 공개 공시·시세를 정리한 교육용 분석이며 매수·매도 권유가 아닙니다.\n실적 17번의 다음 날과 20거래일 뒤는 리포트 3부 기록표에 정리했습니다.\n이 리포트에서 확인할 수 있는 것: 실적 17번, 다음 날과 20거래일 뒤 기록표(3부)\n무료 리포트: " + ut("facebook", "reels_caption") + "\n\n#뉴스케일파워 #SMR #김박사월드"
fb = {"text": fbt, "poll": ["기다림의 비용", "업종 매도", "판매 계약"],
      "replies": [{"text": "뉴스케일 실적 17번의 다음 날·20거래일 뒤 기록표를 무료 리포트 3부에 정리했습니다.\n" + ut("facebook", "reels_comment")}],
      "channels": ["facebook"], "media": {"type": "reels", "path": f"static/social/{S}/SMR_shorts.mp4", "cover": f"static/social/{S}/cover.jpg"}, "publish_at": iso(0.15)}
for n, d in ((S, th1), (S + "-th2", th2), (S + "-th3", th3), (S + "-cards", ig), (S + "-reels", fb), (S + "-fbcards", fbc)):
    json.dump(d, open(f"{OUT}/{n}.json", "w"), ensure_ascii=False, indent=1)
print('ok')

