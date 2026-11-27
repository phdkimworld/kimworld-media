#!/usr/bin/env python3
"""한국어 문체 점검(번역투·AI 관용구·리듬) — 2026-11-27 운영자 "2"(규칙만 가져오기).

규칙 출처: im-not-ai(epoko77-ai, MIT) quick-rules.md 의 패턴 정의를 읽고, 우리 글(대본·설명란·Threads)에 맞는 것만
정규식으로 새로 옮겼다(코드는 가져오지 않음). 내용·숫자·서법(유보·당위)은 건드리지 않고 문체만 본다.
의학·건강 글이라 '~할 수 있다' 같은 유보 표현은 점검하지 않는다(헤지가 의미 — 원 규칙 A-10·G-2도 의학 텍스트는 제외).

사용: python3 tools/kr_style_check.py 파일...   (Threads 대기열 JSON이면 text·reply 를 합쳐서 본다)
종료 1 = 꼭 고칠 것(S1), 0 = 통과(참고 항목은 '참고:'로만 출력)
"""
import json
import re
import sys

S1 = [  # (이름, 패턴, 허용 횟수, 처방)
    ("이중 피동", r"되어지|되어진|지게 된다|지게 됩니다", 0, "'판단된다'처럼 단일 피동이나 능동으로"),
    ("'~에 있어(서)'", r"에 있어서?(?![가-힣]*요)", 0, "'~에서'나 '~을 볼 때'로"),
    ("의의 과장", r"시사하는 바가 크|주목할 만하|매우 중요하", 0, "지우거나 구체적인 결론으로"),
    ("결산 접속어 남발", r"결론적으로|이를 통해|요약하면|정리하자면|그러므로", 2, "1~2개만 남기고 지우기"),
    ("연결어미 뒤 쉼표", r"(?:하고|하며|지만|면서|아서|어서|으며),", 5, "쉼표를 빼고 이어 쓰기"),
]
S2 = [
    ("'~에 대해' 밀집", r"에 대해서?", 2, "'X를 논의'처럼 조사로 바로"),
    ("'단순한 X를 넘어'", r"단순한 [^.\n]{1,20}(?:을|를) 넘어", 0, "'X만이 아니라 Y'로"),
    ("결말 공식", r"할 때입니다|할 때다|시점입니다|순간입니다", 0, "구체 동사로 단언"),
    ("분열문 '중요한 것은'", r"(?:중요한|필요한) 것은|핵심은|관건은", 1, "'방향이 필요합니다'처럼 주어-서술 바로"),
    ("도치 결산 '~하는 이유'", r"하는 이유(?:다|입니다)", 0, "'그래서 ~'로 순방향"),
    ("'~다는 것' 결말", r"다는 것(?:이다|입니다)|다는 뜻(?:이다|입니다)", 1, "'~다'로 바로 끝내기"),
    ("'즉' 남발", r"(?:^|\s)즉[ ,]", 1, "생략하거나 다른 말로"),
    ("이중 조사", r"에서의|으로의|에로의|으로부터의", 0, "절로 풀어 쓰기"),
]


def texts(path):
    if path.endswith(".json"):
        d = json.load(open(path, encoding="utf-8"))
        items = d if isinstance(d, list) else [d]
        for it in items:
            if isinstance(it, dict) and "text" in it:
                yield f"{path}:{it.get('slug', '?')}", it["text"] + "\n\n" + it.get("reply", "").replace("\n===\n", "\n\n")
    else:
        yield path, open(path, encoding="utf-8").read()


def same_endings(t):
    ends = [m[-4:] for m in re.findall(r"[가-힣]+(?=[.?!])", t)]
    run = best = 1
    for a, b in zip(ends, ends[1:]):
        run = run + 1 if a == b else 1
        best = max(best, run)
    return best


def main():
    bad = 0
    for p in sys.argv[1:]:
        for name, t in texts(p):
            t = re.sub(r"https?://\S+", "", t)
            for lab, pat, cap, fix in S1:
                n = len(re.findall(pat, t))
                if n > cap:
                    print(f"✗ {name}: {lab} {n}번 — {fix}"); bad = 1
            for lab, pat, cap, fix in S2:
                n = len(re.findall(pat, t, flags=re.M))
                if n > cap:
                    print(f"  참고: {name}: {lab} {n}번 — {fix}")
            r = same_endings(t)
            if r >= 5:
                print(f"  참고: {name}: 같은 끝말 {r}문장 연속 — 끝맺음을 섞기")
    print("KR_STYLE_OK" if not bad else "KR_STYLE_FIX")
    return bad


if __name__ == "__main__":
    sys.exit(main())
