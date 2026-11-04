import json, sys, datetime as dt
base = dt.datetime.fromisoformat(sys.argv[1])
S = "mrvl-2026-11"; U = f"https://drkimworld.com/r/{S}/"
OUT = "/home/user/kimworld-site/social/queue"
ut = lambda src, c=None: f"{U}?utm_source={src}&utm_medium=social&utm_campaign={S}" + (f"&utm_content={c}" if c else "")
cards = [f"static/social/{S}/cards/card-{i:02d}.jpg" for i in range(1, 11)]
iso = lambda h: (base + dt.timedelta(hours=h)).isoformat(timespec='seconds')
th1 = {"text": "마벨 테크놀로지(MRVL)는 지난 9년 동안 큰 회사를 4번 사들였고, 그중 3번은 발표 날 주가가 올랐다. 그런데 루멘텀 합병은 소문 전날 10월 28일 251.65달러에서 11월 3일 171.97달러로 -31.7%.\n\n숫자로 보면:\n· 루멘텀 1주 = 마벨 4.5주, 주식만 주는 거래\n· 합병 뒤 마벨 기존 주주 약 67%\n· 루멘텀 가격은 합병 가치보다 12.1% 낮음\n\n지난 예측(10월 14일): 적중 0 · 부분 적중 1 · 빗나감 2 · 진행 중 1 — 합병은 시나리오에 없었다. 12월 11일 마벨은 어느 쪽일까?",
       "channels": ["threads"], "poll": ["견조+신뢰 회복", "견조+의심 지속", "실망+신뢰 회복", "실망+의심 지속"],
       "replies": [{"text": "투표하신 시나리오의 판정 기준은 리포트 5부 표에 있다. 답은 리포트 3부 '대형 인수 발표 4번과 이번' 기록표, 루멘텀 할인 계산은 4부다.\n" + U + "\n\n김박사 월드 앱(홈 화면 설치)에서 마벨 테크놀로지를 팔로우하면 12월 판정 뒤 새 리포트 알림을 받을 수 있다.\n\n※ 공개 자료를 정리한 교육용 분석이며 매수·매도 권유가 아님"}],
       "publish_at": iso(0.05), "topic_tag": "주식"}
th2 = {"text": "마벨(MRVL) 인수 4번 중 3번 상승, 루멘텀 합병엔 -31.7%.\n\n합병 조건, 소문 첫날 -13.2%, 업종 대비 하락폭, 과거 인수 기록, 루멘텀 12.1% 할인까지 10장으로 정리했다.\n\n가장 큰 이유는? 합병 의심 / 주식 대가 / 업종 열기 식음 중 하나만 댓글로.",
       "channels": ["threads"], "threads_media": {"paths": cards}, "topic_tag": "주식",
       "replies": [{"text": "대형 인수 4번의 발표 날·20거래일 뒤 숫자는 답은 리포트 3부 기록표에 있다.\n" + ut("threads")}], "publish_at": iso(2)}
th3 = {"text": "11월 3일 루멘텀(LITE) 종가 680.16달러. 합병 조건대로 마벨 4.5주를 받으면 773.87달러다.\n\n시장은 이 합병에 12.1% 할인을 매기고 있다. 완료 예상은 2028년 상반기.\n\n이 할인이 12월 11일까지 8% 안으로 좁혀질까? 그렇게 보는 근거 하나만 댓글로.",
       "channels": ["threads"], "topic_tag": "주식",
       "replies": [{"text": "네 가지 시나리오와 가능성 구간은 답은 리포트 5부 표에 있다.\n" + ut("threads")}], "publish_at": iso(5)}
body = "· 과거 대형 인수 4번 중 3번은 발표 날 상승\n· 루멘텀 합병: 10월 28일 251.65달러 → 11월 3일 171.97달러(-31.7%)\n· 루멘텀 가격은 합병 가치보다 12.1% 낮음\n\n12월 11일, 여러분은 몇 번? 댓글에 번호 하나\n① 실적 견조 + 신뢰 회복 ② 실적 견조 + 의심 지속 ③ 실적 실망 + 신뢰 회복 ④ 실적 실망 + 의심 지속\n\n"
cap = "📊 7장 기록과 9장 투표까지 넘겨 보세요 👉\n\n" + body + "날짜별 기록표는 무료 리포트에 있습니다. 프로필 링크(drkimworld.com) 첫 화면에서 '마벨' 바로 보기\n🔖 저장해 두고 12월 11일 판정 때 다시 보세요\n\n※ 공개 공시·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#마벨 #MRVL #루멘텀 #AI반도체 #미국주식"
ig = {"text": cap, "channels": ["instagram"], "media": {"type": "carousel", "paths": cards}, "publish_at": iso(0.1)}
fbc_t = "마벨(MRVL) 인수 때마다 올랐는데 루멘텀 합병엔 -31.7%? 10장 넘겨 보기\n\n" + body + "이 리포트에서 확인할 수 있는 것: 대형 인수 발표 4번과 이번 기록표(3부)\n무료 리포트: " + ut("facebook", "cards_caption") + "\n\n※ 공개 공시·시세를 정리한 교육용 자료이며 매수·매도 권유가 아닙니다\n\n#마벨 #MRVL #루멘텀 #AI반도체 #미국주식"
fbc = {"text": fbc_t, "channels": ["facebook"], "media": {"type": "carousel", "paths": cards}, "channel_text": {"facebook": fbc_t}, "publish_at": iso(6)}
fbt = "인수할 때마다 오르던 마벨, 루멘텀 합병엔 왜 -31.7%?\n\n마벨 테크놀로지(MRVL), 빅테크의 맞춤형 AI 칩을 설계하는 미국 반도체 회사.\n11월 2일 광 부품 회사 루멘텀을 주식만으로 사들이는 합병을 발표했습니다. 루멘텀 1주당 마벨 4.5주를 주는 조건입니다.\n소문 전날 251.65달러였던 주가는 11월 3일 171.97달러가 됐고, 루멘텀 가격은 합병 가치보다 12.1% 낮습니다.\n\n※ 공개 공시·시세를 정리한 교육용 분석이며 매수·매도 권유가 아닙니다.\n답: 리포트 3부 '대형 인수 발표 4번과 이번' 기록표\n이 리포트에서 확인할 수 있는 것: 대형 인수 발표 4번과 이번 기록표(3부)\n무료 리포트: " + ut("facebook", "reels_caption") + "\n\n#마벨 #MRVL #루멘텀 #김박사월드"
fb = {"text": fbt, "poll": ["합병 의심", "주식 대가", "업종 열기 식음"],
      "replies": [{"text": "마벨의 대형 인수 4번과 이번 루멘텀 합병의 발표 날·20거래일 뒤 기록표를 무료 리포트 3부에 정리했습니다.\n" + ut("facebook", "reels_comment")}],
      "channels": ["facebook"], "media": {"type": "reels", "path": f"static/social/{S}/MRVL_shorts.mp4", "cover": f"static/social/{S}/cover.jpg"}, "publish_at": iso(0.15)}
for n, d in ((S, th1), (S + "-th2", th2), (S + "-th3", th3), (S + "-cards", ig), (S + "-reels", fb), (S + "-fbcards", fbc)):
    json.dump(d, open(f"{OUT}/{n}.json", "w"), ensure_ascii=False, indent=1)
print('ok')
