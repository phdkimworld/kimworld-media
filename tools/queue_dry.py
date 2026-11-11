#!/usr/bin/env python3
# SNS 대기열 생성기(mk_queue.py)를 업로드 전에 가짜 사이트 폴더에서 돌려 queue_check를 미리 통과시킨다.
# 73회차 NBIS 교훈: 투표 보기 축 주어·불릿 35자·2/2 첫 문장 문제 8건이 업로드 뒤 SNS 단계에서야 걸려 다시 씀.
# 사용: python3 queue_dry.py <mk_queue.py> → QUEUE_DRY_OK / QUEUE_DRY_FAIL(+ queue_check 줄)
import os, re, sys, json, glob, shutil, subprocess, tempfile, datetime
src = open(sys.argv[1], encoding='utf-8').read()
tmp = tempfile.mkdtemp(prefix='qdry-')
q = os.path.join(tmp, 'social/queue'); os.makedirs(q)
src = re.sub(r"^Q = .*$", f"Q = {q!r}; os.makedirs(Q, exist_ok=True)", src, count=1, flags=re.M)
f = os.path.join(tmp, 'mk.py'); open(f, 'w', encoding='utf-8').write(src)
t0 = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5))).isoformat(timespec='seconds')
r = subprocess.run([sys.executable, f, t0], capture_output=True, text=True, cwd=tmp)
if r.returncode: print('QUEUE_DRY_FAIL mk_queue 실행 오류\n' + r.stderr[-800:]); sys.exit(1)
def media(d):
    m = d.get('media') or {}
    for k in ('path', 'cover'):
        if m.get(k): yield m[k]
    yield from m.get('paths', [])
    yield from (d.get('threads_media') or {}).get('paths', [])
files = sorted(glob.glob(os.path.join(q, '*.json')))
for fn in files:
    for p in media(json.load(open(fn, encoding='utf-8'))):
        fp = os.path.join(tmp, p); os.makedirs(os.path.dirname(fp), exist_ok=True); open(fp, 'wb').write(b'\0' * 4096)
r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'queue_check.py')] + [os.path.relpath(x, tmp) for x in files],
                   capture_output=True, text=True, cwd=tmp, env=dict(os.environ, KW_SITE=tmp))
bad = [l for l in r.stdout.splitlines() if l.startswith('BAD') and not re.search(r'cover|빈 화면|파일 없음', l)]
shutil.rmtree(tmp, ignore_errors=True)
print('\n'.join(bad + [f'QUEUE_DRY_FAIL {len(bad)}']) if bad else f'QUEUE_DRY_OK {len(files)}건')
sys.exit(1 if bad else 0)
