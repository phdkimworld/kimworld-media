#!/usr/bin/env python3
"""정규 종목 통합 랭크섬(운영자 지시 2026-11-06 "msi와 요청 여부도 랭킹에 하나로 넣어서 랭크섬").

후보 = 사이트 리포트가 있는 종목 ∪ MSI 점수가 있는 종목(msi/latest.md) ∪ 요청 장부 '대기' 종목 ∪ 사이트 업데이트 요청 종목.
네 항목을 각각 순위로 매겨(동점은 평균 순위) 더한 값이 작을수록 위:
  1) 편당 조회(공개 3일 지난 롱폼 평균, traffic_cut)   — 만든 적 없는 종목은 가운데 순위
  2) 참여율((좋아요+댓글×2)/조회)                       — 만든 적 없는 종목은 가운데 순위
  3) MSI 점수(주식·코인 같은 0~100 척도)                — 점수 없는 종목은 공동 꼴찌
  4) 요청 수(댓글 스레드 수 + 사이트 업데이트 요청 수) — 요청 없는 종목은 공동 꼴찌
제외: 최신 리포트 data_as_of가 7일 안인 종목, 이미 만든 종목 중 트래픽 컷(traffic_cut 랭크섬 상위 절반 밖).
사용: python3 tools/unified_rank.py [--top 15] [--no-web]
"""
import os, re, sys, glob, json, datetime, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); MEDIA = os.path.dirname(HERE)
SITE = os.path.join(os.path.dirname(MEDIA), 'kimworld-site')
sys.path.insert(0, HERE)
from traffic_cut import load, verdict

def latest_asof():
    out = {}
    for f in glob.glob(os.path.join(SITE, 'content/reports/*.md')):
        h = open(f, encoding='utf-8').read(3000)
        t = re.search(r"^ticker:\s*['\"]?([A-Za-z0-9.]+)", h, re.M)
        d = re.search(r"^data_as_of:\s*['\"]?(\d{4}-\d\d-\d\d)", h, re.M)
        if t and d: out[t.group(1).upper()] = max(out.get(t.group(1).upper(), ''), d.group(1))
    return out

def msi_scores():
    txt = open(os.path.join(MEDIA, 'msi/latest.md'), encoding='utf-8').read()
    sc = {}
    for line in txt.split('\n'):
        if re.match(r'^(TOP 5:|- 6~10위:|- 11위 이하:|- 밖:)', line):
            for tk, v in re.findall(r'\b([A-Z][A-Z0-9]{1,6}) (\d{2,3})\b', line):
                sc[tk] = int(v)
    return sc

def requests():
    req = {}
    for line in open(os.path.join(MEDIA, 'requests.md'), encoding='utf-8'):
        c = [x.strip() for x in line.split('|')]
        if len(c) > 4 and c[1].startswith('대기'):
            tk = c[2].upper(); thr = [x for x in re.split(r'[ ,·]+', c[4]) if '@' in x]
            req[tk] = req.get(tk, 0) + max(len(thr), 1 if '2순위' not in c[1] else 0)
    if '--no-web' not in sys.argv:
        try:
            r = subprocess.run(['curl', '-s', '-m', '20', '-A', 'Mozilla/5.0 research',
                                f'https://api.drkimworld.com/v1/requests/top?x={int(datetime.datetime.now().timestamp())}'],
                               capture_output=True, text=True)
            for it in json.loads(r.stdout).get('items', []):
                req[it['t'].upper()] = req.get(it['t'].upper(), 0) + int(it['n'])
        except Exception:
            pass
    return req

def ranks(vals, higher_better=True, missing=None):
    # vals: {k: value or None}; None → missing 정책('mid' 가운데, 'last' 공동 꼴찌)
    ks = list(vals); n = len(ks); have = [k for k in ks if vals[k] is not None]
    srt = sorted(have, key=lambda k: -vals[k] if higher_better else vals[k])
    r = {}; i = 0
    while i < len(srt):
        j = i
        while j + 1 < len(srt) and vals[srt[j + 1]] == vals[srt[i]]: j += 1
        for k in srt[i:j + 1]: r[k] = (i + j) / 2 + 1
        i = j + 1
    miss = [k for k in ks if vals[k] is None]
    for k in miss: r[k] = (n + 1) / 2 if missing == 'mid' else (len(have) + 1 + n) / 2
    return r

def main():
    S = load(); asof = latest_asof(); msi = msi_scores(); req = requests()
    today = datetime.date.today()
    cand = set(S['stat']) | set(msi) | set(req) | set(asof)
    rows = {}
    for k in cand:
        a = asof.get(k)
        age = (today - datetime.date.fromisoformat(a)).days if a else None
        if age is not None and age < 7: continue
        if k in S['stat'] and not verdict(k, S)[0]: continue
        rows[k] = age
    st = S['stat']
    rv = ranks({k: (st[k][0] if k in st else None) for k in rows}, missing='mid')
    re_ = ranks({k: (st[k][1] if k in st else None) for k in rows}, missing='mid')
    rm = ranks({k: msi.get(k) for k in rows}, missing='last')
    rq = ranks({k: (req.get(k) or None) for k in rows}, missing='last')
    tot = {k: rv[k] + re_[k] + rm[k] + rq[k] for k in rows}
    top = int(sys.argv[sys.argv.index('--top') + 1]) if '--top' in sys.argv else 15
    print(f"정규 통합 랭크섬 · 후보 {len(rows)}종목(7일 안 업데이트·트래픽 컷 제외) · 조회·참여는 만든 적 없으면 가운데, MSI·요청은 없으면 공동 꼴찌")
    print('순위 | 종목 | 랭크섬 | 조회 순위 | 참여 순위 | MSI(순위) | 요청(순위) | 최신 리포트')
    for i, k in enumerate(sorted(rows, key=lambda k: (tot[k], -(msi.get(k) or 0))), 1):
        if i > top: break
        age = rows[k]
        print(f"{i} | {k} | {tot[k]:.1f} | {rv[k]:.0f} | {re_[k]:.0f} | {msi.get(k, '-')}({rm[k]:.0f}) | {req.get(k, 0)}({rq[k]:.0f}) | {'신규' if age is None else f'{age}일 전'}")

if __name__ == '__main__':
    main()
