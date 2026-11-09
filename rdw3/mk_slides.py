import json
BG = "thumb/custom/bg.png"
def q(f, text, k=None, sub=None, sfx=None):
    s = {"from": f, "layout": "quote", "text": text, "at": f}
    if k: s["kicker"] = k
    if sub: s["sub"] = sub; s["sub_at"] = f
    if sfx: s["sfx"] = sfx
    return s
def stat(f, title, stats, k=None, sfx=None):
    s = {"from": f, "layout": "stat", "title": title, "stats": stats}
    if k: s["kicker"] = k
    if sfx: s["sfx"] = sfx
    return s
def st(at, big, label, tone="gold", note=None):
    d = {"at": at, "big": big, "label": label, "tone": tone}
    if note: d["note"] = note
    return d
def cmp(f, title, l, r, k=None):
    s = {"from": f, "layout": "compare", "title": title, "left": l, "right": r}
    if k: s["kicker"] = k
    return s
def side(at, head, big, lines, tone):
    return {"at": at, "head": head, "big": big, "lines": lines, "tone": tone}
def src(f, kind, orig, tr, srcn, date):
    return {"from": f, "layout": "source", "kind": kind, "orig": orig, "tr": tr, "src": srcn, "date": date, "at": f}
def tl(f, title, items, k=None):
    s = {"from": f, "layout": "timeline", "title": title, "items": items}
    if k: s["kicker"] = k
    return s
def li(f, title, items, k=None):
    s = {"from": f, "layout": "list", "title": title, "items": items}
    if k: s["kicker"] = k
    return s


def pl(f, question, opts):
    return {"from": f, "layout": "poll", "kicker": "투표", "question": question, "at": f,
            "options": [{"at": f + i, "text": o} for i, o in enumerate(opts)], "foot_at": f + 3}

P = []
P = []
# 1 훅
P.append({"slides": [
  {"layout": "hero", "kicker": "RDW · 레드와이어 · 세 번째 추적", "bg": BG, "lines": [
    {"at": 0, "text": "수주잔고 사상 최대", "tone": "up"},
    {"at": 0.3, "text": "실적 첫날 -19.8%", "tone": "down"}]},
  stat(1, "11.05 실적 첫날", [st(1, "-19.8%", "11월 4일 장 마감 뒤 실적", "down")], sfx="boom"),
  stat(2, "11.05 종가", [st(2, "$6.19", "올해 최저 종가", "down")]),
  stat(3, "11.06 다음 날", [st(3, "+16.5%", "$7.21", "up")]),
  q(4, "수주잔고 사상 최대인데\n**실적 날 왜 -19.8%?**", k="질문")]})
# 2 소개
P.append({"slides": [
  stat(0, "오늘의 종목", [st(0, "RDW", "뉴욕증권거래소 · 레드와이어", "gold")], k="김박사 월드"),
  stat(1, "사업", [st(1, "우주·방산", "우주 장비 + 군용 무인기", "blue")]),
  li(2, "오늘의 순서", [
    {"at": 2, "no": "1", "text": "단서 세 가지"},
    {"at": 2, "no": "2", "text": "지켜볼 신호 3"}])]})
# 3 지난 리포트
P.append({"slides": [
  src(0, "지난 리포트", "공급 소화 국면 후반", "남은 주식 판매 한도 3억 5,040만 달러", "김박사 월드 리포트", "2026.10.19"),
  cmp(1, "지난 리포트 이후", side(1, "10.16 종가", "$8.39", ["지난 기준일"], "white"), side(1, "11.06 종가", "-14.1%", ["$7.21"], "down"))]})
# 4 성적표
P.append({"slides": [
  q(0, "지난 예측\n**채점**"),
  stat(1, "시나리오 1", [st(1, "실적 증명", "매출·이익률·주식 수", "gold")]),
  li(2, "그때 꼽은 조건", [
    {"at": 2, "no": "1", "text": "매출 증가", "sub": "3분기 +5.4%"},
    {"at": 2, "no": "2", "text": "이익률 개선", "sub": "매출총이익률 32.3%"},
    {"at": 2, "no": "3", "text": "주식 수 정지", "sub": "+0.09%"}]),
  stat(3, "실적 증명 · 빗나감", [st(3, "-19.8%", "오르는 대신 첫날 하락", "down")]),
  stat(4, "시나리오 2 · 공급 지속", [st(4, "빗나감", "새 주식 판매", "down")]),
  stat(5, "3분기 시장 판매 계약", [st(5, "0주", "판매 없음", "blue")])]})
# 5 성적 + 씨앗
P.append({"ad": [4], "slides": [
  stat(0, "진단 · 공급 소화 후반", [st(0, "부분 적중", "하락은 실적·시장에서", "gold")]),
  li(1, "지난 예측 성적", [
    {"at": 1, "no": "1", "text": "적중 0 · 부분 적중 1", "sub": "진단"},
    {"at": 1, "no": "2", "text": "빗나감 2", "sub": "실적 증명 · 공급 지속"},
    {"at": 2, "no": "3", "text": "진행 중 2", "sub": "예산 충격 · 새 테마"}]),
  q(3, "조건이 켜졌는데\n**왜 정반대?**", k="질문")]})
# 6 단서 1
P.append({"slides": [
  q(0, "단서 1/3\n**실적 첫날의 시장**", k="단서 1", sfx="boom"),
  stat(1, "11.05 나스닥 100 ETF", [st(1, "-6.5%", "QQQ 하루", "down")]),
  cmp(2, "11.05 같은 날", side(2, "로켓랩", "-12.2%", ["RKLB"], "down"), side(2, "AST 스페이스모바일", "-15.2%", ["ASTS"], "down")),
  q(3, "중간선거 뒤\n**기술주·우주주 동반 매도**", sub="보도 내용"),
  stat(4, "11.05 레드와이어", [st(4, "-19.8%", "급락의 한가운데", "down")])]})
# 7 시장 탓?
P.append({"slides": [
  q(0, "그저\n**시장 탓이었나?**"),
  cmp(1, "11.05 하루", side(1, "우주 ETF(UFO)", "-5.6%", ["업종"], "down"), side(1, "레드와이어", "-19.8%", ["RDW"], "down")),
  stat(2, "우주 ETF보다 더 빠진 폭", [st(2, "14.2%p", "11월 5일", "down")]),
  cmp(3, "11.04 → 11.06 이틀 합계", side(3, "로켓랩", "+1.3%", ["제자리 회복"], "up"), side(3, "레드와이어", "-6.6%", ["여전히 아래"], "down")),
  q(4, "시장이 돌아온 뒤\n**남은 차이는?**", k="질문")]})
# 8 단서 2
P.append({"slides": [
  q(0, "단서 2/3\n**회사가 낸 숫자**", k="단서 2", sfx="boom"),
  stat(1, "3분기 매출", [st(1, "+5.4%", "1억 903만 달러 · 1년 전 대비", "up")]),
  stat(2, "시장 예상(S&P 집계)", [st(2, "1억 2,660만", "달러", "gold")]),
  stat(3, "예상 대비", [st(3, "약 14%", "적었다", "down")]),
  q(4, "그 빈자리는\n**어디서?**", k="질문")]})
# 9 방산
P.append({"slides": [
  q(0, "답은\n**방산 부문**"),
  stat(1, "우주 부문 매출", [st(1, "+31.6%", "1년 전 대비", "up")]),
  stat(2, "방산 부문 매출", [st(2, "+31.6%", "우주", "up"), st(2, "-16.0%", "방산 · 무인기", "down")]),
  stat(3, "무인기 생산·출하 시점(공시)", [st(3, "770만", "달러 감소", "down")]),
  stat(4, "재공품·완성품 재고", [st(4, "4,680만", "달러어치", "gold")])]})
# 10 1년 전 + 맛보기
P.append({"ad": [4], "slides": [
  q(0, "이 장면은\n**처음이 아니다**", k="반전", sfx="boom"),
  stat(1, "2025.11.06 1년 전 실적 첫날", [st(1, "-18.1%", "3분기 실적", "down")]),
  cmp(2, "2025.11.06 같은 날", side(2, "로켓랩", "-12.1%", ["업종 급락"], "down"), side(2, "레드와이어", "-18.1%", ["매출 미달"], "down")),
  stat(3, "1년 전 다음 날", [st(3, "+9.7%", "반등", "up")])]})
# 11 이익률
P.append({"slides": [
  q(0, "사상 최고 이익률의\n**사정**", k="반전", sfx="boom"),
  cmp(1, "매출총이익률", side(1, "1년 전", "16.3%", ["3분기"], "white"), side(1, "이번", "32.3%", ["사상 최고"], "up")),
  stat(2, "1년 전 숫자에 든 인수 회계 비용", [st(2, "1,123만", "달러 · 보도", "gold")]),
  stat(3, "조정 기준(보도)", [st(3, "약 27%", "두 분기 모두", "blue")]),
  q(4, "그렇다면\n**현금은?**", k="질문")]})
# 12 단서 3
P.append({"slides": [
  q(0, "단서 3/3\n**현금**", k="단서 3", sfx="boom"),
  stat(1, "잉여현금흐름", [st(1, "영업 − 설비", "영업으로 번 돈 − 설비 투자", "blue")]),
  stat(2, "3분기 잉여현금흐름", [st(2, "-6,635만", "달러 · 한 분기", "down")]),
  cmp(3, "현금이 나간 속도", side(3, "상반기 6개월", "4,800만", ["달러"], "white"), side(3, "3분기 3개월", "6,635만", ["달러"], "down")),
  stat(4, "9월 말 현금", [st(4, "4억 8,890만", "달러", "blue")])]})
# 13 판매 한도
P.append({"slides": [
  q(0, "새 주식은\n**팔지 않았다**"),
  stat(1, "3분기 시장 판매 계약 판매", [st(1, "0주", "10-Q", "blue")]),
  stat(2, "남은 판매 한도", [st(2, "3억 5,040만", "달러", "gold")]),
  stat(3, "7.21달러에 모두 팔면", [st(3, "19.4%", "약 4,860만 주 · 발행주식 대비", "down")]),
  q(4, "올해 약속은\n**지킬 수 있나?**", k="질문")]})
# 14 4분기 문턱 + 두 번째 맛보기
P.append({"ad": [4], "slides": [
  stat(0, "올해 매출 전망(유지)", [st(0, "4.5억~5억", "달러", "gold")]),
  stat(1, "9개월 매출", [st(1, "3억 2,308만", "달러", "white")]),
  stat(2, "4분기 필요 매출(하단)", [st(2, "1억 2,692만", "달러", "gold")]),
  cmp(3, "4분기 문턱", side(3, "3분기 대비", "+16.4%", ["더 팔아야"], "down"), side(3, "올해 최대", "2분기", ["보다도 큼"], "down"))]})
# 15 과거 기록
P.append({"slides": [
  q(0, "이제\n**과거로**", k="기록", sfx="boom"),
  stat(1, "2022년 이후 분기 실적", [st(1, "20번", "이번 포함", "gold")]),
  stat(2, "첫날 -10% 넘게", [st(2, "5번", "이번 제외", "down")]),
  stat(3, "다음 날 반등", [st(3, "5번 중 4번", "첫날 종가 대비 상승", "up")]),
  stat(4, "20거래일 뒤 실적 전 종가 위", [st(4, "5번 중 1번", "나머지 4번은 더 낮았다", "down")], sfx="boom")]})
# 16 이번 반등
P.append({"slides": [
  cmp(0, "다음 날 반등", side(0, "과거 5번 최대", "+9.7%", ["2025.11"], "white"), side(0, "이번", "+16.5%", ["11.06"], "up")),
  cmp(1, "같은 회사의 실적 첫날", side(1, "8월 6일", "+10.4%", ["2분기"], "up"), side(1, "11월 5일", "-19.8%", ["3분기"], "down")),
  q(2, "무엇이\n**시장의 눈을 바꿨나?**", k="질문")]})
# 17 가설 1
P.append({"slides": [
  q(0, "가설 1\n**시장 전체의 매도**", k="가설 1", sfx="boom"),
  stat(1, "11.05 우주주", [st(1, "-12.2%", "로켓랩", "down"), st(1, "-13.2%", "인튜이티브 머신스", "down")]),
  q(2, "하락의 큰 부분은\n**시장의 물결**"),
  cmp(3, "약점 · 이틀 합계", side(3, "로켓랩", "+1.3%", ["회복"], "up"), side(3, "레드와이어", "-6.6%", ["아래"], "down"))]})
# 18 가설 2
P.append({"slides": [
  q(0, "가설 2\n**방산 출하 지연**", k="가설 2", sfx="boom"),
  stat(1, "예상 대비 매출", [st(1, "약 14%", "적었다", "down")]),
  q(2, "사라진 게 아니라\n**뒤로 밀린 매출**"),
  stat(3, "3분기 북투빌", [st(3, "1.73", "새 주문 ÷ 매출", "up")]),
  q(4, "약점\n**4분기에 몰아서 넘겨야**")]})
# 19 가설 3
P.append({"slides": [
  q(0, "가설 3\n**현금 소진**", k="가설 3", sfx="boom"),
  stat(1, "3분기 잉여현금흐름", [st(1, "-6,635만", "달러", "down")]),
  q(2, "이익률보다\n**돈이 나가는 속도**"),
  stat(3, "약점 · 9월 말 현금", [st(3, "4억 8,890만", "달러 · 아직 넉넉", "blue")]),
  li(4, "리포트 5부 시나리오", [
    {"at": 4, "no": "1", "text": "판매 재개 · 전망 달성", "sub": "두 축 2×2"},
    {"at": 4, "no": "2", "text": "네 가지 · 가능성 구간", "sub": "4분기 실적 판정"}])]})
# 20 되불러오기
P.append({"ad": [1], "slides": [
  q(0, "이번 반등은\n**한 달 뒤까지 남을까?**", k="판단")]})
# 21 신호
P.append({"slides": [
  q(0, "지켜볼 신호\n**세 가지**", k="지켜볼 신호"),
  stat(1, "신호 1 · 12월 3일 종가", [st(1, "$7.72", "실적 전 종가 되찾나", "gold")]),
  stat(2, "신호 2 · 12월 11일", [st(2, "예산", "임시 예산 만료", "blue")]),
  stat(3, "신호 3 · 다음 분기 보고서", [st(3, "3억 5,040만", "남은 판매 한도 쓰였나", "blue")])]})
# 22 정리
P.append({"slides": [
  cmp(0, "3분기 실적", side(0, "수주잔고", "6억 1,967만", ["사상 최대"], "up"), side(0, "매출총이익률", "32.3%", ["사상 최고"], "up")),
  li(1, "시장이 먼저 본 것", [
    {"at": 1, "no": "1", "text": "업종 급락", "sub": "11.05 QQQ -6.5%"},
    {"at": 1, "no": "2", "text": "밀린 매출", "sub": "예상 대비 약 14%"},
    {"at": 1, "no": "3", "text": "빠져나간 현금", "sub": "-6,635만 달러"}]),
  q(2, "진짜 시험은\n**4분기 매출**")]})
# 23 닫기
P.append({"ad": [0, 1, 2], "slides": [
  q(0, "대응 전략과 체크리스트\n**고정 댓글 리포트**"),
  stat(1, "홈페이지에서 팔로우", [st(1, "알림", "앱 설치 · 새 리포트", "blue")]),
  stat(2, "카톡으로 공유", [st(2, "12.03", "다음 결과 때 같이 확인", "gold")])]})
# 24 투표
P.append({"slides": [
  q(0, "마지막으로\n**투표 하나**"),
  q(1, "수주잔고 사상 최대인데\n**끌어내린 가장 큰 이유는?**", k="질문"),
  pl(2, "수주잔고 사상 최대인데 끌어내린 가장 큰 이유는?", ["시장 전체의 매도", "방산 출하 지연", "현금 소진"])]})
# 25 outro
P.append({"slides": [
  {"layout": "outro", "lines": [{"at": 0, "text": "댓글에 ①·②·③ 번호로"}, {"at": 1, "text": "다음 미스터리 종목도 댓글에서"}, {"at": 2, "text": "김박사 월드"}]}]})

deck = {"ticker": "RDW", "name": "레드와이어",
        "midroll": "../kit/rdw_youtube_midroll_1920x1080.png",
        "midroll_app": "../kit/rdw_youtube_midroll_app_1920x1080.png",
        "paras": P}
json.dump(deck, open("/home/claude/rdw3/video/slides.json", "w"), ensure_ascii=False, indent=1)
print(len(P))
