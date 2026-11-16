# 장면 HTML을 시간축으로 넘기며 프레임 단위 캡처 → ffmpeg mp4 (실시간 녹화 아님)
# 사용: python3 render_scene.py 장면.html 출력.mp4 [--fps 30] [--size 1920x1080] [--dur 초] [--frames-dir 폴더] [--crf 20]
# 장면 계약: window.scene = {dur, ready(Promise), seek(t)}  — seek(t) 뒤 화면이 그 시각 그대로여야 한다
import sys, os, time, json, argparse, asyncio, subprocess, resource
from playwright.async_api import async_playwright

def cpu_jiffies():
    with open('/proc/stat') as f: v = list(map(int, f.readline().split()[1:]))
    return sum(v) - v[3] - v[4], sum(v)  # busy, total

async def capture(html, fps, w, h, dur, out_cb, gl_args=True):
    args = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] if gl_args else []
    async with async_playwright() as p:
        b = await p.chromium.launch(args=args)
        pg = await b.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1)
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
        await pg.goto('file://' + os.path.abspath(html)); await pg.wait_for_function('window.scene && window.scene.ready')
        await pg.evaluate('scene.ready'); D = dur or await pg.evaluate('scene.dur')
        info = await pg.evaluate("()=>{const c=document.createElement('canvas').getContext('webgl');if(!c)return 'webgl 없음';const d=c.getExtension('WEBGL_debug_renderer_info');return d?c.getParameter(d.UNMASKED_RENDERER_WEBGL):c.getParameter(c.RENDERER)}")
        n = round(D * fps); clip = None
        for i in range(n):
            await pg.evaluate('t=>scene.seek(t)', i / fps)
            png = await pg.screenshot(type='png', clip=clip)
            await out_cb(i, png)
        await b.close()
    return n, info, errs

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('html'); ap.add_argument('out'); ap.add_argument('--fps', type=int, default=30)
    ap.add_argument('--size', default='1920x1080'); ap.add_argument('--dur', type=float); ap.add_argument('--crf', type=int, default=20)
    ap.add_argument('--frames-dir'); ap.add_argument('--no-gl-args', action='store_true')
    a = ap.parse_args(); w, h = map(int, a.size.split('x'))
    t0 = time.time(); c0 = cpu_jiffies(); r0 = resource.getrusage(resource.RUSAGE_CHILDREN); s0 = resource.getrusage(resource.RUSAGE_SELF)
    ff = None
    if not a.frames_dir:
        ff = subprocess.Popen(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(a.fps), '-c:v', 'png', '-i', '-',
                               '-vf', f'scale={w}:{h}:flags=lanczos,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-crf', str(a.crf),
                               '-r', str(a.fps), '-movflags', '+faststart', a.out], stdin=subprocess.PIPE)
    else: os.makedirs(a.frames_dir, exist_ok=True)
    cap_t = [0.0]
    async def cb(i, png):
        if ff: ff.stdin.write(png)
        else: open(os.path.join(a.frames_dir, f'f{i:05d}.png'), 'wb').write(png)
    n, info, errs = asyncio.run(capture(a.html, a.fps, w, h, a.dur, cb, not a.no_gl_args))
    t_cap = time.time() - t0
    if ff: ff.stdin.close(); ff.wait()
    wall = time.time() - t0; c1 = cpu_jiffies(); r1 = resource.getrusage(resource.RUSAGE_CHILDREN); s1 = resource.getrusage(resource.RUSAGE_SELF)
    busy = (c1[0] - c0[0]) / os.sysconf('SC_CLK_TCK')
    child_cpu = (r1.ru_utime + r1.ru_stime) - (r0.ru_utime + r0.ru_stime); self_cpu = (s1.ru_utime + s1.ru_stime) - (s0.ru_utime + s0.ru_stime)
    rep = {'scene': os.path.basename(a.html), 'frames': n, 'fps': a.fps, 'video_sec': round(n / a.fps, 2), 'wall_sec': round(wall, 1), 'capture_sec': round(t_cap, 1),
           'sec_per_frame': round(wall / n, 3), 'machine_cpu_busy_sec': round(busy, 1), 'avg_cores_busy': round(busy / wall, 2),
           'self_plus_reaped_child_cpu_sec': round(self_cpu + child_cpu, 1), 'cores': os.cpu_count(), 'webgl_renderer': info, 'page_errors': errs[:5],
           'out_mb': round(os.path.getsize(a.out) / 1e6, 2) if ff else None}
    print(json.dumps(rep, ensure_ascii=False))
    json.dump(rep, open(os.path.splitext(a.out)[0] + '.render.json', 'w'), ensure_ascii=False, indent=1)

if __name__ == '__main__': main()
