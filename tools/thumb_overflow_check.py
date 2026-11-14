# 썸네일 글자가 화면(1280×720) 밖으로 넘치지 않는지 합성 전에 본다(82회차 ASST: b안 72px 문구가 오른쪽 끝을 넘어 잘린 채 렌더 — 눈으로 보고 고침).
# 사용: python3 thumb_overflow_check.py <thumb/custom 폴더>  → a.html·b.html의 글자 요소(.t·.card·.namebar·.biz-chip) 테두리 상자가 화면 안인지
import asyncio, os, sys, glob
D = sys.argv[1]
async def run():
    from playwright.async_api import async_playwright
    bad = []
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 1280, 'height': 720})
        for h in sorted(glob.glob(os.path.join(D, '[ab].html'))):
            await pg.goto('file://' + os.path.abspath(h)); await pg.wait_for_timeout(200)
            boxes = await pg.evaluate('''() => [...document.querySelectorAll('.t,.card,.namebar,.biz-chip')].map(e => {const r = e.getBoundingClientRect(); return [e.innerText.slice(0, 20), r.left, r.top, r.right, r.bottom, e.scrollWidth > e.clientWidth + 2]})''')
            for txt, l, t, r, b, ov in boxes:
                if l < -2 or t < -2 or r > 1282 or b > 722 or ov:
                    bad.append(f'{os.path.basename(h)} "{txt.strip()}" 상자 ({l:.0f},{t:.0f})~({r:.0f},{b:.0f}) 화면 밖' + (' · 칸 안 넘침' if ov else ''))
        await br.close()
    print('\n'.join(bad) if bad else 'THUMB_FIT_OK'); sys.exit(1 if bad else 0)
asyncio.run(run())
