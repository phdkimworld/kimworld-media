# macro_ctx.py 시험 결과 — SLDP(솔리드파워), 기준일 2026-11-20

운영자 2026-11-22 "종목 관련 정보 뿐만 아니라 시황이나 거시경제 지정학 등 관련된 모든 통찰을 다 포함해서 컨텐츠를 제작" → `tools/macro_ctx.py` 첫 시험(2026-11-22).
명령: `python3 tools/macro_ctx.py SLDP --date 2026-11-20 --work /home/claude/macro_ctx/sldp` (약 40초, 캐시 6시간). 같은 날 JOBY도 시험(조비 1거래일 -8.4%, 예상 -9.7%, 차이 +1.3%p 평소 흔들림 안).

## 원천과 숫자 대조 (도구 출력 ↔ 원천을 따로 받아 다시 계산)
| 항목 | 도구 | 원천에서 다시 | 결과 |
|---|---|---|---|
| SLDP 11/17 → 11/20 종가 | -13.5% | 나스닥 API 1.56 → 1.35 = -13.46% | 같음 |
| QQQ 11/17 → 11/20 | -7.4% | 나스닥 API 656.95 → 608.45 = -7.38% | 같음 |
| SLDP 베타(QQQ, 11/17까지 250거래일) | 1.60 | numpy polyfit 따로 계산 1.601 | 같음 |
| 미 국채 10년 11/20 · 5회 전 | 4.92% · -23bp | 재무부 CSV 11/20 4.92, 11/13 5.15 | 같음 |
| 미 국채 2년 11/20 · 20회 전 | 4.63% · -2bp | 재무부 CSV 11/20 4.63, 10/22 4.65 | 같음 |
| VIX 11/20 | 35.89 | Cboe VIX_History.csv 11/20 종가 35.89 | 같음 |
| 다음 FOMC | 12월 9일(8~9일 회의) | 연준 fomccalendars.htm 2026 'December 8-9*' | 같음 |
| BTQ·LAES 같은 구간 | -16.3% · -11.3% | 발행된 btq-2026-11-5 key_points(BTQ -16.3%, 실스크 -11.3%, QQQ -7.4%) | 같음 |
| 아이렌 베타 | 2.97(250거래일) | 주간 결산 pattern-2026-11-22 '약 2.9'(120거래일) | 표본 길이 차이 안에서 일치 |

읽는 법: 3거래일 -13.5% 가운데 평소 시장 민감도로 예상한 몫이 -11.7%, 차이 -1.7%p는 평소 3거래일 흔들림 ±5.7%p 안 → '시장 동반 쪽'. 업종(LIT) 기준으로는 차이 -5.7%p(마지막 하루는 평소 흔들림의 1~2배) — 두 기준이 다르면 리포트는 두 숫자를 모두 쓰고 '시장과는 같은 폭, 배터리 업종보다는 더 내렸다'처럼 쓴다. 정책은 10-K 위험 요인에 tariff 4회·China 2회·DOE 1회, Federal Register 180일 제목 일치 0건 → '직접 연결 확인 안 됨'.
막힌 것: BLS(CPI·고용 일정) 403 → `/home/claude/macro_ctx/NEED.txt`. FRED는 쓰지 않음(재무부·연준 H.10·EIA 공식 원천).

## 도구 출력 원문(research/macro.md)

> 쓰는 규칙(SKILL 3.6): 숫자는 이 파일·리포트에 있는 값만. 인과 단정('때문에')은 근거 자료가 있을 때만, 아니면 '같은 날 ~도 움직였다'. 정책 연결은 아래 5절에서 채택한 것만. 투자 권유·전망 단정 금지.

## 1. 시황 (종가 11월 20일 기준, 출처 나스닥 API historical(확정 종가))

업종: 배터리 · 업종 기준 배터리·리튬 펀드(LIT)

| 대상 | 종가 | 1일 | 5일 | 20일 | 1년(252거래일) | 사건 구간 11월 17일→11월 20일 |
|---|---|---|---|---|---|---|
| SLDP ← 이번 종목 | 1.35 | -10.0% | -23.3% | -31.8% | -75.3% | -13.5% |
| S&P 500 펀드(SPY) | 689.81 | -3.6% | -8.6% | -9.2% | +4.1% | -5.8% |
| 나스닥 100 펀드(QQQ) | 608.45 | -5.7% | -10.5% | -13.6% | +1.4% | -7.4% |
| 나스닥 종합지수 | 22,617.73 | -5.3% | -10.0% | -12.9% | +0.2% | -7.0% |
| 러셀 2000 소형주 펀드(IWM) | 256.61 | -2.9% | -7.5% | -6.9% | +9.9% | -4.6% |
| 배터리·리튬 펀드(LIT) ← 업종 기준 | 51.98 | -4.3% | -11.5% | -14.3% | -17.7% | -7.9% |
| QS | 2.79 | -8.5% | -24.2% | -30.8% | -77.6% | -14.9% |
| ENVX | 1.17 | -9.3% | -26.9% | -58.1% | -84.6% | -14.6% |

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

## 3. 시장 동반 분해 (사건 구간 11월 17일 종가 → 11월 20일 종가, 구간 근거: 직전 리포트 sldp-2026-11-3 data_as_of)

베타(평소 민감도) = 구간 시작 전 250거래일 하루 수익률 회귀. 예상 = 날마다 베타 × 기준 수익률을 이어 붙임(절편 제외). 평소 흔들림 = 회귀 나머지의 하루 표준편차 × √거래일.

| 기준 | 베타 | 설명력 R² | 구간 기준 등락 | 예상 | 실제 | 차이(고유) | 평소 흔들림 | 판정 |
|---|---|---|---|---|---|---|---|---|
| 나스닥 100 펀드(QQQ) | 1.60 | 0.30 | -7.4% | -11.7% | -13.5% | -1.7%p | ±5.7%p | 시장 동반 쪽(차이가 평소 흔들림 안) |
| 배터리·리튬 펀드(LIT) | 0.98 | 0.23 | -7.9% | -7.7% | -13.5% | -5.7%p | ±6.1%p | 시장 동반 쪽(차이가 평소 흔들림 안) |
| 나스닥 100 펀드(QQQ) · 마지막 하루 11월 20일 | 1.60 | | -5.7% | -9.1% | -10.0% | -0.9%p | ±3.3%p | 시장 동반 쪽(차이가 평소 흔들림 안) |
| 배터리·리튬 펀드(LIT) · 마지막 하루 11월 20일 | 0.98 | | -4.3% | -4.3% | -10.0% | -5.7%p | ±3.5%p | 일부 고유 움직임(평소 흔들림의 1~2배) |

**한 문장 초안(리포트·대본, 숫자는 위 표 그대로)**: 11월 17일 종가부터 11월 20일 종가까지 3거래일 동안 솔리드파워는 -13.5%였습니다. 같은 기간 나스닥 100 펀드(QQQ)는 -7.4%였고, 평소 민감도(약 1.6배)로 예상한 움직임은 -11.7%였습니다. 차이는 -1.7%p로, 평소 3거래일 흔들림(±5.7%p) 안입니다.
- 업종 기준: 같은 구간 배터리·리튬 펀드(LIT) -7.9%, 업종 민감도 약 1.0배로 예상 -7.7% → 차이 -5.7%p(시장 동반 쪽(차이가 평소 흔들림 안)).

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

최신 연차 보고서: 10-K 제출 2026-02-25 (위험 요인 절) https://www.sec.gov/Archives/edgar/data/1844862/000110465926019435/sldp-20251231x10k.htm

| 키워드 | 횟수 | 첫 구절(12단어 이하) |
|---|---|---|
| battery | 93 | Solid Power is a U.S.-based leader in solid-state battery technology and manufacturing |
| Inflation Reduction Act | 0 |  |
| tariff | 4 | foreign direct investment rules and regulations, tariffs and quotas, and other related |
| China | 2 | used to power EVs as well as increased competition from China; ● |
| critical mineral | 0 |  |
| Department of Energy | 1 | in May 2025, the “Assistance Agreement”) with the U.S. Department of Energy |

Federal Register: 최근 180일 제목에 검색어(battery; critical minerals; foreign entity of concern; advanced manufacturing production credit)가 든 규칙·규칙안·대통령 문서 없음

**채택(에이전트가 채우거나 그대로 둔다)**: 직접 연결 확인 안 됨
- 채택 형식: `YYYY-MM-DD · 무엇(1차 출처 URL) · 연결 고리: 회사 10-K '…' 항목/매출 비중` 한 줄. 연결 근거가 없으면 위 줄을 그대로 둔다(억지 연결 금지).

## 6. 통섭: 같은 구간 핵심 종목 (시장 기준 나스닥 100 펀드(QQQ), 11월 17일→11월 20일)

| 종목 | 베타 | 실제 | 예상 | 차이 | 판정 | 최근 리포트 |
|---|---|---|---|---|---|---|
| 플러그 파워(PLUG) | 1.51 | -8.9% | -11.1% | +2.2%p | 시장 동반 쪽 | /r/plug-2026-11-4/ |
| 실스크(LAES) | 2.15 | -11.3% | -15.7% | +4.3%p | 시장 동반 쪽 | /r/laes-2026-11-5/ |
| BTQ(BTQ) | 2.51 | -16.3% | -18.1% | +1.9%p | 시장 동반 쪽 | /r/btq-2026-11-5/ |
| 조비(JOBY) | 1.70 | -17.8% | -12.5% | -5.3%p | 시장 동반 쪽 | /r/joby-2026-11-4/ |
| 뉴스케일(SMR) | 2.51 | -17.8% | -18.1% | +0.3%p | 시장 동반 쪽 | /r/smr-2026-11-4/ |
| 아이렌(IREN) | 2.97 | -25.2% | -21.3% | -3.9%p | 시장 동반 쪽 | /r/iren-2026-11-5/ |
| 이노데이터(INOD) | 2.24 | -13.2% | -16.3% | +3.1%p | 시장 동반 쪽 | /r/inod-2026-11-2/ |

**기저율 한 문장 초안**: 같은 3거래일 동안 핵심 종목 7개 가운데 7개는 평소 시장 민감도로 예상한 범위 안에서 움직였습니다.

## 7. 그림 초안

`/home/claude/macro_ctx/sldp/research/macro_figs.json` — figkit 형식(relative: 종목·업종·시장 누적 등락, compare: 예상 vs 실제). 번호(n)·slug를 리포트에 맞게 고치고 figs.json에 합친다. 그림 숫자는 리포트 본문·부록에 먼저 넣는다(easy_check 대조).

## 출처(접속 2026-11-22)

- 나스닥 API historical(확정 종가) — SLDP·ETF·비교 종목 | https://api.nasdaq.com/api/quote/SLDP/historical?assetclass=stocks
- Cboe VIX 일별 종가(VIX_History.csv) | https://www.cboe.com/tradable_products/vix/vix_historical_data/
- 미 재무부 일별 국채 수익률 곡선(Daily Treasury Par Yield Curve Rates) | https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve
- 연준 H.10 광의 달러지수(Nominal Broad Dollar Index, 1997년 1월=100, 주간 공표라 며칠 늦음) | https://www.federalreserve.gov/releases/h10/
- EIA 서부텍사스유(WTI) 쿠싱 현물 일별(공표가 며칠 늦음) | https://www.eia.gov/dnav/pet/hist/RWTCD.htm
- 연준 FOMC 회의 일정(공식) | https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
- 미 경제분석국(BEA) 발표 일정(공식) | https://www.bea.gov/news/schedule
- SLDP 10-K(제출 2026-02-25) 위험 요인 | https://www.sec.gov/Archives/edgar/data/1844862/000110465926019435/sldp-20251231x10k.htm

## 막힌 원천(NEED.txt)

- BLS 소비자물가(CPI) 일정(403이면 운영자가 공식 페이지 날짜를 review/macro_calendar.md에 적거나 접근 허용): curl -s -A 'Mozilla/5.0 research' 'https://www.bls.gov/schedule/news_release/cpi.htm'
- BLS 고용 보고서(비농업 고용) 일정(403이면 운영자가 공식 페이지 날짜를 review/macro_calendar.md에 적거나 접근 허용): curl -s -A 'Mozilla/5.0 research' 'https://www.bls.gov/schedule/news_release/empsit.htm'
