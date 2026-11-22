# BE(블룸 에너지) 시장·거시·정책 배경 — 기준일 2026-11-20(11월 20일) 확정 종가
만든 때 2026-11-22 14:59 · 다시: `python3 tools/macro_ctx.py BE --date 2026-11-20 --from 2026-11-13 --work /home/claude/x5_1122`

> 쓰는 규칙(SKILL 3.6): 숫자는 이 파일·리포트에 있는 값만. 인과 단정('때문에')은 근거 자료가 있을 때만, 아니면 '같은 날 ~도 움직였다'. 정책 연결은 아래 5절에서 채택한 것만. 투자 권유·전망 단정 금지.

## 1. 시황 (종가 11월 20일 기준, 출처 나스닥 API historical(확정 종가))

업종: 수소·연료전지 발전(데이터센터 전력) · 업종 기준 청정에너지 펀드(ICLN) · 비고 연료전지 전용 ETF 없음 → ICLN(청정에너지), 데이터센터 전력 비교로 VRT

| 대상 | 종가 | 1일 | 5일 | 20일 | 1년(252거래일) | 사건 구간 11월 13일→11월 20일 |
|---|---|---|---|---|---|---|
| BE ← 이번 종목 | 142.39 | -15.3% | -25.8% | -26.3% | +30.7% | -25.8% |
| S&P 500 펀드(SPY) | 689.81 | -3.6% | -8.6% | -9.2% | +4.1% | -8.6% |
| 나스닥 100 펀드(QQQ) | 608.45 | -5.7% | -10.5% | -13.6% | +1.4% | -10.5% |
| 나스닥 종합지수 | 22,617.73 | -5.3% | -10.0% | -12.9% | +0.2% | -10.0% |
| 러셀 2000 소형주 펀드(IWM) | 256.61 | -2.9% | -7.5% | -6.9% | +9.9% | -7.5% |
| 청정에너지 펀드(ICLN) ← 업종 기준 | 13.84 | -4.5% | -12.5% | -13.6% | -16.4% | -12.5% |
| PLUG | 0.96 | -7.1% | -13.8% | -30.7% | -49.7% | -13.8% |
| FCEL | 6.69 | -11.9% | -30.9% | -39.8% | +2.6% | -30.9% |
| VRT | 166.24 | -10.1% | -17.7% | -14.5% | -2.6% | -17.7% |

- VIX(변동성 지수) 35.89 (11월 20일, Cboe) · 5거래일 전 대비 +16.59p · 20거래일 전 대비 +16.44p

## 2. 거시

| 지표 | 값(날짜) | 5회 전 대비 | 20회 전 대비 | 출처 |
|---|---|---|---|---|
| 미 국채 10년 금리 | 4.92% (11월 20일) | -23bp | -4bp | 미 재무부 |
| 미 국채 2년 금리 | 4.63% (11월 20일) | -25bp | -2bp | 미 재무부 |
| 10년-2년 차이 | +29bp (11월 20일) | | | 계산 |
| 광의 달러지수 | 122.65 (11월 13일) | +0.9% | +0.9% | 연준 H.10(주간 공표, 늦음) |
| 달러 강세 펀드(UUP) | 29.62 (11월 20일) | +0.4% | +2.3% | 나스닥 API historical(확정 종가) |
| WTI 현물(배럴당) | 89.53달러 (11월 17일) | -0.1% | -17.0% | EIA(공표 늦음) |

## 3. 시장 동반 분해 (사건 구간 11월 13일 종가 → 11월 20일 종가, 구간 근거: 직전 리포트 없음 → 5거래일)

베타(평소 민감도) = 구간 시작 전 250거래일 하루 수익률 회귀. 예상 = 날마다 베타 × 기준 수익률을 이어 붙임(절편 제외). 평소 흔들림 = 회귀 나머지의 하루 표준편차 × √거래일.

| 기준 | 베타 | 설명력 R² | 구간 기준 등락 | 예상 | 실제 | 차이(고유) | 평소 흔들림 | 판정 |
|---|---|---|---|---|---|---|---|---|
| 나스닥 100 펀드(QQQ) | 3.04 | 0.35 | -10.5% | -29.8% | -25.8% | +4.0%p | ±12.7%p | 시장 동반 쪽(차이가 평소 흔들림 안) |
| 청정에너지 펀드(ICLN) | 2.75 | 0.57 | -12.5% | -31.4% | -25.8% | +5.6%p | ±10.3%p | 시장 동반 쪽(차이가 평소 흔들림 안) |
| 나스닥 100 펀드(QQQ) · 마지막 하루 11월 20일 | 3.04 | | -5.7% | -17.3% | -15.3% | +2.0%p | ±5.7%p | 시장 동반 쪽(차이가 평소 흔들림 안) |
| 청정에너지 펀드(ICLN) · 마지막 하루 11월 20일 | 2.75 | | -4.5% | -12.3% | -15.3% | -3.0%p | ±4.6%p | 시장 동반 쪽(차이가 평소 흔들림 안) |

**한 문장 초안(리포트·대본, 숫자는 위 표 그대로)**: 11월 13일 종가부터 11월 20일 종가까지 5거래일 동안 블룸 에너지는 -25.8%였습니다. 같은 기간 나스닥 100 펀드(QQQ)는 -10.5%였고, 평소 민감도(약 3.0배)로 예상한 움직임은 -29.8%였습니다. 차이는 +4.0%p로, 평소 5거래일 흔들림(±12.7%p) 안입니다.
- 업종 기준: 같은 구간 청정에너지 펀드(ICLN) -12.5%, 업종 민감도 약 2.8배로 예상 -31.4% → 차이 +5.6%p(시장 동반 쪽(차이가 평소 흔들림 안)).

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

최신 연차 보고서: 10-K 제출 2026-02-09 (위험 요인 절) https://www.sec.gov/Archives/edgar/data/1664703/000162828026006516/be-20251231.htm

| 키워드 | 횟수 | 첫 구절(12단어 이하) |
|---|---|---|
| fuel cell | 99 | the global energy transition. We manufacture a versatile fuel cell energy platform, |
| hydrogen | 61 | electricity and the Bloom Electrolyzer™ for producing hydrogen. Our primary product, the |
| investment tax credit | 3 | The U.S. federal government provides businesses with the Investment Tax Credit (ITC) |
| tariff | 61 | multiple initiatives to mitigate the impact of trade tariffs and other trade |
| data center | 53 | Bloom serves Fortune 500 companies across the data center, semiconductor manufacturing, artificial |
| Department of Energy | 3 | commerce. In 2025, FERC as directed by the U.S. Department of Energy |

Federal Register: 최근 180일 제목에 검색어(fuel cell; clean hydrogen; investment tax credit; 48E)가 든 규칙·규칙안·대통령 문서 없음

**채택(에이전트가 채우거나 그대로 둔다)**: 직접 연결 확인 안 됨
- 채택 형식: `YYYY-MM-DD · 무엇(1차 출처 URL) · 연결 고리: 회사 10-K '…' 항목/매출 비중` 한 줄. 연결 근거가 없으면 위 줄을 그대로 둔다(억지 연결 금지).

## 6. 통섭: 같은 구간 핵심 종목 (시장 기준 나스닥 100 펀드(QQQ), 11월 13일→11월 20일)

| 종목 | 베타 | 실제 | 예상 | 차이 | 판정 | 최근 리포트 |
|---|---|---|---|---|---|---|
| 플러그 파워(PLUG) | 1.51 | -13.8% | -15.6% | +1.8%p | 시장 동반 쪽 | /r/plug-2026-11-4/ |
| 실스크(LAES) | 2.14 | -23.0% | -21.6% | -1.4%p | 시장 동반 쪽 | /r/laes-2026-11-5/ |
| 솔리드파워(SLDP) | 1.58 | -23.3% | -16.3% | -7.0%p | 시장 동반 쪽 | /r/sldp-2026-11-4/ |
| BTQ(BTQ) | 2.39 | -28.0% | -24.0% | -4.0%p | 시장 동반 쪽 | /r/btq-2026-11-5/ |
| 조비(JOBY) | 1.68 | -29.1% | -17.2% | -11.9%p | 일부 고유 움직임 | /r/joby-2026-11-4/ |
| 뉴스케일(SMR) | 2.49 | -27.9% | -24.8% | -3.1%p | 시장 동반 쪽 | /r/smr-2026-11-4/ |
| 아이렌(IREN) | 2.93 | -34.9% | -28.8% | -6.2%p | 시장 동반 쪽 | /r/iren-2026-11-5/ |
| 이노데이터(INOD) | 2.23 | -20.7% | -22.5% | +1.8%p | 시장 동반 쪽 | /r/inod-2026-11-2/ |

**기저율 한 문장 초안**: 같은 5거래일 동안 핵심 종목 8개 가운데 7개는 평소 시장 민감도로 예상한 범위 안에서 움직였습니다.

## 7. 그림 초안

`/home/claude/x5_1122/research/macro_figs.json` — figkit 형식(relative: 종목·업종·시장 누적 등락, compare: 예상 vs 실제). 번호(n)·slug를 리포트에 맞게 고치고 figs.json에 합친다. 그림 숫자는 리포트 본문·부록에 먼저 넣는다(easy_check 대조).

## 출처(접속 2026-11-22)

- 나스닥 API historical(확정 종가) — BE·ETF·비교 종목 | https://api.nasdaq.com/api/quote/BE/historical?assetclass=stocks
- Cboe VIX 일별 종가(VIX_History.csv) | https://www.cboe.com/tradable_products/vix/vix_historical_data/
- 미 재무부 일별 국채 수익률 곡선(Daily Treasury Par Yield Curve Rates) | https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve
- 연준 H.10 광의 달러지수(Nominal Broad Dollar Index, 1997년 1월=100, 주간 공표라 며칠 늦음) | https://www.federalreserve.gov/releases/h10/
- EIA 서부텍사스유(WTI) 쿠싱 현물 일별(공표가 며칠 늦음) | https://www.eia.gov/dnav/pet/hist/RWTCD.htm
- 연준 FOMC 회의 일정(공식) | https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
- 미 경제분석국(BEA) 발표 일정(공식) | https://www.bea.gov/news/schedule
- BE 10-K(제출 2026-02-09) 위험 요인 | https://www.sec.gov/Archives/edgar/data/1664703/000162828026006516/be-20251231.htm

## 막힌 원천(NEED.txt)

- BLS 소비자물가(CPI) 일정(403이면 운영자가 공식 페이지 날짜를 review/macro_calendar.md에 적거나 접근 허용): curl -s -A 'Mozilla/5.0 research' 'https://www.bls.gov/schedule/news_release/cpi.htm'
- BLS 고용 보고서(비농업 고용) 일정(403이면 운영자가 공식 페이지 날짜를 review/macro_calendar.md에 적거나 접근 허용): curl -s -A 'Mozilla/5.0 research' 'https://www.bls.gov/schedule/news_release/empsit.htm'
