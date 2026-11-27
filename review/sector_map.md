# 티커 → 업종 ETF·비교 종목·정책 검색어 (macro_ctx.py가 읽는 표)

운영자 2026-11-22 "종목 관련 정보 뿐만 아니라 시황이나 거시경제 지정학 등 관련된 모든 통찰을 다 포함해서 컨텐츠를 제작".
`tools/macro_ctx.py`가 아래 '## 표'의 첫 표만 읽는다. 열 순서를 바꾸지 않는다. 새 종목은 한 줄 추가(없으면 도구가 IWM으로 대신하고 경고).

- **업종 ETF**: 쉼표로 여러 개, 앞이 우선. 앞 ETF 시세가 없으면(예: HDRO 나스닥 API 자료 없음) 다음 ETF로 분해한다. 전용 ETF가 없는 업종은 가장 가까운 것(eVTOL → ITA 항공우주·방산, 사유를 비고에).
- **비교 종목**: 같은 업종 대표주. 리포트 '업종·시장 비교' 그림과 동반 표에 함께 쓴다.
- **코인**: `BTC`면 비트코인(크라켄 일봉)과 IBIT를 거시 표에 넣는다(코인 관련 종목만).
- **정책 검색어**: Federal Register API 검색어(`;`로 구분). 결과는 후보일 뿐이다 — 10-K 위험 요인과 맞는 것만 '연결 고리' 한 줄로 채택하고, 없으면 '직접 연결 확인 안 됨'(억지 연결 금지).
- **10-K 키워드**: 최신 연차 보고서(10-K·20-F·40-F)에서 찾을 단어(`;`). 몇 번 나오는지와 첫 구절(12단어 이하)만 적는다.

## 표
| 티커 | 이름 | 업종 | 업종 ETF | 비교 종목 | 코인 | 정책 검색어 | 10-K 키워드 | 비고 |
|---|---|---|---|---|---|---|---|---|
| PLUG | 플러그 파워 | 수소 | HDRO,ICLN | BE,FCEL | - | clean hydrogen;hydrogen production credit;45V | hydrogen;45V;Inflation Reduction Act;tariff;Department of Energy;loan | HDRO 자료 없으면 ICLN(청정에너지) |
| BE | 블룸 에너지 | 수소·연료전지 발전(데이터센터 전력) | ICLN | PLUG,FCEL,VRT | - | fuel cell;clean hydrogen;investment tax credit;48E | fuel cell;hydrogen;investment tax credit;tariff;data center;Department of Energy | 연료전지 전용 ETF 없음 → ICLN(청정에너지), 데이터센터 전력 비교로 VRT |
| LAES | 실스크 | 양자 보안 반도체 | QTUM | BTQ,IONQ | - | post-quantum cryptography;quantum computing;export controls semiconductors | post-quantum;quantum;export control;China;tariff;semiconductor | |
| BTQ | BTQ | 양자 | QTUM | IONQ,LAES | - | post-quantum cryptography;quantum computing | post-quantum;quantum;export control;China;tariff | 40-F·6-K 제출(캐나다) |
| SLDP | 솔리드파워 | 배터리 | LIT | QS,ENVX | - | battery;critical minerals;foreign entity of concern;advanced manufacturing production credit | battery;Inflation Reduction Act;tariff;China;critical mineral;Department of Energy | |
| JOBY | 조비 | eVTOL | ITA,ARKQ | ACHR | - | powered-lift;advanced air mobility;electric vertical takeoff | FAA;certification;tariff;Department of Defense;China;Toyota | eVTOL 전용 ETF 없음 → ITA(항공우주·방산) |
| ACHR | 아처 | eVTOL | ITA,ARKQ | JOBY | - | powered-lift;advanced air mobility;electric vertical takeoff | FAA;certification;tariff;Department of Defense;export control;Boeing | eVTOL 전용 ETF 없음 → ITA(항공우주·방산) |
| SMR | 뉴스케일 | 원전 | URA,NLR | OKLO | - | small modular reactor;nuclear reactor licensing;advanced reactor | NRC;Nuclear Regulatory Commission;Department of Energy;tariff;uranium;TVA | |
| LEU | 센트러스 에너지 | 원전·우라늄 농축 | URA,NLR | SMR,OKLO,CCJ | - | uranium enrichment;HALEU;centrifuge | Department of Energy;NRC;Russian uranium;import ban;waiver;HALEU;tariff | |
| IREN | 아이렌 | AI 데이터센터·채굴 | WGMI | CIFR,APLD | BTC | data center;digital asset;export controls artificial intelligence | bitcoin;tariff;export control;power;China;Microsoft | |
| INOD | 이노데이터 | AI 데이터 | IGV | SOUN | - | artificial intelligence | artificial intelligence;regulation;tariff;customer concentration | |
| APLD | 어플라이드 디지털 | AI 데이터센터 | WGMI | IREN,CORZ | BTC | data center;export controls artificial intelligence | data center;tariff;power;export control;CoreWeave | |
| CLSK | 클린스파크 | AI 데이터센터·채굴 | WGMI | IREN,APLD,CORZ | BTC | data center;digital asset | bitcoin;data center;power;ERCOT;convertible | |
| RGTI | 리게티 | 양자 | QTUM | IONQ,QBTS | - | quantum computing;quantum information science | quantum;export control;China;Department of Energy;DARPA | |
| QBTS | 디웨이브 퀀텀 | 양자 | QTUM | IONQ,RGTI | - | quantum computing;quantum information science;CHIPS and Science Act | quantum;export control;China;tariff;Department of Commerce | |
| ENVX | 에노빅스 | 배터리 | LIT | SLDP,QS | - | battery;critical minerals | battery;tariff;China;Malaysia;Inflation Reduction Act | |
| QS | 퀀텀스케이프 | 배터리 | LIT | SLDP,ENVX | - | battery;critical minerals | battery;tariff;China;Volkswagen;Inflation Reduction Act | |
| LCID | 루시드 | 전기차 | DRIV | RIVN | - | electric vehicle;fuel economy standards | tariff;tax credit;Saudi;electric vehicle | |
| RKLB | 로켓랩 | 우주 | UFO,ARKX | ASTS | - | commercial space launch;space force | NASA;Space Force;tariff;export control;Department of Defense | |
| CEG | 컨스텔레이션 | 원전·전력 | NLR,URA | VST | - | nuclear reactor licensing;electricity transmission | NRC;Nuclear Regulatory Commission;PJM;tariff;production tax credit | |
| SMCI | 슈퍼마이크로 | AI 서버 | SMH | DELL | - | export controls semiconductors;artificial intelligence | export control;China;tariff;Nvidia | |
| SOUN | 사운드하운드 | AI 소프트웨어 | IGV | BBAI | - | artificial intelligence | artificial intelligence;tariff;China | |
| SERV | 서브 로보틱스 | 로봇 | BOTZ | RR | - | autonomous vehicles;sidewalk robots | autonomous;regulation;tariff;Uber | |
| RXRX | 리커전 | 바이오 | XBI | ABCL | - | drug approval | FDA;clinical;tariff | |
| TEM | 템퍼스 AI | AI 헬스케어 | IGV,XBI | RXRX | - | laboratory developed tests;artificial intelligence | FDA;laboratory developed;Medicare;tariff | |
| ASST | 스트라이브 | 비트코인 금고 | WGMI | MSTR | BTC | digital asset | bitcoin;digital asset;tariff | |
| GPUS | 하이퍼스케일 데이터 | AI 데이터센터·채굴 | WGMI | IREN | BTC | data center;digital asset | bitcoin;data center;power | |
| RZLV | 리졸브 AI | AI 쇼핑 소프트웨어 | IWM | SOUN | | e-commerce;payments | e-commerce;payments;digital asset | 11-27 첫 등록(macro_ctx 경고) |
