# 업비트 상장 코인 회차의 화면 가격 단위 검사(90회차 INJ, SKILL 3.3·2026-10-15 복기 '업비트 상장 코인은 가격·반응 모두 원화 종가로 통일, 크라켄 달러를 섞지 않는다').
# 사용: python3 tools/krw_unit_check.py <video 폴더>  — slides.json ticker가 사이트 tickers.yaml에서 코인(theme에 '코인')이면
#   stat big·compare big에 코인 자체 가격을 달러($·달러)로 쓴 화면을 FAIL로 낸다. 같은 화면 제목·라벨에 ETF·펀드·거래액·자금·순자산이 있으면(코인 가격이 아니라 다른 돈) 통과.
import json, os, re, sys
V = sys.argv[1]; d = json.load(open(os.path.join(V, 'slides.json')))
T = d.get('ticker', '')
Y = os.environ.get('KW_SITE', '/home/user/kimworld-site') + '/data/tickers.yaml'
txt = open(Y, encoding='utf-8').read() if os.path.exists(Y) else ''
m = re.search(r'^%s:\n((?:  .*\n)+)' % re.escape(T), txt, re.M)
coin = bool(m and re.search(r'theme:\s*"?코인', m.group(1)))  # '비트코인·AI 데이터센터'(채굴주)는 코인이 아님(96회차 IREN 오탐)
if not coin: print(f'KRW_SKIP {T} 코인 아님'); sys.exit(0)
OK = re.compile(r'ETF|펀드|거래액|자금|순자산|출발|시가총액|매출|수수료|INJC|재단')
bad = []
for pi, p in enumerate(d['paras']):
    for s in p['slides']:
        ctx = ' '.join(str(s.get(k, '')) for k in ('title', 'kicker'))
        bigs = [(x.get('big', ''), x.get('label', '') + ' ' + x.get('note', '')) for x in s.get('stats', [])]
        for side in ('left', 'right'):
            if side in s: bigs.append((s[side].get('big', ''), s[side].get('head', '') + ' ' + ' '.join(s[side].get('lines', []))))
        for big, lab in bigs:
            if re.search(r'\$\s?\d|\d\s?달러', str(big)) and not OK.search(ctx + ' ' + lab + ' ' + str(big)):
                bad.append(f'p{pi} {ctx[:30]} | {big}')
print('\n'.join('KRW_UNIT ' + b + ' → 업비트 원화 종가로(달러는 라벨에 참고로)' for b in bad) if bad else f'KRW_OK {T} 코인 화면 가격 원화')
sys.exit(1 if bad else 0)
