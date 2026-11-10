#!/usr/bin/env python3
# 녹음 전에 귀로 뭉개지기 쉬운 긴 금액·주식 수를 잡는다(70회차 IONQ: ASR이 '구천만'·'사억 삼천이백만'을 뭉개 splice_para 두 번 —
# 녹음 뒤 고치면 맥 TTS 대기·재녹음이 겹쳐 토큰과 시간이 든다. 71회차 IREN부터 TTS 제출 전에 이 검사).
# 사용: python3 num_speak_check.py <narration.txt>
#  - '억' 뒤 만 단위가 두 자리 넘게 이어지는 말(예: 사억 삼천이백만, 이억 이천팔백만)
#  - '만' 앞이 천·백·십·일 네 자리 모두 든 말(예: 칠천삼백팔십삼만)
#  과거 폴더 오탐 점검(11-10): ionq3 1·joby3 4·rdw3 1·eose 4(모두 ASR은 통과했으나 줄여도 뜻이 같음)·iren5·inod3·stx2 0 — 모두 '약 …천만'으로 줄여도 뜻이 같은 값이라 녹음 전 줄임을 기본으로 한다
#  → '약 사억 삼천만'처럼 한 자리로 줄이거나 '약 N억'으로. 정확한 값은 화면·리포트에 둔다.
import re, sys

D = '[일이삼사오육칠팔구]'
PAT = [
    (re.compile(rf'{D}?억\s?(?:{D}?천)?(?:{D}?백)?(?:{D}?십)?{D}?만'), 'eok'),
    (re.compile(rf'{D}?천{D}?백{D}?십{D}?만'), 'man'),
]


def places(s):
    m = s.split('억')[-1]
    return sum(1 for u in '천백십' if u in m) + (1 if re.search(rf'{D}만', m) else 0)


def check(text):
    bad = []
    for i, para in enumerate([p for p in text.split('\n\n') if p.strip()], 1):
        seen = []
        for rx, kind in PAT:
            for m in rx.finditer(para):
                w = m.group(0)
                if kind == 'eok' and places(w) < 2:
                    continue
                if kind == 'man' and (places(w) < 4 or any(w in b for b in seen)):
                    continue
                seen.append(w)
                if para[max(0, m.start() - 2):m.start()].endswith('약 ') and places(w) < 3:
                    continue
                bad.append(f'NUMSPEAK p{i} "{w}" → \'약\' + 앞 두 자리로 줄이기(정확한 값은 화면·리포트)')
    return bad


if __name__ == '__main__':
    bad = check(open(sys.argv[1], encoding='utf-8').read())
    print('\n'.join(bad) if bad else 'NUMSPEAK_OK')
    sys.exit(1 if bad else 0)
