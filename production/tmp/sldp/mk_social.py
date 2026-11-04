import json, sys, datetime as dt
base = dt.datetime.fromisoformat(sys.argv[1])
S = "sldp-2026-11"; U = f"https://drkimworld.com/r/{S}/"
OUT = "/home/user/kimworld-site/social/queue"
ut = lambda src, c=None: f"{U}?utm_source={src}&utm_medium=social&utm_campaign={S}" + (f"&utm_content={c}" if c else "")
cards = [f"static/social/{S}/cards/card-{i:02d}.jpg" for i in range(1, 10)]
iso = lambda h: (base + dt.timedelta(hours=h)).isoformat(timespec='seconds')
th1 = {"text": "솔리드파워(SLDP) 3분기 매출은 1년 전보다 93% 줄었다. 그런데 11월 3일 주가 2.03달러는 한 주당 유동성 약 1.74달러의 1.17배.\n\n숫자로 보면:\n· 9월 말 유동성 3억 9,756만 달러, 부채 0\n· 올해 현금 투입 전망 7,500만~8,500만 달러로 하향\n· 순손실 2,440만 달러\n\n현금값 근처에서 맞은 실적 10번 중 20거래일 뒤 높았던 건 3번. 12월 3일까지 솔리드파워는 어느 쪽일까?",
       "channels": ["threads"], "poll": ["현금 지키며 합작 발표", "현금 지키며 소식 없음", "합작과 함께 주식 발행", "시장 매각 재개"],
       "replies": [{"text": "투표하신 시나리오의 판정 기준은 리포트 5부 표에 있다. 답은 리포트 3부 '현금값 근처에서 맞은 실적 10번' 기록표, 3분기 숫자는 1부 표다.\n" + U + "\n\n지난 10월 26일 리포트의 예측 성적(적중 2 · 빗나감 0 · 진행 중 3)도 함께 정리했다.\n\n김박사 월드 앱(홈 화면 설치)에서 솔리드파워를 팔로우하면 12월 판정 뒤 새 리포트 알림을 받을 수 있다.\n\n※ 공개 자료를 정리한 교육용 분석이며 매수·매도 권유가 아님"}],
       "publish_at": iso(0.05), "topic_tag": "주식"}
th2 = {"text": "솔리드파워(SLDP) 매출 -93%인데 주가는 현금의 1.17배.\n\n3분기 숫자, 줄어든 현금 계획, 지난 예측 채점, 현금값 근처 실적 10번 기록까지 9장으로 정리했다.\n\n다음 주가를 가를 것은? 합작법인 발표 / 현금 지키기 / 주식 발행 여부 중 하나만 댓글로.",
       "channels": ["threads"], "threads_media": {"paths": cards}, "topic_tag": "주식",
       "replies": [{"text": "실적 10번의 첫날·20거래일 뒤 숫자는 답은 리포트 3부 기록표에 있다.\n" + ut("threads")}], "publish_at": iso(2)}
th3 = {"text": "솔리드파워(SLDP)가 한 주당 현금의 1.5배 안에서 맞은 실적 10번 중, 첫 반응일에 오른 건 4번, 20거래일 뒤 실적 전보다 높았던 건 3번이었다.\n\n첫 반응 범위는 -19.2% ~ +6.8%.\n\n이번엔 다를까? 그렇게 보는 근거 하나만 댓글로.",
       "channels": ["threads"], "topic_tag": "주식",
       "replies": [{"text": "네 가지 시나리오와 가능성 구간은 답은 리포트 5부 표에 있다.\n" + ut("threads")}], "publish_at": iso(5)}
body = "· 3분기 매출 24만 3,000달러, 1년 전보다 -93%\n· 11월 3일 2.03달러, 한 주당 유동성의 1.17배\n· 현금값 근처 실적 10번 중 20거래일 뒤 높았던 건 3번\n\n12월 3일, 여러분은 몇 번? 댓글에 번호 하나\n① 현금 지키며 합작 발표 ② 현금 지키며 소식 없음 ③ 합작과 함께 주식 발행 ④ 시장 매각 재개\n\n"
cap = "📊 7장 기록과 8장 투표까지 넘겨 보세요 👉\n\n" + body + "날짜별 기록표는 무료 리포트에 있습니다. 프로필 링크(drkimworld.com) 첫 화면에서 '솔리드파워' 바로 보기\n🔖 저장해 두고 12월 3일 판정 때 다시 보세요\n\n※ 공개 공시·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#솔리드파워 #SLDP #전고체배터리 #미국주식 #실적발표"
ig = {"text": cap, "channels": ["instagram"], "media": {"type": "carousel", "paths": cards}, "publish_at": iso(0.1)}
fbc_t = "솔리드파워(SLDP) 매출 -93%인데 주가는 현금의 1.17배? 9장 넘겨 보기\n\n" + body + "이 리포트에서 확인할 수 있는 것: 현금값 근처에서 맞은 실적 10번 기록표(3부)\n무료 리포트: " + ut("facebook", "cards_caption") + "\n\n※ 공개 공시·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#솔리드파워 #SLDP #전고체배터리 #미국주식 #실적발표"
fbc = {"text": fbc_t, "channels": ["facebook"], "media": {"type": "carousel", "paths": cards}, "channel_text": {"facebook": fbc_t}, "publish_at": iso(6)}
fbt = "매출은 93% 줄었는데 주가는 왜 현금값 위일까?\n\n솔리드파워(SLDP), 전고체 배터리 전해질을 만드는 미국 회사.\n11월 3일 장 마감 뒤 3분기 실적에서 매출은 24만 3,000달러로 1년 전 373만 달러보다 크게 줄었습니다.\n대신 올해 현금 투입 전망을 7,500만~8,500만 달러로 낮췄고, 9월 말 유동성은 3억 9,756만 달러, 부채는 없습니다.\n11월 3일 종가 2.03달러는 한 주당 유동성의 1.17배입니다.\n\n※ 공개 공시·시세를 정리한 교육용 분석이며 매수·매도 권유가 아닙니다.\n답: 리포트 3부 '현금값 근처에서 맞은 실적 10번' 기록표\n이 리포트에서 확인할 수 있는 것: 현금값 근처에서 맞은 실적 10번 기록표(3부)\n무료 리포트: " + ut("facebook", "reels_caption") + "\n\n#솔리드파워 #SLDP #전고체배터리 #김박사월드"
fb = {"text": fbt, "poll": ["합작법인 발표", "현금 지키기", "주식 발행 여부"],
      "replies": [{"text": "현금값 근처에서 맞은 실적 10번의 첫날·20거래일 뒤 기록표를 무료 리포트 3부에 정리했습니다.\n" + ut("facebook", "reels_comment")}],
      "channels": ["facebook"], "media": {"type": "reels", "path": f"static/social/{S}/SLDP_shorts.mp4", "cover": f"static/social/{S}/cover.jpg"}, "publish_at": iso(0.15)}
for n, d in ((S, th1), (S + "-th2", th2), (S + "-th3", th3), (S + "-cards", ig), (S + "-reels", fb), (S + "-fbcards", fbc)):
    json.dump(d, open(f"{OUT}/{n}.json", "w"), ensure_ascii=False, indent=1)
print('ok')
