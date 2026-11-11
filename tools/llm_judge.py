#!/usr/bin/env python3
"""발행 전 가독성·'AI 느낌' 심사(운영자 지시 2026-11-11). 경고만 내고 언제나 0으로 끝난다(발행을 막지 않음).

심사 본체는 사이트 저장소 scripts/llm_judge.py(모델 호출·장부는 scripts/llm.py)를 그대로 불러 쓴다.
- 세션에 ANTHROPIC_API_KEY 가 있으면 여기서 바로 심사해 review/judge_<slug>.md 에 쓴다(장부는 사이트 social/llm/usage.json).
- 키가 없으면(no_key, 세션 컨테이너는 보통 이 경우) 경고만 내고, 사이트 judge.yml 결과
  (사이트 social/llm/judge/<slug>.md — 새 리포트를 main 에 올리면 몇 분 뒤 커밋됨)가 있으면 그 내용을 보여 준다.
사용: python3 tools/llm_judge.py <리포트.md 또는 slug> [--wait 분]
  --wait N: 사이트 결과 파일이 없으면 N분까지 1분마다 사이트 저장소를 pull 해 기다린다.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

SITE = Path(os.environ.get("KW_SITE", "/home/user/kimworld-site"))
MEDIA = Path(__file__).resolve().parent.parent


def site_result(slug):
    f = SITE / "social" / "llm" / "judge" / f"{slug}.md"
    return f if f.exists() else None


def main(argv):
    if not argv:
        print(__doc__)
        return 0
    arg = argv[0]
    path = Path(arg) if arg.endswith(".md") else SITE / "content" / "reports" / f"{arg}.md"
    slug = path.stem
    wait = int(argv[argv.index("--wait") + 1]) if "--wait" in argv else 0
    sys.path.insert(0, str(SITE / "scripts"))
    try:
        import llm
        import llm_judge
    except ImportError:
        print(f"::warning::사이트 저장소({SITE})의 scripts/llm_judge.py 를 찾지 못해 심사를 건너뜀(발행은 막지 않음)")
        return 0
    if llm.has_key() and path.exists():
        status, md = llm_judge.judge(path)
        if status == "ok":
            out = MEDIA / "review" / f"judge_{slug}.md"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(md, encoding="utf-8")
            print(md)
            print(f"JUDGE_DONE {out}")
            return 0
        print(f"JUDGE_SKIP {status} — 세션 직접 심사 건너뜀, 사이트 결과를 본다")
    else:
        print("JUDGE_SKIP no_key — 세션에는 키가 없다. 사이트 judge.yml 결과(social/llm/judge/<slug>.md)를 본다")
    for i in range(wait + 1):
        f = site_result(slug)
        if f:
            print(f.read_text(encoding="utf-8"))
            print(f"JUDGE_SITE {f}")
            return 0
        if i < wait:
            time.sleep(60)
            subprocess.run(["git", "pull", "-q", "--rebase", "origin", "main"], cwd=SITE, capture_output=True)
    print(f"::warning::{slug} 심사 결과 없음(키·크레딧 없음이거나 아직 실행 전). 발행은 막지 않는다.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
