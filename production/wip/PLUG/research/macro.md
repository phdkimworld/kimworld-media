# PLUG(플러그 파워) 시장·거시·정책 배경 — 기준일 2026-11-25(11월 25일) 확정 종가
만든 때 2026-11-27 06:51 · 다시: `python3 tools/macro_ctx.py PLUG --date 2026-11-25 --from 2026-11-24 --work /dev/shm/plug1127`

> 쓰는 규칙(SKILL 3.6): 숫자는 이 파일·리포트에 있는 값만. 인과 단정('때문에')은 근거 자료가 있을 때만, 아니면 '같은 날 ~도 움직였다'. 정책 연결은 아래 5절에서 채택한 것만. 투자 권유·전망 단정 금지.

**경고**: HDRO 나스닥 API 시세 없음 → ICLN 사용

## 1. 시황 (종가 11월 25일 기준, 출처 나스닥 API historical(확정 종가))

업종: 수소 · 업종 기준 청정에너지 펀드(ICLN) · 비고 HDRO 자료 없으면 ICLN(청정에너지)

| 대상 | 종가 | 1일 | 5일 | 20일 | 1년(252거래일) | 사건 구간 11월 24일→11월 25일 |
|---|---|---|---|---|---|---|
| PLUG ← 이번 종목 | 1.06 | +14.3% | -1.4% | -25.0% | -45.7% | +14.3% |
| S&P 500 펀드(SPY) | 716.70 | -0.3% | -1.8% | -7.2% | +7.2% | -0.3% |
| 나스닥 100 펀드(QQQ) | 633.93 | -0.7% | -3.9% | -12.6% | +4.8% | -0.7% |
| 나스닥 종합지수 | 23,585.80 | -0.6% | -3.5% | -11.2% | +3.1% | -0.6% |
| 러셀 2000 소형주 펀드(IWM) | 268.87 | +0.6% | -0.5% | -4.4% | +12.1% | +0.6% |
| 청정에너지 펀드(ICLN) ← 업종 기준 | 14.20 | +1.0% | -3.5% | -9.8% | -12.8% | +1.0% |
| BE | 152.89 | -2.3% | -10.6% | -33.0% | +60.0% | -2.3% |
| FCEL | 7.44 | +4.8% | -4.1% | -39.9% | +24.0% | +4.8% |

- VIX(변동성 지수) 28.29 (11월 25일, Cboe) · 5거래일 전 대비 +3.73p · 20거래일 전 대비 +11.38p

## 2. 거시

| 지표 | 값(날짜) | 5회 전 대비 | 20회 전 대비 | 출처 |
|---|---|---|---|---|
| 미 국채 10년 금리 | 4.85% (11월 25일) | -22bp | -14bp | 미 재무부 |
| 미 국채 2년 금리 | 4.61% (11월 25일) | -19bp | -9bp | 미 재무부 |
| 10년-2년 차이 | +24bp (11월 25일) | | | 계산 |
| 광의 달러지수 | 123.60 (11월 20일) | +0.8% | +1.8% | 연준 H.10(주간 공표, 늦음) |
| 달러 강세 펀드(UUP) | 29.60 (11월 25일) | -0.1% | +1.9% | 나스닥 API historical(확정 종가) |
| WTI 현물(배럴당) | 82.24달러 (11월 24일) | -8.1% | -20.4% | EIA(공표 늦음) |

## 3. 시장 동반 분해 (사건 구간 11월 24일 종가 → 11월 25일 종가, 구간 근거: 직전 리포트 plug-2026-11-5 data_as_of)

베타(평소 민감도) = 구간 시작 전 250거래일 하루 수익률 회귀. 예상 = 날마다 베타 × 기준 수익률을 이어 붙임(절편 제외). 평소 흔들림 = 회귀 나머지의 하루 표준편차 × √거래일.

| 기준 | 베타 | 설명력 R² | 구간 기준 등락 | 예상 | 실제 | 차이(고유) | 평소 흔들림 | 판정 |
|---|---|---|---|---|---|---|---|---|
| 나스닥 100 펀드(QQQ) | 1.47 | 0.19 | -0.7% | -1.0% | +14.3% | +15.3%p | ±4.5%p | 회사 고유 움직임이 큼(평소 흔들림의 2배 밖 — 회사 사건 확인) |
| 청정에너지 펀드(ICLN) | 1.41 | 0.30 | +1.0% | +1.4% | +14.3% | +12.9%p | ±4.2%p | 회사 고유 움직임이 큼(평소 흔들림의 2배 밖 — 회사 사건 확인) |

**한 문장 초안(리포트·대본, 숫자는 위 표 그대로)**: 11월 24일 종가부터 11월 25일 종가까지 1거래일 동안 플러그 파워는 +14.3%였습니다. 같은 기간 나스닥 100 펀드(QQQ)는 -0.7%였고, 평소 민감도(약 1.5배)로 예상한 움직임은 -1.0%였습니다. 차이는 +15.3%p로, 평소 1거래일 흔들림(±4.5%p) 밖입니다.
- 업종 기준: 같은 구간 청정에너지 펀드(ICLN) +1.0%, 업종 민감도 약 1.4배로 예상 +1.4% → 차이 +12.9%p(회사 고유 움직임이 큼(평소 흔들림의 2배 밖 — 회사 사건 확인)).

## 4. 다음 거시 일정 (공식 일정 페이지 날짜만)

| 날짜 | 일정 |
|---|---|
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

## 6. 통섭: 같은 구간 핵심 종목 (시장 기준 나스닥 100 펀드(QQQ), 11월 24일→11월 25일)

| 종목 | 베타 | 실제 | 예상 | 차이 | 판정 | 최근 리포트 |
|---|---|---|---|---|---|---|
| 실스크(LAES) | 2.03 | +9.9% | -1.3% | +11.2%p | 회사 고유 움직임이 큼 | /r/laes-2026-11-7/ |
| 솔리드파워(SLDP) | 1.53 | +6.1% | -1.0% | +7.1%p | 회사 고유 움직임이 큼 | /r/sldp-2026-11-5/ |
| BTQ(BTQ) | 2.37 | +4.2% | -1.6% | +5.8%p | 시장 동반 쪽 | /r/btq-2026-11-5/ |
| 조비(JOBY) | 1.64 | +11.1% | -1.1% | +12.2%p | 회사 고유 움직임이 큼 | /r/joby-2026-11-5/ |
| 뉴스케일(SMR) | 2.29 | -1.5% | -1.5% | -0.0%p | 시장 동반 쪽 | /r/smr-2026-11-4/ |
| 아이렌(IREN) | 3.02 | -0.8% | -2.0% | +1.2%p | 시장 동반 쪽 | /r/iren-2026-11-6/ |
| 이노데이터(INOD) | 2.16 | +1.6% | -1.4% | +3.0%p | 시장 동반 쪽 | /r/inod-2026-11-2/ |

**기저율 한 문장 초안**: 같은 1거래일 동안 핵심 종목 7개 가운데 4개는 평소 시장 민감도로 예상한 범위 안에서 움직였습니다.

## 7. 그림 초안

`/dev/shm/plug1127/research/macro_figs.json` — figkit 형식(relative: 종목·업종·시장 누적 등락, compare: 예상 vs 실제). 번호(n)·slug를 리포트에 맞게 고치고 figs.json에 합친다. 그림 숫자는 리포트 본문·부록에 먼저 넣는다(easy_check 대조).

## 출처(접속 2026-11-27)

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
