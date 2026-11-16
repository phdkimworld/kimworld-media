# 지난 예측 성적 숫자가 리포트·설명란·고정댓글·쇼츠·SNS·카드에서 서로 같은지 본다(94회차 JOBY: 성적 줄을 일곱 곳에 손으로 옮겨 적으며 어긋날 위험).
# 사용: python3 tools/prev_score_sync_check.py <작업 폴더(/home/claude/<t>)> [리포트.md]
#  - '적중 a · 빗나감 b · 진행 중 c'(쉼표·가운뎃점·'확인 전'·'부분' 허용)를 모든 텍스트 산출물에서 뽑아 (적중, 빗나감, 진행/확인 전) 묶음이 하나뿐인지 확인
import sys, os, re, glob, json
W = sys.argv[1]; R = sys.argv[2] if len(sys.argv) > 2 else (glob.glob(os.path.join(W, 'report', '*-20*.md')) or [None])[0]
files = [R] if R else []
for pat in ('video/description.txt', 'video/pinned.txt', 'shorts/upload_meta.json', 'cards/cards.json', 'sns/mk_queue.py'):
    files += glob.glob(os.path.join(W, pat))
rx = re.compile(r'적중\s*(\d+)\s*[,·]\s*(?:부분(?: 적중)?\s*(\d+)\s*[,·]\s*)?빗나감\s*(\d+)(?:\s*[,·]\s*(?:진행 중|확인 전)\s*(\d+))?')
seen = {}
for f in files:
    t = open(f, encoding='utf-8').read()
    if f.endswith('.json'): t = json.dumps(json.load(open(f, encoding='utf-8')), ensure_ascii=False)
    for m in rx.finditer(t):
        k = tuple(int(x or 0) for x in m.groups())
        seen.setdefault(k, set()).add(os.path.relpath(f, W))
if len(seen) > 1:
    for k, v in seen.items(): print('PREV_SCORE_MISMATCH 적중 %d·부분 %d·빗나감 %d·진행 %d:' % k, ', '.join(sorted(v)))
    sys.exit(1)
print('PREV_SCORE_SYNC_OK', ('적중 %d·부분 %d·빗나감 %d·진행 %d' % next(iter(seen))) if seen else '성적 줄 없음', f'({len(files)}개 파일)')
