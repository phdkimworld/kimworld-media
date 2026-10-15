# 김박사 월드 영상 제작 지침 v1(2026-10-15) C장 '업로드 전 검증'을 재고, 전달 메시지에 붙일 한 줄을 만든다.
# 사용:
#   python3 video_check.py long  <롱폼.mp4> <slides.json> <upload_meta.json>
#       slides.json 옆의 slides_out/segments.json(make_slide_video.py가 만든다)을 함께 읽는다
#   python3 video_check.py shorts <쇼츠.mp4>
# 하나라도 기준에 걸리면 끝 코드 1. 10초 프레임은 slides_out/check_10s.png 로 저장하니 눈으로 확인한다.
import sys, os, re, json, subprocess

def probe(v):
    o = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,width,height,r_frame_rate',
                        '-show_entries', 'format=duration', '-of', 'json', v], capture_output=True, text=True).stdout
    j = json.loads(o); vs = [s for s in j['streams'] if s['codec_type'] == 'video'][0]
    au = [s for s in j['streams'] if s['codec_type'] == 'audio']
    return vs['width'], vs['height'], vs['r_frame_rate'], vs['codec_name'], (au[0]['codec_name'] if au else None), float(j['format']['duration'])

def gray_frames(v, crop, w=64, h=28, fps=1):
    d = subprocess.run(['ffmpeg', '-v', 'error', '-i', v, '-vf', f'fps={fps},{crop}scale={w}:{h},format=gray', '-f', 'rawvideo', '-'],
                       capture_output=True).stdout
    n = w * h
    return [d[i * n:(i + 1) * n] for i in range(len(d) // n)]

def scene_times(v, thr):
    e = subprocess.run(['ffmpeg', '-hide_banner', '-i', v, '-vf', f"select='gt(scene,{thr})',showinfo", '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    return [float(x) for x in re.findall(r'pts_time:([\d.]+)', e)]

def tail_silence(v, dur):
    e = subprocess.run(['ffmpeg', '-hide_banner', '-i', v, '-af', 'silencedetect=n=-40dB:d=0.1', '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = re.findall(r'silence_start: ([\d.]+)', e); en = re.findall(r'silence_end: ([\d.]+)', e)
    if st and len(st) > len(en): return round(dur - float(st[-1]), 2)
    return 0.0

def long(v, slides, meta):
    fails, out = [], {}
    w, h, fr, vc, ac, dur = probe(v)
    ok = (w, h, fr, vc, ac) == (1920, 1080, '30/1', 'h264', 'aac')
    out['res'] = f'{w}×{h}@{fr.split("/")[0]}'; ok or fails.append(f'규격 {w}×{h} {fr} {vc}/{ac}')
    wd = os.path.join(os.path.dirname(os.path.abspath(slides)), 'slides_out')
    seg = json.load(open(os.path.join(wd, 'segments.json'), encoding='utf-8'))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '10', '-i', v, '-frames:v', '1', os.path.join(wd, 'check_10s.png')])
    # A3 slides.json 빈 화면 점검 + 완성 영상의 본문이 빈 초
    d = json.load(open(slides, encoding='utf-8')); bad = []
    for pi, p in enumerate(d['paras'], 1):
        for s in p['slides']:
            f = s.get('from', 0)
            els = s.get('lines') or s.get('stats') or s.get('items') or s.get('points') or []
            ats = [e.get('at', 0) for e in els]
            if s.get('layout') == 'compare': ats = [s.get('left', {}).get('at', 0), s.get('right', {}).get('at', 0)]
            if s.get('layout') in ('quote', 'source'): ats = [s.get('at', 0)]
            if ats and min(ats) > f: bad.append(f'p{pi} {s.get("layout")} {s.get("title", "")}')
    bad and fails.append(f'빈 화면 슬라이드 {len(bad)}개: {bad[:5]}')
    ads = seg.get('ad', [])
    in_ad = lambda t: any(a - 0.5 <= t <= b + 0.5 for a, b in ads)
    fr_ = gray_frames(v, 'crop=iw:ih*0.78:0:ih*0.22,')
    empty = [i for i, x in enumerate(fr_) if sum(1 for b in x if b > 90) < 6 and not in_ad(i)]
    out['empty'] = len(empty); len(empty) > 2 and fails.append(f'본문 빈 초 {len(empty)}초 {empty[:10]}')
    # A4 화면 전환 간격(미드롤·outro 제외)
    outro0 = seg['duration'] - seg.get('outro_sec', 0)
    cuts = sorted(set([0.0] + scene_times(v, 0.04) + [a for a, b in ads] + [b for a, b in ads] + [outro0]))
    gaps = [(a, b) for a, b in zip(cuts, cuts[1:]) if b <= outro0 + 0.1 and not in_ad((a + b) / 2)]
    lg = max(gaps, key=lambda g: g[1] - g[0]) if gaps else (0, 0)
    out['still'] = round(lg[1] - lg[0]); lg[1] - lg[0] > 15 and fails.append(f'정지 {lg[1]-lg[0]:.0f}초({lg[0]:.0f}~{lg[1]:.0f})')
    # A6 미드롤
    full = round(sum(b - a for a, b in ads)); out['ad'] = f'{full}초({len(ads)}회)+배너 {seg.get("banner_paras", 0)}회'
    full > 30 and fails.append(f'전체 화면 미드롤 {full}초 > 30초')
    # A7 표기
    txt = open(slides, encoding='utf-8').read(); m = re.findall(r'\$[\d.,]+\s*(?:만|억)', txt)
    out['money'] = len(m); m and fails.append(f'표기 위반 {m[:5]}')
    # A8 챕터
    desc = json.load(open(meta, encoding='utf-8'))['description']
    ch = re.findall(r'^\d{1,2}:\d{2}\s', desc, re.M); out['chap'] = len(ch)
    (len(ch) < 3 or not desc.count('00:00')) and fails.append('설명란 챕터 부족')
    # A10 outro
    out['outro'] = round(seg.get('outro_sec', 0)); out['outro'] < 20 and fails.append(f'outro {out["outro"]}초 < 20초')
    line = (f"검증: 해상도 {out['res']} · 10초 훅 확인 필요(check_10s.png) · 빈 화면 {out['empty']}초 · 최장 정지 {out['still']}초 · "
            f"미드롤 전체화면 {out['ad']} · 표기 위반 {out['money']} · 챕터 {out['chap']}개 · outro {out['outro']}초")
    return line, fails

def shorts(v):
    fails = []
    w, h, fr, vc, ac, dur = probe(v)
    ((w, h, fr) != (1080, 1920, '30/1') or dur > 60) and fails.append(f'규격 {w}×{h} {fr} {dur:.1f}초')
    # 하단 30%·오른쪽 15%(높이 45% 아래)에 글자: 밝은 화소가 많은 프레임 수
    bot = gray_frames(v, 'crop=iw:ih*0.30:0:ih*0.70,', 54, 29, 2)
    rgt = gray_frames(v, 'crop=iw*0.15:ih*0.55:iw*0.85:ih*0.45,', 16, 53, 2)
    nb = sum(1 for x in bot if sum(1 for b in x if b > 150) > 8); nr = sum(1 for x in rgt if sum(1 for b in x if b > 150) > 6)
    (nb > 2 or nr > 2) and fails.append(f'안전 영역 글자 프레임 하단 {nb}·오른쪽 {nr}(0.5초 단위)')
    # 쇼츠 요소는 튀어나오는 애니메이션으로 들어와 장면 전환 점수로는 잡히지 않는다.
    # 0.25초 간격 프레임을 비교해 화소 1% 이상이 눈에 띄게(밝기 25 이상) 바뀌면 화면이 바뀐 것으로 센다.
    fq = gray_frames(v, '', 54, 96, 4); n = 54 * 96
    ch = [i / 4 for i in range(1, len(fq)) if sum(1 for x, y in zip(fq[i], fq[i - 1]) if abs(x - y) > 25) > n * 0.01]
    cuts = sorted(set([0.0] + ch + [dur])); ev = [cuts[0]] + [t for p, t in zip(cuts, cuts[1:]) if t - p > 0.3] + [dur]
    lg = max((b - a for a, b in zip(ev, ev[1:])), default=0); lg > 3 and fails.append(f'정지 {lg:.1f}초')
    sil = tail_silence(v, dur); sil > 0.3 and fails.append(f'끝 무음 {sil}초')
    line = f"검증(쇼츠): {w}×{h}@{fr.split('/')[0]} · {dur:.0f}초 · 시각 변화 {len(ev)-2}회 · 최장 정지 {lg:.1f}초 · 끝 무음 {sil}초 · 안전 영역 침범 {nb + nr}"
    return line, fails

if __name__ == '__main__':
    mode = sys.argv[1]
    line, fails = long(*sys.argv[2:5]) if mode == 'long' else shorts(sys.argv[2])
    print(line)
    for f in fails: print('  ✗', f)
    sys.exit(1 if fails else 0)
