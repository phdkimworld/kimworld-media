# 구독 전환 시험 기록 (SKILL V3.95, 운영자 2026-11-17 "1 3만 수행")

기준선: 2026-11-10~11-17 채널 조회 +26,887 · 구독 +30 → 1,000회당 1.1명(vidIQ 채널 통계). 판정 2026-12-01.
워터마크: 설정됨 2026-11-17 20:4x ET(`yt_subs.py --watermark` 응답 2xx, 빨간 '구독' 300px 오른쪽 아래·처음부터). 첫 시도는 httplib2 압축 해제 오류 → requests 직접 업로드로 고침. 화면 표시는 API로 확인 불가
영상별 구독 읽기(`--report 14`): 11-20까지 403(분석 권한 없음) → 11-20 12:27 ET 새 토큰(yt-analytics.readonly 포함)으로 읽을 수 있다. 하루 첫 제작 세션이 아래 '영상별 집계'를 채운다(F10). 2026-11-21부터 자료는 사이트 yt-analytics.yml → ops stats/yt_analytics.json(새 키, 컨테이너 키와 무관) → `python3 tools/yt_analytics_read.py --pull --sub-test`. 영상별 수치가 없으면 12-01 판정은 채널 구독자 변화 ÷ 조회로(11-17 20시 ET 구독자 3,340)

| 날짜 | 티커 | 영상 ID | 형태 | 구독 문장 시각(초) |
| --- | --- | --- | --- | --- |
| 11-17 | SLDP | K6zvU0sUeak | B | 330 |
| 2026-11-17 | BTQ | usFP6dPpDX8 | B | 362~414(13번째 문단 끝 문장) |
| 11-18 | IREN | 3c5XFLVO9sM | A | 322 |
| 11-18 | SMR | CpGayNCaSHU | A | 364 |
| 11-18 | JOBY | WBTk2DeqVjA | B | 323 |
| 11-18 | 오답노트1 | CG8DRq8t1dc | B | 332 |
| 11-19 | LAES | 2LuMR4kBlmA | A | 335 |
| 11-19 | JOBY | m2eALHEvv8c | B | 346 |
| 11-20 | PLUG | G4LwNPV5bB8 | A | 358 |
| 11-20 | ENVX | 9XvR-qdcTUE | B | 375 |
| 11-21 | APLD | 1TKhp0NOkYU | A | 281 |
| 11-21 | RGTI | c-8RHgUfHv8 | A | 455 |
| 11-21 | SLDP | JusnxXSiIVQ | B | 326 |
| 11-21 | SMR | LtzNialqBF8 | A | 415 |

## 영상별 집계 (F10 — 숫자는 비공개: phdkimworld/kimworld ops-data `review/sub_test_per_video.md`, 운영자 11-22 "비공개로 옮겨")

- 자료 있는 영상 8/14편 · 1,000회당 구독은 B(질문형) 쪽이 높음 — 관찰 중(12-01 판정) · 갱신 2026-11-22
| 11-21 | INOD | fzbU46COnbk | B | 341 |
| 11-21 | BTQ | oIrfim1wfyY | A | 418 |
| 11-22 | 패턴 결산 | w-5VJA_M-Fc | B | 374 |
| 11-22 | BE | VdSWc4jMjzI | A | 428 |
| 11-22 | ACHR | 76JW6fhIjEw | B | 362 |
| 11-22 | QBTS | PVtpl9NWWQk | A | 456 |
| 11-23 | LAES | zbq6gLjyeVI | A | 454 |
| 11-23 | IREN | MGh3KnhUDAM | A | 357 |
| 11-24 | PLUG | vO2GZt0GbnE | B | 614 |
