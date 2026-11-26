#!/usr/bin/env python3
"""영양제 중간광고 제품 직접 링크 (운영자 2026-11-26 "링크는 이제 몰이 아니라 제품 링크를 바로 달기로 했어").

💊 줄이 말하는 '제품 조건'(health_midroll.md 10절 표)을 뒷면 표기(상품 이름)로 만족하는 쿠팡 파트너스 상품 하나를
사이트 건강몰 진열(health/catalog.json — `best`가 있으면 그것 먼저, 없으면 `products`)에서 고르고, 회차 하위 ID
`md<성분 2자><티커 소문자>`(영문·숫자 20자 이하)의 단축 링크를 돌려준다.

사용:
  python3 tools/product_link.py <H1|H2|H3|omega3|lutein|probiotics> <TICKER>        # 고르기 + 캐시 확인
  python3 tools/product_link.py H2 SLDP --set https://link.coupang.com/a/xxxx       # 워크플로 결과 단축 링크를 캐시에 적기
  python3 tools/product_link.py H3 SLDP --url https://www.coupang.com/vp/products/<id> --name "<상품 이름>"  # 진열에 맞는 상품이 없을 때 직접(운영자 확인 뒤)
  python3 tools/product_link.py --list                                               # 캐시 보기
출력 마지막 줄:
  PRODUCT_LINK_OK <하위 ID> <단축 링크>                 → 그대로 💊 줄에
  PRODUCT_LINK_DISPATCH <하위 ID> <임시 긴 링크>        → 아래 MCP 호출로 단축 링크를 만든 뒤 --set. 시간이 없으면 긴 링크(진열 하위 ID hm…)로 올려도 된다
  PRODUCT_LINK_NOMATCH <성분>                          → 조건을 만족하는 상품이 진열에 없음: 성분(H코드)을 바꾸거나 --url로 직접
캐시: review/product_links.json (공개 저장소 — 링크는 어차피 공개 채널에 올라가는 것, 키·토큰 없음)
"""
import json, os, re, sys, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.environ.get('KW_SITE', '/home/user/kimworld-site')
CACHE = os.path.join(ROOT, 'review', 'product_links.json')
REPO = ('phdkimworld', 'kimworld-site')

# 성분 코드표(health_midroll.md 10절과 같아야 한다). cond = 💊 줄·화면 '제품 조건' 문구, ok = 상품 이름이 그 조건을 표기하는지
CODES = {
    'H1': {'ing': 'omega3', 'two': 'om', 'name': '오메가3', 'cond': 'EPA·DHA 합 하루 500mg 이상'},
    'H2': {'ing': 'lutein', 'two': 'lu', 'name': '루테인', 'cond': '루테인 하루 10~20mg'},
    'H3': {'ing': 'probiotics', 'two': 'pb', 'name': '유산균', 'cond': '균주 이름에 비피더스균 락티스'},
}
ING2CODE = {v['ing']: k for k, v in CODES.items()}


def _epa_dha(name):
    n = name.replace(',', '')
    def grab(tag):
        # 'EPA 720mg'(뒤 숫자+mg)가 먼저, 아니면 '500 EPA'(앞 숫자) — '500 EPA 250 DHA'에서 EPA 뒤 250을 EPA로 읽지 않게
        m = re.search(tag + r'\s*(\d{2,4})\s*mg', n, re.I) or re.search(r'(\d{2,4})\s*(?:mg)?\s*' + tag, n, re.I) or re.search(tag + r'\s*(\d{2,4})', n, re.I)
        return int(m.group(1)) if m else 0
    return grab('EPA') + grab('DHA')


def ok(code, name):
    """상품 이름(뒷면 표기)이 조건을 만족하면 (True, 근거) — 이름에 숫자·균주가 안 보이면 고르지 않는다(추정 금지)"""
    if code == 'H1':
        s = _epa_dha(name)
        return (s >= 500, f'이름 표기 EPA+DHA {s}mg') if s else (False, '')
    if code == 'H2':
        m = re.search(r'루테인\s*(\d{1,2})\s*mg', name, re.I) or re.search(r'lutein\s*(\d{1,2})\s*mg', name, re.I)
        return (10 <= int(m.group(1)) <= 20, f'이름 표기 루테인 {m.group(1)}mg') if m else (False, '')
    if code == 'H3':
        m = re.search(r'락티스|lactis|BB-?12|HN019|Bi-07|B420', name, re.I)
        return (True, f'이름 표기 균주 {m.group(0)}') if m else (False, '')
    return (False, '')


def pid(url):
    m = re.search(r'pageKey=(\d+)', url) or re.search(r'/products/(\d+)', url)
    it = re.search(r'itemId=(\d+)', url); vi = re.search(r'vendorItemId=(\d+)', url)
    if not m: return None, None
    q = '&'.join(x for x in (f'itemId={it.group(1)}' if it else '', f'vendorItemId={vi.group(1)}' if vi else '') if x)
    return m.group(1), f'https://www.coupang.com/vp/products/{m.group(1)}' + (f'?{q}' if q else '')


def candidates(code):
    cat = json.load(open(os.path.join(SITE, 'health', 'catalog.json'), encoding='utf-8'))
    ing = CODES[code]['ing']
    best = [x for x in (cat.get('best') or []) if isinstance(x, dict) and (x.get('ing') or x.get('slug') or x.get('ingredient')) == ing]
    pool = best + list((cat.get('products') or {}).get(ing) or [])
    out, seen = [], set()
    for x in pool:
        good, why = ok(code, str(x.get('name', '')))
        p, www = pid(str(x.get('url', '')))
        if not good or not p or p in seen: continue
        seen.add(p); out.append(dict(x, why=why, pid=p, www=www))
    # 한 달 안팎 묶음(6만 원 이하) 먼저 → 최근 진열 → 로켓 → 순위 → 가격
    out.sort(key=lambda x: (int(x.get('price') or 0) > 60000, -int(str(x.get('seen') or '0').replace('-', '') or 0), not x.get('rocket'), int(x.get('rank') or 99), int(x.get('price') or 0)))
    return out


def subid(code, ticker):
    return re.sub(r'[^a-z0-9]', '', f"md{CODES[code]['two']}{ticker.lower()}")[:20]


def load():
    try: return json.load(open(CACHE, encoding='utf-8'))
    except Exception: return {}


def save(c):
    json.dump(c, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True); open(CACHE, 'a').write('\n')


def main():
    a = sys.argv[1:]
    if not a or a[0] in ('-h', '--help'): print(__doc__); return
    if a[0] == '--list':
        for k, v in sorted(load().items()): print(k, v.get('short') or '(단축 없음)', v.get('name', '')[:40])
        return
    code = a[0].upper() if a[0].upper() in CODES else ING2CODE.get(a[0].lower())
    if not code or len(a) < 2: sys.exit('사용: product_link.py <H1|H2|H3|성분> <TICKER> [--set URL | --url URL --name 이름]')
    tk = a[1]; sid = subid(code, tk); c = load(); opt = dict(zip(a[2::2], a[3::2]))
    if '--set' in opt:
        u = opt['--set'].strip()
        if not re.fullmatch(r'https://link\.coupang\.com/a/[A-Za-z0-9]+', u): sys.exit('PRODUCT_LINK_FAIL --set은 https://link.coupang.com/a/… 단축 링크만')
        if sid not in c: sys.exit('PRODUCT_LINK_FAIL 먼저 고르기(인자 없이)를 한 번 돌린다')
        c[sid].update(short=u, set_at=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%MZ')); save(c)
        print(f'PRODUCT_LINK_OK {sid} {u}'); return
    if '--url' in opt:
        p, www = pid(opt['--url'])
        if not p: sys.exit('PRODUCT_LINK_FAIL --url은 https://www.coupang.com/vp/products/<번호>')
        nm = opt.get('--name', '')
        good, why = ok(code, nm)
        if not good: sys.exit(f'PRODUCT_LINK_FAIL --name "{nm}"에 조건({CODES[code]["cond"]}) 표기가 안 보임 — 뒷면 표기와 같은 이름으로')
        pick = {'name': nm, 'why': why, 'pid': p, 'www': www, 'url': ''}
    else:
        cs = candidates(code)
        if not cs:
            print(f'조건: {CODES[code]["cond"]} — 건강몰 진열(health/catalog.json {CODES[code]["ing"]})에 이름으로 확인되는 상품이 없음')
            print(f'PRODUCT_LINK_NOMATCH {CODES[code]["ing"]}'); sys.exit(2)
        pick = cs[0]
    old = c.get(sid) or {}
    if old.get('pid') == pick['pid'] and old.get('short'):
        print(f"제품: {old['name']} ({old.get('why', '')})"); print(f"PRODUCT_LINK_OK {sid} {old['short']}"); return
    c[sid] = {'code': code, 'ticker': tk.upper(), 'ing': CODES[code]['ing'], 'cond': CODES[code]['cond'], 'name': pick['name'], 'why': pick['why'],
              'pid': pick['pid'], 'www': pick['www'], 'long': pick.get('url', ''), 'short': '', 'at': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%MZ')}
    save(c)
    print(f"제품: {pick['name']} ({pick['why']}, 진열 {pick.get('seen', '-')}, {pick.get('price', '-')}원)")
    print(f"조건: {CODES[code]['cond']} · 하위 ID {sid}")
    print('단축 링크 만들기(GitHub MCP):')
    print('  actions_run_trigger ' + json.dumps({'method': 'run_workflow', 'owner': REPO[0], 'repo': REPO[1], 'workflow_id': 'coupang-deeplink.yml', 'ref': 'main',
                                                'inputs': {'urls': pick['www'], 'subid': sid}}, ensure_ascii=False))
    print('  → actions_list(list_workflow_runs, coupang-deeplink.yml)로 run id → actions_get / get_job_logs에서 "::notice title=단축 링크 %s::… -> https://link.coupang.com/a/…"' % sid)
    print(f'  → python3 tools/product_link.py {code} {tk.upper()} --set <단축 링크>')
    print(f"PRODUCT_LINK_DISPATCH {sid} {pick.get('url') or pick['www']}")


if __name__ == '__main__':
    main()
