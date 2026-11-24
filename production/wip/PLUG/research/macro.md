# PLUG(플러그 파워) 시장·거시·정책 배경 — 기준일 2026-11-24(11월 24일) 확정 종가
만든 때 2026-11-24 21:53 · 다시: `python3 tools/macro_ctx.py PLUG --date 2026-11-24 --from 2026-11-19 --work /home/claude/x8_1124`

> 쓰는 규칙(SKILL 3.6): 숫자는 이 파일·리포트에 있는 값만. 인과 단정('때문에')은 근거 자료가 있을 때만, 아니면 '같은 날 ~도 움직였다'. 정책 연결은 아래 5절에서 채택한 것만. 투자 권유·전망 단정 금지.

**경고**: HDRO 나스닥 API 시세 없음 → ICLN 사용

## 1. 시황 (종가 11월 24일 기준, 출처 나스닥 API historical(확정 종가))

업종: 수소 · 업종 기준 청정에너지 펀드(ICLN) · 비고 HDRO 자료 없으면 ICLN(청정에너지)

| 대상 | 종가 | 1일 | 5일 | 20일 | 1년(252거래일) | 사건 구간 11월 19일→11월 24일 |
|---|---|---|---|---|---|---|
| PLUG ← 이번 종목 | 0.93 | -6.3% | -11.3% | -33.5% | -53.0% | -9.6% |
| S&P 500 펀드(SPY) | 717.87 | -0.6% | -2.0% | -6.7% | +8.9% | +0.3% |
| 나스닥 100 펀드(QQQ) | 638.10 | -2.0% | -2.9% | -11.5% | +8.1% | -1.1% |
| 나스닥 종합지수 | 9.85 | -100.0% | -100.0% | -100.0% | -100.0% | -100.0% |
| 러셀 2000 소형주 펀드(IWM) | 267.14 | +0.5% | -0.7% | -4.7% | +13.4% | +1.1% |
| 청정에너지 펀드(ICLN) ← 업종 기준 | 14.06 | -1.2% | -5.3% | -11.3% | -12.5% | -3.0% |
| BE | 156.41 | -7.0% | -9.8% | -28.4% | +73.8% | -7.0% |
| FCEL | 7.10 | -8.7% | -13.9% | -41.7% | +13.8% | -6.5% |

- VIX(변동성 지수) 26.62 (11월 23일, Cboe) · 5거래일 전 대비 +3.71p · 20거래일 전 대비 +8.23p

## 2. 거시

| 지표 | 값(날짜) | 5회 전 대비 | 20회 전 대비 | 출처 |
|---|---|---|---|---|
| 미 국채 10년 금리 | 4.91% (11월 24일) | -19bp | -9bp | 미 재무부 |
| 미 국채 2년 금리 | 4.63% (11월 24일) | -17bp | -5bp | 미 재무부 |
| 10년-2년 차이 | +28bp (11월 24일) | | | 계산 |
| 광의 달러지수 | 123.60 (11월 20일) | +0.8% | +1.8% | 연준 H.10(주간 공표, 늦음) |
| 달러 강세 펀드(UUP) | 29.63 (11월 24일) | +0.3% | +1.8% | 나스닥 API historical(확정 종가) |
| WTI 현물(배럴당) | 89.53달러 (11월 17일) | -0.1% | -17.0% | EIA(공표 늦음) |

## 3. 시장 동반 분해 (사건 구간 11월 19일 종가 → 11월 24일 종가, 구간 근거: 직전 리포트 plug-2026-11-4 data_as_of)

베타(평소 민감도) = 구간 시작 전 250거래일 하루 수익률 회귀. 예상 = 날마다 베타 × 기준 수익률을 이어 붙임(절편 제외). 평소 흔들림 = 회귀 나머지의 하루 표준편차 × √거래일.

| 기준 | 베타 | 설명력 R² | 구간 기준 등락 | 예상 | 실제 | 차이(고유) | 평소 흔들림 | 판정 |
|---|---|---|---|---|---|---|---|---|
| 나스닥 100 펀드(QQQ) | 1.55 | 0.18 | -1.1% | -2.0% | -9.6% | -7.6%p | ±7.8%p | 시장 동반 쪽(차이가 평소 흔들림 안) |
| 청정에너지 펀드(ICLN) | 1.39 | 0.29 | -3.0% | -4.2% | -9.6% | -5.4%p | ±7.2%p | 시장 동반 쪽(차이가 평소 흔들림 안) |
| 나스닥 100 펀드(QQQ) · 마지막 하루 11월 24일 | 1.55 | | -2.0% | -3.1% | -6.3% | -3.2%p | ±4.5%p | 시장 동반 쪽(차이가 평소 흔들림 안) |
| 청정에너지 펀드(ICLN) · 마지막 하루 11월 24일 | 1.39 | | -1.2% | -1.7% | -6.3% | -4.6%p | ±4.2%p | 일부 고유 움직임(평소 흔들림의 1~2배) |

**한 문장 초안(리포트·대본, 숫자는 위 표 그대로)**: 11월 19일 종가부터 11월 24일 종가까지 3거래일 동안 플러그 파워는 -9.6%였습니다. 같은 기간 나스닥 100 펀드(QQQ)는 -1.1%였고, 평소 민감도(약 1.5배)로 예상한 움직임은 -2.0%였습니다. 차이는 -7.6%p로, 평소 3거래일 흔들림(±7.8%p) 안입니다.
- 업종 기준: 같은 구간 청정에너지 펀드(ICLN) -3.0%, 업종 민감도 약 1.4배로 예상 -4.2% → 차이 -5.4%p(시장 동반 쪽(차이가 평소 흔들림 안)).

## 4. 다음 거시 일정 (공식 일정 페이지 날짜만)

| 날짜 | 일정 |
|---|---|
| 2026-11-25(11월 25일) | 개인소득·지출(PCE 물가 포함) Personal Income and Outlays, October 2026 |
| 2026-12-09(12월 9일) | FOMC(연준 금리 회의) December 8-9* — 결정 발표는 마지막 날 · 경제전망(점도표) 회의 |
| 2026-12-23(12월 23일) | 개인소득·지출(PCE 물가 포함) Personal Income and Outlays, November 2026 |
| 2027-01-27(1월 27일) | FOMC(연준 금리 회의) January 26-27 — 결정 발표는 마지막 날 |
| 확인 안 됨 | 소비자물가(CPI): 확인 안 됨(BLS 공식 일정 페이지 접근 막힘) |
| 확인 안 됨 | 고용 보고서(비농업 고용): 확인 안 됨(BLS 공식 일정 페이지 접근 막힘) |

## 5. 지정학·정책 (사업과 직접 연결되는 것만)

최신 연차 보고서: 10-K 제출 2026-03-02 (위험 요인 절) https://www.sec.gov/Archives/edgar/data/1093691/000110465926022286/plug-20251231x10k.htm

| 키워드 | 횟수 | 첫 구절(12단어 이하) |
|---|---|---|
| hydrogen | 95 | We may be unable to successfully execute and operate our hydrogen production |
| 45V | 1 | tax incentives relevant to us, including: (i) the Section 45V Clean Hydrogen |
| Inflation Reduction Act | 0 |  |
| tariff | 16 | that may be impacted by market uncertainty, trade and tariff policies, costs |
| Department of Energy | 1 | advancement of American energy dominance through revised Department of Energy policy directives. |
| loan | 13 | profitability. ​ While our activities related to the DOE loan program continue |

Federal Register: 최근 180일 제목에 검색어(clean hydrogen; hydrogen production credit; 45V)가 든 규칙·규칙안·대통령 문서 없음

**채택(에이전트가 채우거나 그대로 둔다)**: 직접 연결 확인 안 됨
- 채택 형식: `YYYY-MM-DD · 무엇(1차 출처 URL) · 연결 고리: 회사 10-K '…' 항목/매출 비중` 한 줄. 연결 근거가 없으면 위 줄을 그대로 둔다(억지 연결 금지).

## 6. 통섭: 같은 구간 핵심 종목 (시장 기준 나스닥 100 펀드(QQQ), 11월 19일→11월 24일)

| 종목 | 베타 | 실제 | 예상 | 차이 | 판정 | 최근 리포트 |
|---|---|---|---|---|---|---|
| 실스크(LAES) | 2.17 | -13.0% | -3.3% | -9.7%p | 일부 고유 움직임 | /r/laes-2026-11-6/ |
| 솔리드파워(SLDP) | 1.58 | -12.0% | -2.1% | -9.9%p | 일부 고유 움직임 | /r/sldp-2026-11-4/ |
| BTQ(BTQ) | 2.46 | -5.3% | -4.1% | -1.2%p | 시장 동반 쪽 | /r/btq-2026-11-5/ |
| 조비(JOBY) | 1.71 | -10.4% | -2.3% | -8.1%p | 일부 고유 움직임 | /r/joby-2026-11-5/ |
| 뉴스케일(SMR) | 2.46 | -13.1% | -4.1% | -9.0%p | 일부 고유 움직임 | /r/smr-2026-11-4/ |
| 아이렌(IREN) | 2.98 | -10.5% | -5.5% | -5.0%p | 시장 동반 쪽 | /r/iren-2026-11-6/ |
| 이노데이터(INOD) | 2.24 | +3.6% | -3.5% | +7.1%p | 시장 동반 쪽 | /r/inod-2026-11-2/ |

**기저율 한 문장 초안**: 같은 3거래일 동안 핵심 종목 7개 가운데 3개는 평소 시장 민감도로 예상한 범위 안에서 움직였습니다.

## 7. 그림 초안

`/home/claude/x8_1124/research/macro_figs.json` — figkit 형식(relative: 종목·업종·시장 누적 등락, compare: 예상 vs 실제). 번호(n)·slug를 리포트에 맞게 고치고 figs.json에 합친다. 그림 숫자는 리포트 본문·부록에 먼저 넣는다(easy_check 대조).

## 출처(접속 2026-11-24)

- 나스닥 API historical(확정 종가) — PLUG·ETF·비교 종목 | https://api.nasdaq.com/api/quote/PLUG/historical?assetclass=stocks
- Cboe VIX 일별 종가(VIX_History.csv) | https://www.cboe.com/tradable_products/vix/vix_historical_data/
- 미 재무부 일별 국채 수익률 곡선(Daily Treasury Par Yield Curve Rates) | https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve
- 연준 H.10 광의 달러지수(Nominal Broad Dollar Index, 1997년 1월=100, 주간 공표라 며칠 늦음) | https://www.federalreserve.gov/releases/h10/
- EIA 서부텍사스유(WTI) 쿠싱 현물 일별(공표가 며칠 늦음) | https://www.eia.gov/dnav/pet/hist/RWTCD.htm
- 연준 FOMC 회의 일정(공식) | https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
- 미 경제분석국(BEA) 발표 일정(공식) | https://www.bea.gov/news/schedule
- PLUG 10-K(제출 2026-03-02) 위험 요인 | https://www.sec.gov/Archives/edgar/data/1093691/000110465926022286/plug-20251231x10k.htm

## 막힌 원천(NEED.txt)

- BLS 소비자물가(CPI) 일정(403이면 운영자가 공식 페이지 날짜를 review/macro_calendar.md에 적거나 접근 허용): curl -s -A 'Mozilla/5.0 research' 'https://www.bls.gov/schedule/news_release/cpi.htm'
- BLS 고용 보고서(비농업 고용) 일정(403이면 운영자가 공식 페이지 날짜를 review/macro_calendar.md에 적거나 접근 허용): curl -s -A 'Mozilla/5.0 research' 'https://www.bls.gov/schedule/news_release/empsit.htm'
