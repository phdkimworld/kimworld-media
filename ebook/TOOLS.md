# 전자책 제작 도구·스킬 목록 (2026-11-21 운영자 "이북 제작에 도움될만한 스킬들 깃헙들 다 찾아와")

남이 만든 스킬·저장소는 **설치 전에 SKILL.md와 스크립트를 끝까지 읽고** 쓴다(외부 코드). 원고는 이 폴더 마크다운이 원본, 나머지는 거기서 만든다.

## 1. 이미 쓸 수 있는 것 (설치 없음)
| 무엇 | 어디 | 쓰는 곳 |
|---|---|---|
| readability-edit | 운영자 계정 스킬 | 장마다 초보 독자 눈높이 다듬기 |
| iterative-logic-review | 운영자 계정 스킬 | 장마다 논리 빈칸·모순 반복 검토(독립 검토 에이전트) |
| pdf · docx 스킬 | 기본 스킬 | 판매용 PDF·교정용 Word |
| Docs 아티팩트 | 대화 | 운영자가 장별 원고에 직접 메모·수정 |
| Pandoc 3.1 | 작업 공간에 설치돼 있음 | 마크다운 → EPUB3·HTML |
| 예측 장부 `review/predictions/ledger.jsonl` · `tools/pred_ledger.py` | 이 저장소 | 책 숫자의 단일 원천(성적·브라이어·보정 표) |

## 2. 원고 쓰기용 Claude 스킬 (외부)
| 스킬 | 저장소 | 쓸모 |
|---|---|---|
| non-fiction-book-factory: book-ideation · book-architect · research-assistant · draft-coach | https://github.com/robertguss/claude-code-toolkit | 논픽션 책 설계(독자 약속·변화 곡선·장별 청사진·근거 공백) → 장별 초고 코칭. TOC v2를 청사진으로 바꾸는 데 가장 맞음 |
| narrative-nonfiction | https://github.com/rhavekost/author-toolkit | 논증형 논픽션: 기초 → 장 전개 → 전체 흐름 점검, 세션 사이 청사진·작업 노트 유지(긴 원고에 유리) |
| book-chapter-generator 등 | https://github.com/dmccreary/ibook-skills | 개념 의존 그래프로 장 순서 잡기(교재형). 참고용 |

## 3. EPUB·PDF 만들기 (외부)
| 도구 | 저장소·문서 | 쓸모 |
|---|---|---|
| epub-creator 스킬 | https://github.com/bluewaves-creations/bluewaves-skills | 마크다운+그림 → EPUB3, 자동 QA(ebooklib 기반) |
| markdown-to-epub 스킬 | https://github.com/smerchek/claude-epub-skill | H1=장·H2=절, 목차·메타데이터 자동 |
| Pandoc EPUB | https://pandoc.org/epub.html | 가장 단순한 길: `pandoc ch*.md -o book.epub --metadata-file meta.yaml --css epub.css` |
| Vivliostyle CLI / Create Book | https://github.com/vivliostyle/vivliostyle-cli · https://docs.vivliostyle.org/create-book.html | CSS로 조판하는 책 PDF·EPUB(일본어 조판에서 나와 한글 세로·가로 조판에 강함) |
| Typst + Pretendard | https://github.com/orioncactus/pretendard · https://typst.app/universe | 빠른 PDF 조판. 한국어 Quarto+Typst 예: https://statkclee.github.io/quarto-craft/ |
| EPUBCheck | https://github.com/w3c/epubcheck (자바) · https://likecoin.github.io/epubcheck-ts/docs/ (TS판) | 유통사 업로드 전 EPUB 검증(필수) |
| 검증 게이트 예시 | https://dev.to/german_yamil_e021eef8710d/assembling-validated-epub3-ebooks-with-pandoc-and-python-metadata-guardrails-and-build-gates-2m1g | Pandoc+Python으로 메타데이터 검사·빌드 게이트 |

## 4. 한국 유통 참고
- 교보·리디 업로드 준비물(제목·저자·출판사명·소개·목차·키워드·가격, 유통 심사 순서): https://brunch.co.kr/@seoulessay/673 — 파일 규격·표지 크기는 각 유통사 출간 가이드에서 최종 확인.
- 구글 플레이 북 파일 가이드: https://support.google.com/books/partner/answer/3424254?hl=ko-KR
- W3C 한국어 조판 요구사항(klreq): https://www.w3.org/TR/2020/NOTE-klreq-20200527

## 5. 권하는 순서 (초안)
1. 설계: TOC_DRAFT v2 → book-architect 방식으로 장별 청사진(이 장이 독자에게 주는 것·근거 예측 ID·숫자)
2. 숫자: 장마다 `pred_ledger.py`로 표를 뽑아 원고에 붙인다(손으로 옮기지 않음)
3. 초고 → readability-edit → iterative-logic-review
4. 빌드: Pandoc으로 EPUB3, Typst 또는 Vivliostyle로 PDF, EPUBCheck 통과
5. 판매처·가격·출시는 운영자 결정(크몽 PDF / 교보·리디 EPUB)
