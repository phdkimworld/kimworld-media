# SLDP(솔리드파워) 시장·거시·정책 배경 — 기준일 2026-11-24(11월 24일) 확정 종가
만든 때 2026-11-25 15:52 · 다시: `python3 tools/macro_ctx.py SLDP --date 2026-11-24 --from 2026-11-20 --work /home/claude/sldp1125`

> 쓰는 규칙(SKILL 3.6): 숫자는 이 파일·리포트에 있는 값만. 인과 단정('때문에')은 근거 자료가 있을 때만, 아니면 '같은 날 ~도 움직였다'. 정책 연결은 아래 5절에서 채택한 것만. 투자 권유·전망 단정 금지.

## 1. 시황 (종가 11월 24일 기준, 출처 나스닥 API historical(확정 종가))

업종: 배터리 · 업종 기준 배터리·리튬 펀드(LIT)

| 대상 | 종가 | 1일 | 5일 | 20일 | 1년(252거래일) | 사건 구간 11월 20일→11월 24일 |
|---|---|---|---|---|---|---|
| SLDP ← 이번 종목 | 1.32 | -6.7% | -15.4% | -34.7% | -73.7% | -2.2% |
| S&P 500 펀드(SPY) | 718.78 | -0.5% | -1.9% | -6.6% | +9.1% | +4.2% |
| 나스닥 100 펀드(QQQ) | 638.10 | -2.0% | -2.9% | -11.5% | +8.1% | +4.9% |
| 나스닥 종합지수 | 23,733.54 | -1.5% | -2.4% | -10.4% | +6.6% | +4.9% |
| 러셀 2000 소형주 펀드(IWM) | 267.14 | +0.5% | -0.7% | -4.7% | +13.4% | +4.1% |
| 배터리·리튬 펀드(LIT) ← 업종 기준 | 53.69 | -1.8% | -4.8% | -14.3% | -10.9% | +3.3% |
| QS | 2.78 | -5.1% | -15.2% | -33.5% | -75.8% | -0.4% |
| ENVX | 1.10 | -2.7% | -19.7% | -67.2% | -85.3% | -6.0% |

- VIX(변동성 지수) 26.36 (11월 24일, Cboe) · 5거래일 전 대비 +0.90p · 20거래일 전 대비 +8.84p

## 2. 거시

| 지표 | 값(날짜) | 5회 전 대비 | 20회 전 대비 | 출처 |
|---|---|---|---|---|
| 미 국채 10년 금리 | 4.91% (11월 24일) | -19bp | -9bp | 미 재무부 |
| 미 국채 2년 금리 | 4.63% (11월 24일) | -17bp | -5bp | 미 재무부 |
| 10년-2년 차이 | +28bp (11월 24일) | | | 계산 |
| 광의 달러지수 | 123.60 (11월 20일) | +0.8% | +1.8% | 연준 H.10(주간 공표, 늦음) |
| 달러 강세 펀드(UUP) | 29.63 (11월 24일) | +0.3% | +1.8% | 나스닥 API historical(확정 종가) |
| WTI 현물(배럴당) | 89.53달러 (11월 17일) | -0.1% | -17.0% | EIA(공표 늦음) |

## 3. 시장 동반 분해 (사건 구간 11월 20일 종가 → 11월 24일 종가, 구간 근거: 직전 리포트 sldp-2026-11-4 data_as_of)

베타(평소 민감도) = 구간 시작 전 250거래일 하루 수익률 회귀. 예상 = 날마다 베타 × 기준 수익률을 이어 붙임(절편 제외). 평소 흔들림 = 회귀 나머지의 하루 표준편차 × √거래일.

| 기준 | 베타 | 설명력 R² | 구간 기준 등락 | 예상 | 실제 | 차이(고유) | 평소 흔들림 | 판정 |
|---|---|---|---|---|---|---|---|---|
| 나스닥 100 펀드(QQQ) | 1.59 | 0.31 | +4.9% | +7.6% | -2.2% | -9.8%p | ±4.7%p | 회사 고유 움직임이 큼(평소 흔들림의 2배 밖 — 회사 사건 확인) |
| 배터리·리튬 펀드(LIT) | 1.00 | 0.24 | +3.3% | +3.3% | -2.2% | -5.5%p | ±4.9%p | 일부 고유 움직임(평소 흔들림의 1~2배) |
| 나스닥 100 펀드(QQQ) · 마지막 하루 11월 24일 | 1.59 | | -2.0% | -3.1% | -6.7% | -3.6%p | ±3.3%p | 일부 고유 움직임(평소 흔들림의 1~2배) |
| 배터리·리튬 펀드(LIT) · 마지막 하루 11월 24일 | 1.00 | | -1.8% | -1.8% | -6.7% | -4.9%p | ±3.5%p | 일부 고유 움직임(평소 흔들림의 1~2배) |

**한 문장 초안(리포트·대본, 숫자는 위 표 그대로)**: 11월 20일 종가부터 11월 24일 종가까지 2거래일 동안 솔리드파워는 -2.2%였습니다. 같은 기간 나스닥 100 펀드(QQQ)는 +4.9%였고, 평소 민감도(약 1.6배)로 예상한 움직임은 +7.6%였습니다. 차이는 -9.8%p로, 평소 2거래일 흔들림(±4.7%p) 밖입니다.
- 업종 기준: 같은 구간 배터리·리튬 펀드(LIT) +3.3%, 업종 민감도 약 1.0배로 예상 +3.3% → 차이 -5.5%p(일부 고유 움직임(평소 흔들림의 1~2배)).

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

## 6. 통섭: 같은 구간 핵심 종목 (시장 기준 나스닥 100 펀드(QQQ), 11월 20일→11월 24일)

| 종목 | 베타 | 실제 | 예상 | 차이 | 판정 | 최근 리포트 |
|---|---|---|---|---|---|---|
| 플러그 파워(PLUG) | 1.52 | -2.6% | +7.3% | -9.9%p | 일부 고유 움직임 | /r/plug-2026-11-5/ |
| 실스크(LAES) | 2.18 | +1.2% | +10.3% | -9.0%p | 일부 고유 움직임 | /r/laes-2026-11-6/ |
| BTQ(BTQ) | 2.40 | +3.9% | +11.2% | -7.4%p | 시장 동반 쪽 | /r/btq-2026-11-5/ |
| 조비(JOBY) | 1.69 | -2.5% | +8.1% | -10.6%p | 회사 고유 움직임이 큼 | /r/joby-2026-11-5/ |
| 뉴스케일(SMR) | 2.43 | -1.8% | +11.4% | -13.2%p | 일부 고유 움직임 | /r/smr-2026-11-4/ |
| 아이렌(IREN) | 2.99 | +9.6% | +13.8% | -4.2%p | 시장 동반 쪽 | /r/iren-2026-11-6/ |
| 이노데이터(INOD) | 2.20 | +11.6% | +10.3% | +1.2%p | 시장 동반 쪽 | /r/inod-2026-11-2/ |

**기저율 한 문장 초안**: 같은 2거래일 동안 핵심 종목 7개 가운데 3개는 평소 시장 민감도로 예상한 범위 안에서 움직였습니다.

## 7. 그림 초안

`/home/claude/sldp1125/research/macro_figs.json` — figkit 형식(relative: 종목·업종·시장 누적 등락, compare: 예상 vs 실제). 번호(n)·slug를 리포트에 맞게 고치고 figs.json에 합친다. 그림 숫자는 리포트 본문·부록에 먼저 넣는다(easy_check 대조).

## 출처(접속 2026-11-25)

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
