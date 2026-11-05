import json, sys, datetime as dt
base = dt.datetime.fromisoformat(sys.argv[1])
S = "aeva-2026-11"; U = f"https://drkimworld.com/r/{S}/"
OUT = "/home/user/kimworld-site/social/queue"
ut = lambda src, c=None: f"{U}?utm_source={src}&utm_medium=social&utm_campaign={S}" + (f"&utm_content={c}" if c else "")
cards = [f"static/social/{S}/cards/card-{i:02d}.jpg" for i in range(1, 10)]
iso = lambda h: (base + dt.timedelta(hours=h)).isoformat(timespec='seconds')
th1 = {"text": "에이바 테크놀로지스(AEVA)는 '현금이 많은 라이다 회사'로 불리지만, 주가는 5월 27일 29.29달러에서 11월 4일 9.49달러로 -67.6%.\n\n숫자로 보면:\n· 한 주당 현금 2.12달러, 주가의 약 22%\n· 전환사채 1억 달러를 빼면 0.68달러\n· 급등한 날 5번 중 4번은 한 달 뒤 더 낮음\n\n11월 4일 3분기 매출은 사상 최대였다. 12월 3일 에이바는 어느 쪽일까?",
       "channels": ["threads"], "poll": ["실적 안도 지속", "첫날만 반등", "저점 추가 하락", "새 주식 하락"],
       "replies": [{"text": "투표하신 시나리오의 판정 기준은 리포트 5부 표에 있다. 현금과 몸값 계산은 1부 표, 급등한 날 5번과 20거래일 뒤는 3부 기록표에 정리했다.\n" + U + "\n\n시청자 요청으로 만든 리포트다. 다음 분석 원하는 종목은 댓글로.\n\n김박사 월드 앱(홈 화면 설치)에서 에이바 테크놀로지스를 팔로우하면 새 리포트 알림을 받을 수 있다.\n\n※ 공개 자료를 정리한 교육용 분석이며 매수·매도 권유가 아님"}],
       "publish_at": iso(1.0), "topic_tag": "주식"}
th2 = {"text": "에이바 테크놀로지스(AEVA) 현금 많다는데 고점 대비 -67.6%.\n\n한 주당 현금 2.12달러, 전환사채 뺀 0.68달러, 8월 이후 라이다 업종 비교, 급등한 날 5번의 한 달 뒤까지 9장으로 정리했다.\n\n가장 큰 이유는? 기다림 비용 / 고점 공모 / 테마 식음 중 하나만 댓글로.",
       "channels": ["threads"], "threads_media": {"paths": cards}, "topic_tag": "주식",
       "replies": [{"text": "급등한 날 5번의 그날·20거래일 뒤 숫자는 리포트 3부 기록표에 있다.\n" + ut("threads")}], "publish_at": iso(3)}
th3 = {"text": "에이바 테크놀로지스(AEVA)는 지난 8월 6일 데이터센터 계약 발표 날 하루 +28.8% 올랐다.\n\n20거래일 뒤에는 그날 종가보다 -39.6%, 11월 4일에는 -62.4%.\n\n계약이 매출이 되는 2027년 하반기까지, 주가가 기다려 줄까? 그렇게 보는 근거 하나만 댓글로.",
       "channels": ["threads"], "topic_tag": "주식",
       "replies": [{"text": "네 가지 시나리오와 가능성 구간은 리포트 5부 표에 정리했다.\n" + ut("threads")}], "publish_at": iso(6)}
body = "· 5월 27일 29.29달러 → 11월 4일 9.49달러(-67.6%)\n· 한 주당 현금 2.12달러, 전환사채 빼면 0.68달러\n· 회사 발표로 +20% 넘게 오른 5번 중 4번은 한 달 뒤 더 낮음\n\n12월 3일, 여러분은 몇 번? 댓글에 번호 하나\n① 실적 안도가 이어짐 ② 첫날만 반등 ③ 저점 근처 추가 하락 ④ 새 주식과 함께 하락\n\n"
cap = "📊 6장 기록과 8장 투표까지 넘겨 보세요 👉\n\n" + body + "계산표와 기록표는 무료 리포트에 있습니다. 프로필 링크(drkimworld.com) 첫 화면에서 '에이바' 바로 보기\n🔖 저장해 두고 12월 3일 판정 때 다시 보세요\n\n※ 공개 공시·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#에이바 #AEVA #라이다 #자율주행 #미국주식"
ig = {"text": cap, "channels": ["instagram"], "media": {"type": "carousel", "paths": cards}, "publish_at": iso(1.1)}
fbc_t = "에이바 테크놀로지스(AEVA) 현금 많다는데 고점 대비 -67.6%? 9장 넘겨 보기\n\n" + body + "이 리포트에서 확인할 수 있는 것: 현금과 몸값 계산표(1부), 급등한 날 5번 기록표(3부)\n무료 리포트: " + ut("facebook", "cards_caption") + "\n\n※ 공개 공시·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#에이바 #AEVA #라이다 #미국주식"
fbc = {"text": fbc_t, "channels": ["facebook"], "media": {"type": "carousel", "paths": cards}, "channel_text": {"facebook": fbc_t}, "publish_at": iso(7)}
fbt = "현금이 많다는 라이다 회사, 왜 고점 대비 -67.6%?\n\n에이바 테크놀로지스(AEVA), 빛으로 거리와 속도를 함께 재는 4D 라이다를 만드는 미국 회사.\n9월 말 한 주당 현금은 2.12달러로 11월 4일 종가 9.49달러의 약 22%이고, 전환사채 1억 달러를 빼면 0.68달러입니다. 시가총액은 현금의 4.48배입니다.\n\n※ 공개 공시·시세를 정리한 교육용 분석이며 매수·매도 권유가 아닙니다.\n회사 발표로 급등한 날 5번의 한 달 뒤는 리포트 3부 기록표에 정리했습니다.\n이 리포트에서 확인할 수 있는 것: 현금과 몸값 계산표(1부), 급등한 날 5번 기록표(3부)\n무료 리포트: " + ut("facebook", "reels_caption") + "\n\n#에이바 #AEVA #김박사월드"
fb = {"text": fbt, "poll": ["기다림 비용", "고점 공모", "테마 식음"],
      "replies": [{"text": "에이바의 현금과 몸값 계산은 무료 리포트 1부 표, 급등한 날 5번의 20거래일 뒤는 3부 기록표에 정리했습니다.\n" + ut("facebook", "reels_comment")}],
      "channels": ["facebook"], "media": {"type": "reels", "path": f"static/social/{S}/AEVA_shorts.mp4", "cover": f"static/social/{S}/cover.jpg"}, "publish_at": iso(1.2)}
for n, d in ((S, th1), (S + "-th2", th2), (S + "-th3", th3), (S + "-cards", ig), (S + "-reels", fb), (S + "-fbcards", fbc)):
    json.dump(d, open(f"{OUT}/{n}.json", "w"), ensure_ascii=False, indent=1)
print('ok')
