#!/usr/bin/env python3
"""Three-wall looping reel. Wall 1 = the original 1-50 clips (presenter removed), walls 2 and 3 = the 50-100
clips. Every clip comes forward from its own tile with its own sound; a promo (music-only or voice-over)
plays full screen after a random 3, 4 or 5 clips; the same person never comes forward twice in a row and
the same promo style or theme never runs twice in a row."""
import glob, json, os, random, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
S = '/tmp/claude-0/-home-user/f2431104-f768-5341-9abb-88e318700789/scratchpad/promo'
A = '/tmp/claude-0/-home-user-buddy-up-train/f2431104-f768-5341-9abb-88e318700789/scratchpad'
O = S + '/wall2/work3'; os.makedirs(O, exist_ok=True)
FEAT = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0
AIN = 0.6; COLS, ROWS, TW, TH = 13, 4, 148, 270; SLOTS = COLS * ROWS; WALLLEN = 30
rng = random.Random(7)

# --- clips and who is in them (same shoot = same person) ---
EXCL_OLD = {5, 6, 15, 17, 29, 30, 37, 47, 48}
GROUP_OLD = {4: 'A', 13: 'A', 14: 'A', 7: 'C', 8: 'C', 10: 'E', 39: 'E', 16: 'X', 18: 'X', 19: 'X', 32: 'X', 33: 'X', 40: 'X',
             25: 'J', 26: 'J', 27: 'J', 28: 'J', 42: 'P', 46: 'P', 31: 'E2', 38: 'E2'}
EXCL_NEW = {2}
GROUP_NEW = {3: 'b', 13: 'b', 14: 'b', 8: 'd', 20: 'd', 34: 'd', 9: 'e', 19: 'e', 38: 'f', 39: 'f', 40: 'f', 49: 'f', 50: 'f', 10: 'g', 17: 'g',
             15: 'i', 16: 'i', 18: 'j', 28: 'j', 22: 'k', 23: 'k', 55: 'k', 56: 'k', 24: 'l', 31: 'l', 26: 'n', 43: 'n', 29: 'p', 30: 'p', 53: 'p', 54: 'p',
             33: 'r', 41: 'r', 48: 'r', 52: 'r', 35: 's', 46: 's', 36: 't', 37: 't', 45: 'w', 59: 'w', 57: 'z', 60: 'z', 62: 'bb', 63: 'bb', 1: 'a', 61: 'a'}
old = sorted(glob.glob(A + '/clips-raw/*.mp4'))
old = [(p, GROUP_OLD.get(i, f'o{i}')) for i, p in enumerate(old, 1) if i not in EXCL_OLD]
new_names = open(S + '/clips50/order.txt').read().split()
new = [(f'{S}/clips50/{n}', GROUP_NEW.get(i, f'n{i}')) for i, n in enumerate(new_names, 1) if i not in EXCL_NEW]
def has_audio(f):
    return 'audio' in subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', f]).decode()
old = [c for c in old if has_audio(c[0])]; new = [c for c in new if has_audio(c[0])]   # nothing silent comes forward
half = (len(new) + 1) // 2
walls = [old, new[:half], new[half:]]
promos = [(p, os.path.basename(p).split('-')[1], os.path.basename(p).split('-24s')[0].split('-', 2)[2]) for p in sorted(glob.glob(S + '/sets2/*.mp4')) + sorted(glob.glob(S + '/sets2vo/*.mp4'))]
# the client's own five reference promos join the pool (style 'ref', theme = file name)
U = '/root/.claude/uploads/f2431104-f768-5341-9abb-88e318700789'
promos += [(f'{U}/{n}.mp4', 'ref', n.split('-', 1)[1]) for n in ['70d06d36-weight_loss_guesswork_original_landscape', '58f6bb94-weight_loss_guesswork_landscape',
           '836aaa9f-weight_loss_guesswork_original_2_landscape', '367fc4bc-plans_built_around_your_goal_original_landscape', '331d0328-weight_loss_guesswork_alt_landscape']]
promos = [p for p in promos if has_audio(p[0])]   # silent promos are out

def order_no_repeat(items, prev_group=None):
    """Shuffle, then fix any two neighbours from the same shoot by swapping forward."""
    items = items[:]; rng.shuffle(items)
    for _ in range(20):
        ok = True; last = prev_group
        for i in range(len(items)):
            if items[i][1] == last:
                for j in range(i + 1, len(items)):
                    if items[j][1] != last and (j + 1 >= len(items) or items[j + 1][1] != items[i][1]):
                        items[i], items[j] = items[j], items[i]; break
                else: ok = False
            last = items[i][1]
        if ok: break
    return items

def run(c): subprocess.run(c, check=True)
def probe(f):
    j = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,width,height', '-show_entries', 'format=duration', '-of', 'json', f]))
    v = [s for s in j['streams'] if s['codec_type'] == 'video'][0]
    return int(v['width']), int(v['height']), float(j['format']['duration']), any(s['codec_type'] == 'audio' for s in j['streams'])
stage = sys.argv[1] if len(sys.argv) > 1 else 'all'
print(f'walls: {[len(w) for w in walls]} clips, {len(promos)} promos')

if stage in ('all', 'tiles'):
    def tile(args):
        w, i = args; src = walls[w][i % len(walls[w])][0]; out = f'{O}/tile-{w}-{i:02d}.mp4'
        if os.path.exists(out): return
        run(['ffmpeg', '-v', 'error', '-y', '-stream_loop', '-1', '-i', src, '-t', str(WALLLEN), '-an',
             '-vf', f'scale={TW}:{TH}:force_original_aspect_ratio=increase,crop={TW}:{TH},fps=30,setsar=1,format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', out])
    with ThreadPoolExecutor(4) as ex: list(ex.map(tile, [(w, i) for w in range(3) for i in range(SLOTS)]))
    for w in range(3):
        if os.path.exists(f'{O}/wall-{w}.mp4'): continue
        args = ['ffmpeg', '-v', 'error', '-y']
        for i in range(SLOTS): args += ['-i', f'{O}/tile-{w}-{i:02d}.mp4']
        layout = '|'.join(f'{(i % COLS) * TW}_{(i // COLS) * TH}' for i in range(SLOTS))
        fc = ''.join(f'[{i}:v]' for i in range(SLOTS)) + f'xstack=inputs={SLOTS}:layout={layout}[g];[g]crop=1920:1080:2:0,format=yuv420p[v]'
        run(args + ['-filter_complex', fc, '-map', '[v]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-an', f'{O}/wall-{w}.mp4'])

if stage in ('all', 'segs'):
    # the running order: per wall, people never twice in a row (across the wall boundary too); promos at random gaps
    plan = []; last_group = None; last_style = None; last_theme = None; promo_pool = promos[:]; rng.shuffle(promo_pool); pi = 0
    gap = rng.choice([3, 4, 5]); since = 0
    for w in range(3):
        ordered = order_no_repeat(walls[w], last_group)
        for path, group in ordered:
            i = walls[w].index((path, group)); plan.append(('clip', w, i, path)); last_group = group; since += 1
            if since >= gap:
                for _ in range(len(promo_pool)):
                    cand = promo_pool[pi % len(promo_pool)]; pi += 1
                    if cand[1] != last_style and cand[2] != last_theme: break
                plan.append(('promo', cand[0])); last_style, last_theme = cand[1], cand[2]
                since = 0; gap = rng.choice([3, 4, 5])
    seglist = []; T = [0.0]
    def ease(q): return f'(0.5-0.5*cos(PI*{q}))'
    jobs = []
    for n, item in enumerate(plan):
        if item[0] == 'clip':
            _, w, i, f = item; cw, ch, dur, has_a = probe(f); D = min(FEAT, dur)
            c, r = i % COLS, i // COLS; asp = cw / ch
            h0 = TH; w0 = h0 * asp; x0 = c * TW - 2 + (TW - w0) / 2; y0 = r * TH
            H1 = 1000; W1 = H1 * asp
            if W1 > 1500: W1 = 1500; H1 = W1 / asp
            X1 = (1920 - W1) / 2; Y1 = (1080 - H1) / 2
            pe = f'if(lt(t,{AIN}),{ease(f"t/{AIN}")},if(lt(t,{D - AIN}),1,{ease(f"({D}-t)/{AIN}")}))'
            lerp = lambda a, b: f'({a}+({b}-{a})*{pe})'
            off = T[0] % WALLLEN; out = f'{O}/seg-{n:03d}.mp4'
            aud = f"[1:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=in:st=0:d=0.3,afade=t=out:st={max(0, D - 0.5)}:d=0.5[a]" if has_a else f"anullsrc=r=48000:cl=stereo,atrim=0:{D}[a]"
            fc = (f"[0:v]eq=brightness=-0.08[bg];[1:v]format=rgba,scale=w='{lerp(w0, W1)}':h='{lerp(h0, H1)}':eval=frame[fg];"
                  f"[bg][fg]overlay=x='{lerp(x0, X1)}':y='{lerp(y0, Y1)}':format=auto,format=yuv420p,fps=30[v];{aud}")
            jobs.append((out, ['ffmpeg', '-v', 'error', '-y', '-stream_loop', '-1', '-ss', f'{off:.3f}', '-i', f'{O}/wall-{w}.mp4', '-i', f, '-t', f'{D:.3f}', '-filter_complex', fc,
                               '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-shortest', out]))
            T[0] += D
        else:
            f = item[1]; out = f'{O}/seg-{n:03d}.mp4'; _, _, pd, has_a = probe(f)
            vf = f'scale=1920:1080,fps=30,setsar=1,format=yuv420p,fade=t=in:st=0:d=0.4,fade=t=out:st={max(0, pd - 0.4):.2f}:d=0.4'
            if has_a: cmd = ['ffmpeg', '-v', 'error', '-y', '-i', f, '-vf', vf, '-af', 'aresample=48000,aformat=channel_layouts=stereo', '-map', '0:v', '-map', '0:a']
            else: cmd = ['ffmpeg', '-v', 'error', '-y', '-i', f, '-stream_loop', '-1', '-i', MUSIC, '-t', f'{pd:.3f}', '-vf', vf, '-af', f'volume=0.5,aresample=48000,aformat=channel_layouts=stereo,afade=t=out:st={max(0, pd - 1):.2f}:d=1', '-map', '0:v', '-map', '1:a']
            jobs.append((out, cmd + ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-shortest', out]))
            T[0] += pd
        seglist.append(out)
    with open(f'{O}/plan.txt', 'w') as fh:
        for item in plan: fh.write(' '.join(map(str, item)) + '\n')
    def do(job):
        out, cmd = job
        if not os.path.exists(out): run(cmd)
    with ThreadPoolExecutor(4) as ex: list(ex.map(do, jobs))
    with open(f'{O}/list.txt', 'w') as fh:
        for s in seglist: fh.write(f"file '{s}'\n")
    final = f'{S}/wall2/fitb-wall-loop.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{O}/list.txt', '-c', 'copy', '-movflags', '+faststart', final])
    print('total', round(T[0] / 60, 1), 'minutes;', len(plan), 'segments;', sum(1 for p in plan if p[0] == 'promo'), 'promos')
print('STAGE DONE', stage)
