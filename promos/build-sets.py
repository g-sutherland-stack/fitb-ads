#!/usr/bin/env python3
"""Four more promo sets, one per uploaded style, five themes each, 24 s, voice-over + music.

  pixel    the portrait pixel-letter promo letterboxed on blurred sides (weight_loss_guesswork_original)
  dark     the dark green centred headline, gold pill, receipt card, logo lockup (weight_loss_guesswork_landscape)
  blobs    the olive / mustard / cream organic shapes with the serif headline (weight_loss_guesswork_original_2)
  kinetic  the word-by-word gold title and the white photo card (weight_loss_guesswork_alt)

Timing is shared so one voice-over fits every style:  0-5 hook · 5-12 feature · 12-18 points · 18-24 close.
"""
import glob, math, subprocess, sys, wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, str(Path(__file__).parent))
from make_promos import (S, A, U, MUSIC, W, H, FPS, SAGE, GREEN, INK, DARK, DARK2, GOLD, WHITE, LOGO, ICON,
                         inter, pix, ease, clamp01, shot_by_prefix, phone, shadowed, big_word, wordmark, pixel_text, dark_bg, icon_card_img)

OUT = S / 'sets'; OUT.mkdir(exist_ok=True)
VO = S / 'vo'; VO.mkdir(exist_ok=True)
SERIF = '/usr/share/fonts/truetype/crosextra/Caladea-{}.ttf'
def serif(w, size): return ImageFont.truetype(SERIF.format(w), size)
OLIVE = (90, 110, 48); OLIVE_DARK = (58, 72, 30); SAGE2 = (122, 150, 72); MUSTARD = (150, 128, 20); CREAM = (240, 232, 190); CREAM2 = (247, 242, 212)
TOTAL = 24.0; T1, T2, T3 = 5.0, 12.0, 18.0

THEMES = [
    dict(key='tracking', big2='LOGGED', head=['Tracking,', 'minus the', 'hassle.'], gold='hassle.', big='TRACK', serif_head='Tracking,\nminus the hassle', serif_two='Snap it.\nLogged.',
         caption='LOG A MEAL\nFROM ONE PHOTO', card='Snap it.\nLogged.', feature='Snap your meal. Logged.', sub='One photo. Calories, protein, water, counted.',
         points=['Calories and protein from one photo', 'Water, steps, sleep and workouts', 'Your day score, 0 to 100'],
         receipt=dict(title='Lunch, from a photo', subtitle='Chicken and avocado salad', rows=[('Calories', '520 kcal'), ('Protein', '38 g'), ('Water today', '1.2 L')],
                      note='Barcode scanning included. No premium tier, no trial.', button='Log My First Meal Free'),
         shots=['0bd33d40', 'fa4f4d1d', '6ac5ae12'],
         vo=['Tracking, minus the hassle.', 'Log a meal from one photo. FitB works out the calories and protein.',
             'Water, steps, sleep and workouts, all in one place, with a day score you can win.', 'Free. No paywall, no trial. Download FitB today.']),
    dict(key='trainers', big2='BOOKED', head=['A trainer,', 'minus the', 'guesswork.'], gold='guesswork.', big='TRAINER', serif_head='A trainer,\nminus the guesswork', serif_two='Real coaches.\nReal bookings.',
         caption='FIND A TRAINER\nAT YOUR LEVEL', card='Real coaches.\nReal bookings.', feature='Find a trainer. Booked.', sub='Verified. Prices up front. Pay in the app.',
         points=['Verified trainers near you', 'Prices and availability up front', 'Book and pay in the app'],
         receipt=dict(title='Trainer near you', subtitle='Maribel, strength coach, 1.2 miles', rows=[('Session', '£35'), ('Next slot', 'Tue 18:00'), ('Rating', '4.9')],
                      note='Verified trainer. Book and pay in the app.', button='Book A Session'),
         shots=['99adf839', 'f870b486', '8643bee3'],
         vo=['A trainer, minus the guesswork.', 'Find a verified personal trainer near you, at your level.',
             'See prices and availability up front, then book and pay in the app.', 'Free to join. Download FitB today.']),
    dict(key='gym', big2='CLASSES', head=['Your gym,', 'minus the', 'queue.'], gold='queue.', big='GYM', serif_head='Your gym,\nminus the queue', serif_two='Find a gym.\nFill your week.',
         caption='CLASSES YOU CAN\nBOOK IN A TAP', card='Find a gym.\nFill your week.', feature='Pick a class. Reserved.', sub='Live timetables. One tap. Trainers at every gym.',
         points=['Gyms by town with live timetables', 'Reserve a class in one tap', 'Trainers at every gym'],
         receipt=dict(title='Group Fitness Class', subtitle="Tom's Health & Fitness, 07:00", rows=[('Spots left', '6'), ('Price', '£8'), ('Trainer', 'Kaleigh')],
                      note='Live timetable. Reserve in one tap.', button='Reserve A Spot'),
         shots=['ddf6a2a5', 'd1b71f80', '9f37e178'],
         vo=['Your gym, minus the queue.', 'Gyms by town, with live timetables.',
             'Reserve a class in one tap, and meet the trainers at every gym.', 'Free to join. Download FitB today.']),
    dict(key='recovery', big2='REST', head=['Recovery,', 'minus the', 'burnout.'], gold='burnout.', big='RECOVER', serif_head='Recovery,\nminus the burnout', serif_two='Rest is part\nof the plan.',
         caption='SLEEP, WATER\nAND REST, TRACKED', card='Rest is part\nof the plan.', feature='Sleep, water, rest. Tracked.', sub='See how recovered you really are.',
         points=['Sleep and recovery check-ins', 'Meditations and mobility', 'Rest days that count'],
         receipt=dict(title='Recovery check-in', subtitle='Last night', rows=[('Sleep', '7 h 20'), ('Recovery', '72%'), ('Water', '1.8 L')],
                      note='Rest days count. Meditations included.', button="Log Tonight's Sleep"),
         shots=['fde66f60', '9756f970', '5a90a4c4'],
         vo=['Recovery, minus the burnout.', 'Log your sleep, water and rest, and see how recovered you really are.',
             'Meditations, mobility and rest days that count towards your plan.', 'Free. No paywall, no trial. Download FitB today.']),
    dict(key='weight-loss', big2='TREND', head=['Weight loss,', 'minus the', 'guesswork.'], gold='guesswork.', big='WEIGHT', serif_head='Weight loss,\nminus the guesswork', serif_two='Trend,\nnot one number.',
         caption='THE SCALE IS\nNOT THE SCORE', card='Trend,\nnot one number.', feature='Weigh in weekly. Trend, not a verdict.', sub='A weekly review moves your target in safe steps.',
         points=['Weigh in weekly, see the trend', 'A weekly review adjusts your target', 'A buddy who checks in'],
         receipt=dict(title='Weekly review', subtitle='Weigh-in day', rows=[('Trend', '-0.4 kg'), ('Days logged', '6 of 7'), ('Target', '1,850 kcal')],
                      note='The scale is not the score.', button='Start My Week Free'),
         shots=['0bd33d40', 'ef8ffbfc', 'ee64cb03'],
         vo=['Weight loss, minus the guesswork.', 'Weigh in once a week and see your trend, not one number.',
             'A weekly review adjusts your calorie target, and a buddy checks in, so you never do it alone.', 'Free. No paywall, no trial. Download FitB today.']),
]

# ---------------- voice-over ----------------
_voice = None
def voice():
    global _voice
    if _voice is None:
        from piper import PiperVoice
        _voice = PiperVoice.load(glob.glob(str(S / 'voices' / '**' / 'en-gb-southern_english_female-low.onnx'), recursive=True)[0])
    return _voice

def vo_track(t):
    """Four chunks at 0 / 5 / 12 / 18 s over the music bed; returns the mixed wav path."""
    out = VO / f"{t['key']}.wav"
    if out.exists(): return out
    parts = []
    for i, line in enumerate(t['vo']):
        p = VO / f"{t['key']}-{i}.wav"
        with wave.open(str(p), 'wb') as w: voice().synthesize_wav(line, w)
        parts.append(p)
    starts = [0.3, T1 + 0.3, T2 + 0.3, T3 + 0.3]
    cmd = ['ffmpeg', '-v', 'error', '-y', '-i', str(MUSIC)]
    for p in parts: cmd += ['-i', str(p)]
    fc = f'[0:a]volume=0.16,atrim=0:{TOTAL},afade=t=out:st={TOTAL-1.5}:d=1.5[m];'
    for i, st in enumerate(starts):
        fc += f'[{i+1}:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.6,adelay={int(st*1000)}|{int(st*1000)}[v{i}];'
    fc += '[m]' + ''.join(f'[v{i}]' for i in range(4)) + f'amix=inputs=5:duration=first:normalize=0,alimiter=limit=0.95[a]'
    subprocess.run(cmd + ['-filter_complex', fc, '-map', '[a]', '-ar', '48000', str(out)], check=True)
    return out

# ---------------- shared bits ----------------
def fade_layer(fr, layer, a):
    if a <= 0: return
    if a < 1: layer.putalpha(layer.split()[3].point(lambda v: int(v * a)))
    fr.alpha_composite(layer)

def text_layer(txt, font, colour, x, y, a=1.0):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((x, y), txt, font=font, fill=colour + (int(255 * a),))
    return layer

def centred(fr, txt, font, colour, y, a=1.0):
    tw = font.getlength(txt); fr.alpha_composite(text_layer(txt, font, colour, (W - tw) / 2, y, a))

def receipt_card(r, scale=1.0):
    """The white 'receipt' card from the dark promo: title, subtitle, three rows, note, green button."""
    cw, ch = 690, 640
    c = Image.new('RGBA', (cw, ch), (255, 255, 255, 255)); d = ImageDraw.Draw(c)
    d.text((34, 34), r['title'], font=inter('SemiBold', 30), fill=(30, 30, 30))
    d.rounded_rectangle([cw - 150, 36, cw - 34, 72], radius=6, outline=(205, 205, 200), width=2)
    d.text((cw - 136, 44), 'EXAMPLE', font=inter('Medium', 17), fill=(110, 110, 105))
    d.text((34, 84), r['subtitle'], font=inter('Regular', 24), fill=(120, 120, 115))
    y = 140
    for label, val in r['rows']:
        d.rounded_rectangle([34, y, cw - 34, y + 70], radius=10, fill=(243, 244, 240))
        d.ellipse([54, y + 27, 70, y + 43], fill=GREEN)
        d.text((88, y + 20), label, font=inter('Medium', 26), fill=(40, 40, 40))
        d.text((cw - 50 - inter('SemiBold', 24).getlength(val), y + 22), val, font=inter('SemiBold', 24), fill=(30, 30, 30))
        y += 84
    d.rounded_rectangle([34, y, cw - 34, y + 84], radius=10, fill=(243, 244, 240), outline=(220, 222, 215))
    d.text((56, y + 28), r['note'], font=inter('Regular', 22), fill=(70, 70, 65))
    y += 104
    d.rounded_rectangle([34, y, cw - 34, y + 60], radius=8, fill=(84, 112, 44))
    bt = inter('SemiBold', 26); d.text(((cw - bt.getlength(r['button'])) / 2, y + 14), r['button'], font=bt, fill=WHITE)
    mask = Image.new('L', (cw, ch), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=22, fill=255)
    out = Image.new('RGBA', (cw, ch), (0, 0, 0, 0)); out.paste(c, (0, 0), mask)
    if scale != 1.0: out = out.resize((int(cw * scale), int(ch * scale)), Image.LANCZOS)
    return shadowed(out, alpha=120)

def photo_card(shot):
    """White card: soft sage kitchen-ish backdrop, FitB wordmark, a tilted phone with the app screen."""
    cw, ch = 920, 560
    bg = Image.new('RGBA', (cw, ch), (236, 238, 230, 255))
    g = Image.new('RGBA', (cw, ch), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    gd.ellipse([cw * 0.55, -ch * 0.2, cw * 1.3, ch * 0.9], fill=(190, 204, 160, 255))
    gd.ellipse([-cw * 0.2, ch * 0.5, cw * 0.5, ch * 1.3], fill=(220, 226, 205, 255))
    g = g.filter(ImageFilter.GaussianBlur(70)); bg.alpha_composite(g)
    lg = LOGO.resize((round(LOGO.width * 56 / LOGO.height), 56), Image.LANCZOS); bg.alpha_composite(lg, (36, 32))
    ph = phone(shot, 470).rotate(-8, expand=True, resample=Image.BICUBIC)
    bg.alpha_composite(shadowed(ph, blur=22, alpha=120), (cw // 2 - 60, 30))
    mask = Image.new('L', (cw, ch), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=26, fill=255)
    out = Image.new('RGBA', (cw, ch), (0, 0, 0, 0)); out.paste(bg, (0, 0), mask)
    return shadowed(out, alpha=130)

def blob(size, colour, seed=1, spikes=0, wobble=0.12):
    """Organic blob (or a starburst when spikes > 0) as an RGBA image."""
    import random
    rnd = random.Random(seed); w, h = size
    pts = []; n = 180
    phases = [rnd.random() * 6.28 for _ in range(4)]
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 1 + wobble * (math.sin(2 * a + phases[0]) * 0.6 + math.sin(3 * a + phases[1]) * 0.4 + math.sin(5 * a + phases[2]) * 0.25)
        if spikes: r *= 1 + 0.12 * math.cos(spikes * a)
        pts.append((w / 2 + math.cos(a) * r * w / 2 * 0.86, h / 2 + math.sin(a) * r * h / 2 * 0.86))
    im = Image.new('RGBA', size, (0, 0, 0, 0)); ImageDraw.Draw(im).polygon(pts, fill=colour + (255,))
    return im

# ---------------- style: pixel (portrait, blurred sides) ----------------
PW, PH = 1080, 1920
def pixel_portrait(t, tt, big, card, icon, wm):
    fr = Image.new('RGBA', (PW, PH), SAGE + (255,))
    if tt < T2:
        x = PW + 40 - (PW + big.width + 80) * (tt / T2)
        fr.alpha_composite(big, (int(x), 300))
        n = int(clamp01((tt - 0.2) / 1.4) * len(t['caption']))
        if t['caption'][:n].strip(): fr.alpha_composite(pixel_text(t['caption'][:n], 64, INK), (80, 160))
        if tt > T1:
            a = ease((tt - T1) / 0.7); layer = Image.new('RGBA', (PW, PH), (0, 0, 0, 0))
            layer.alpha_composite(card, ((PW - card.width) // 2, 560 + int((1 - a) * 90))); fade_layer(fr, layer, a)
    elif tt < T3:
        x = -big.width * 0.3 - (tt - T2) / (T3 - T2) * big.width * 0.3
        soft = big.copy(); soft.putalpha(soft.split()[3].point(lambda v: v * 45 // 100)); fr.alpha_composite(soft, (int(x), 1100))
        fr.alpha_composite(pixel_text(t['big'], 52, INK), (80, 160))
        for i, pt in enumerate(t['points']):
            pa = ease((tt - T2 - 0.2 - i * 1.6) / 0.5)
            if pa <= 0: continue
            fr.alpha_composite(pixel_text('> ' + pt.upper(), 40, INK), (80, 330 + i * 150))
        a = ease((tt - T2) / 0.5); layer = Image.new('RGBA', (PW, PH), (0, 0, 0, 0))
        layer.alpha_composite(card, ((PW - card.width) // 2, 860)); fade_layer(fr, layer, a)
    else:
        a = ease((tt - T3) / 0.6); layer = Image.new('RGBA', (PW, PH), (0, 0, 0, 0))
        layer.alpha_composite(icon, ((PW - icon.width) // 2, 640 + int((1 - a) * 60))); fade_layer(fr, layer, a)
        b = ease((tt - T3 - 0.6) / 0.5)
        if b > 0:
            l1 = pixel_text('FREE. NO PAYWALL.', 56, INK); l2 = pixel_text('FITB.SOCIAL', 48, GREEN)
            la = Image.new('RGBA', (PW, PH), (0, 0, 0, 0)); la.alpha_composite(l1, ((PW - l1.width) // 2, 1080)); la.alpha_composite(l2, ((PW - l2.width) // 2, 1170)); fade_layer(fr, la, b)
    fr.alpha_composite(wm, (PW - wm.width - 70, 70))
    # letterbox: blurred fill behind the portrait frame
    small = fr.resize((480, 270), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BICUBIC)
    port = fr.resize((608, 1080), Image.LANCZOS)
    small.alpha_composite(port, ((W - 608) // 2, 0))
    return small

# ---------------- style: dark centred + receipt ----------------
def dark_centred(t, tt, bg, card, icon):
    fr = bg.copy(); f = inter('Bold', 92); fp = inter('Bold', 72)
    if tt < T1:
        a = ease(tt / 0.5)
        centred(fr, t['head'][0] + ' ' + t['head'][1], f, WHITE, 300 + int((1 - a) * 30), a)
        centred(fr, t['head'][2], f, WHITE, 410 + int((1 - a) * 30), a)
        b = ease((tt - 0.9) / 0.4)
        if b > 0:
            txt = "And it's FREE."; tw = fp.getlength(txt); sc = 0.6 + 0.4 * b
            pw, ph_ = int((tw + 70) * sc), int(110 * sc)
            layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
            d.rounded_rectangle([(W - pw) / 2, 600 - ph_ / 2, (W + pw) / 2, 600 + ph_ / 2], radius=14, fill=GOLD + (int(255 * b),))
            fr.alpha_composite(layer)
            if b > 0.85: centred(fr, txt, fp, DARK2, 600 - 44)
    elif tt < T3:
        a = ease((tt - T1) / 0.6); sc = 0.9 + 0.1 * a
        c = card if sc == 1 else card.resize((int(card.width * sc), int(card.height * sc)), Image.LANCZOS)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(c, ((W - c.width) // 2, 40 + int((1 - a) * 40))); fade_layer(fr, layer, a)
        b = ease((tt - T1 - 0.5) / 0.5)
        if b > 0:
            centred(fr, t['feature'], inter('Bold', 76), WHITE, 800, b)
            centred(fr, t['sub'], inter('Medium', 40), GOLD, 900, b)
        if tt > T2:
            # points slide in under the sub line
            for i, pt in enumerate(t['points']):
                pa = ease((tt - T2 - i * 1.5) / 0.5)
                if pa <= 0: continue
                centred(fr, '·  ' + pt + '  ·', inter('Medium', 34), WHITE, 960 + int((1 - pa) * 20), pa)
                break  # one at a time, the latest replaces the previous
    else:
        a = ease((tt - T3) / 0.6)
        lock = Image.new('RGBA', (560, 160), (0, 0, 0, 0))
        ic = ICON.resize((140, round(140 * ICON.height / ICON.width)), Image.LANCZOS)
        card_ic = Image.new('RGBA', (160, 160), (0, 0, 0, 0)); ImageDraw.Draw(card_ic).rounded_rectangle([0, 0, 159, 159], radius=34, fill=(66, 84, 48, 255))
        card_ic.alpha_composite(ic, (10, 10)); lock.alpha_composite(card_ic, (0, 0))
        ImageDraw.Draw(lock).text((190, 20), 'FitB', font=inter('Bold', 110), fill=WHITE)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(lock, ((W - lock.width) // 2 + 60, 380 + int((1 - a) * 30))); fade_layer(fr, layer, a)
        b = ease((tt - T3 - 0.5) / 0.5)
        if b > 0:
            centred(fr, ' '.join(t['head']), inter('SemiBold', 52), WHITE, 600, b)
            centred(fr, 'Free on iPhone and Android.', inter('SemiBold', 46), GOLD, 680, b)
    return fr

# ---------------- style: blobs + serif ----------------
def blobs_style(t, tt, pcard, icon_small, star, blob_m, blob_c, cloud):
    fs = serif('Bold', 120)
    if tt < T1:
        fr = Image.new('RGBA', (W, H), OLIVE + (255,))
        a = ease(tt / 0.6); sc = 0.7 + 0.3 * a
        st = star.resize((int(star.width * sc), int(star.height * sc)), Image.LANCZOS)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(st, ((W - st.width) // 2, (H - st.height) // 2)); fade_layer(fr, layer, a)
        b = ease((tt - 0.4) / 0.5)
        if b > 0:
            lines = t['serif_head'].split('\n')
            for i, l in enumerate(lines): centred(fr, l, fs, CREAM2, (H - 140 * len(lines)) // 2 + i * 140, b)
    elif tt < T3:
        fr = Image.new('RGBA', (W, H), OLIVE_DARK + (255,))
        a = ease((tt - T1) / 0.7)
        bl = blob_m.resize((int(blob_m.width * (0.8 + 0.2 * a)), int(blob_m.height * (0.8 + 0.2 * a))), Image.LANCZOS)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(bl, (W - bl.width + 120, H - bl.height + 160)); fade_layer(fr, layer, a)
        b = ease((tt - T1 - 0.3) / 0.6)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(pcard, (W - pcard.width - 60 + int((1 - b) * 60), 120)); fade_layer(fr, layer, b)
        if tt > T2:
            for i, pt in enumerate(t['points']):
                pa = ease((tt - T2 - i * 1.6) / 0.5)
                if pa <= 0: continue
                fr.alpha_composite(text_layer(pt, serif('Bold', 42), CREAM2, 100, 340 + i * 110, pa))
        else:
            c = ease((tt - T1 - 0.8) / 0.5)
            if c > 0:
                for i, l in enumerate(t['serif_two'].split('\n')): fr.alpha_composite(text_layer(l, serif('Bold', 96), CREAM2, 120, 330 + i * 115, c))
    else:
        fr = Image.new('RGBA', (W, H), CREAM + (255,))
        a = ease((tt - T3) / 0.7)
        cl = cloud.resize((int(cloud.width * (0.85 + 0.15 * a)), int(cloud.height * (0.85 + 0.15 * a))), Image.LANCZOS)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(cl, ((W - cl.width) // 2, (H - cl.height) // 2 + 40)); fade_layer(fr, layer, a)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(icon_small, ((W - icon_small.width) // 2, 560)); fade_layer(fr, layer, a)
        b = ease((tt - T3 - 0.5) / 0.5)
        if b > 0:
            centred(fr, 'FitB', serif('Bold', 140), MUSTARD, 300, b)
            centred(fr, 'Free. No paywall, no trial.  ·  fitb.social', serif('Bold', 48), OLIVE_DARK, 820, b)
    return fr

# ---------------- style: kinetic + photo card ----------------
def kinetic_style(t, tt, bg, pcard, icon):
    fr = bg.copy(); f = inter('Bold', 150)
    if tt < T2:
        shift = ease((tt - T1) / 0.8) if tt > T1 else 0.0
        lines = t['head']; lh = 165; y0 = (H - lh * 3) // 2 - 20
        for i, line in enumerate(lines):
            a = ease((tt - 0.35 * i - 0.2) / 0.45)
            if a <= 0: continue
            colour = GOLD if line == t['gold'] else WHITE
            font = f if shift == 0 else ImageFont.truetype(f.path, int(150 - 60 * shift))
            tw = font.getlength(line); xc = (W - tw) / 2 * (1 - shift) + 110 * shift
            y = (y0 + i * lh + (1 - a) * 40) * (1 - shift) + (280 + i * 110) * shift
            fr.alpha_composite(text_layer(line, font, colour, xc, y, a))
            if line == t['gold'] and shift == 0:
                u = ease((tt - 0.35 * i - 0.9) / 0.5)
                if u > 0: ImageDraw.Draw(fr).rectangle([xc, y + 158, xc + tw * u, y + 168], fill=GOLD)
        if shift > 0:
            layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(pcard, (W - pcard.width - 80 + int((1 - shift) * 200), (H - pcard.height) // 2)); fade_layer(fr, layer, shift)
    elif tt < T3:
        for i, line in enumerate(t['head']):
            fr.alpha_composite(text_layer(line, inter('Bold', 90), GOLD if line == t['gold'] else WHITE, 110, 280 + i * 110))
        fr.alpha_composite(pcard, (W - pcard.width - 80, (H - pcard.height) // 2))
        for i, pt in enumerate(t['points']):
            pa = ease((tt - T2 - i * 1.6) / 0.5)
            if pa <= 0: continue
            fr.alpha_composite(text_layer('— ' + pt, inter('Medium', 40), WHITE, 110, 660 + i * 70, pa))
    else:
        a = ease((tt - T3) / 0.6)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(icon, ((W - icon.width) // 2, 180 + int((1 - a) * 40))); fade_layer(fr, layer, a)
        for i, (txt, font, colour) in enumerate([('Free. No paywall, no trial.', inter('Bold', 92), WHITE), ('fitb.social', inter('Medium', 54), GOLD)]):
            la = ease((tt - T3 - 0.6 - i * 0.5) / 0.5)
            if la > 0: centred(fr, txt, font, colour, 600 + i * 120 + int((1 - la) * 30), la)
    return fr

# ---------------- style: plans (true landscape pixel page, from plans_built_around_your_goal) ----------------
def plans_style(t, tt, big, big2, card, pcard, icon, wm):
    fr = Image.new('RGBA', (W, H), SAGE + (255,))
    if tt < T1:
        # the giant word crosses the whole page, letters bleeding off top and bottom
        x = W + 40 - (W + big.width + 80) * (tt / T1)
        fr.alpha_composite(big, (int(x), (H - big.height) // 2))
    elif tt < T2:
        x = W * 0.1 - (tt - T1) / (T2 - T1) * big2.width * 0.45
        fr.alpha_composite(big2, (int(x), H - big2.height + 200))
        a = ease((tt - T1) / 0.7)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(card, ((W - card.width) // 2, (H - card.height) // 2 + int((1 - a) * 80))); fade_layer(fr, layer, a)
    elif tt < T3:
        x = -big.width * 0.35 - (tt - T2) / (T3 - T2) * big.width * 0.25
        soft = big.copy(); soft.putalpha(soft.split()[3].point(lambda v: v * 55 // 100)); fr.alpha_composite(soft, (int(x), H - big.height + 260))
        n = int(clamp01((tt - T2 - 0.1) / 1.2) * len(t['caption']))
        if t['caption'][:n].strip(): fr.alpha_composite(pixel_text(t['caption'][:n], 60, INK), (130, 190))
        for i, pt in enumerate(t['points']):
            pa = ease((tt - T2 - 1.6 - i * 1.3) / 0.4)
            if pa <= 0: continue
            fr.alpha_composite(pixel_text('> ' + pt.upper(), 30, INK), (130, 420 + i * 70))
        a = ease((tt - T2) / 0.7)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(pcard, (W - pcard.width - 60 + int((1 - a) * 120), (H - pcard.height) // 2 + 20)); fade_layer(fr, layer, a)
    else:
        a = ease((tt - T3) / 0.6)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(icon, ((W - icon.width) // 2, 230 + int((1 - a) * 50))); fade_layer(fr, layer, a)
        b = ease((tt - T3 - 0.6) / 0.5)
        if b > 0:
            l1 = pixel_text('FREE. NO PAYWALL, NO TRIAL.', 52, INK); l2 = pixel_text('FITB.SOCIAL', 44, GREEN)
            la = Image.new('RGBA', (W, H), (0, 0, 0, 0)); la.alpha_composite(l1, ((W - l1.width) // 2, 720)); la.alpha_composite(l2, ((W - l2.width) // 2, 800)); fade_layer(fr, la, b)
    fr.alpha_composite(wm, (W - wm.width - 110, 90))
    return fr

# ---------------- render ----------------
def render(style, t):
    shots = [shot_by_prefix(s) for s in t['shots']]
    out = OUT / f"fitb-{style}-{t['key']}-24s.mp4"
    audio = vo_track(t)
    assets = {}
    if style == 'pixel':
        from make_promos import card_dark
        assets = dict(big=big_word(t['big']), card=card_dark(t, shots[0]), icon=icon_card_img(), wm=wordmark(INK))
    elif style == 'dark':
        assets = dict(bg=dark_bg(), card=receipt_card(t['receipt']), icon=icon_card_img())
    elif style == 'blobs':
        ic = Image.new('RGBA', (150, 150), (255, 255, 255, 255)); i2 = ICON.resize((100, round(100 * ICON.height / ICON.width)), Image.LANCZOS)
        ic.alpha_composite(i2, (25, 25)); m = Image.new('L', (150, 150), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, 149, 149], radius=24, fill=255)
        icon_small = Image.new('RGBA', (150, 150), (0, 0, 0, 0)); icon_small.paste(ic, (0, 0), m)
        assets = dict(pcard=photo_card(shots[0]), icon_small=shadowed(icon_small, alpha=90), star=blob((1000, 1000), SAGE2, seed=3, spikes=10, wobble=0.05),
                      blob_m=blob((1500, 1300), MUSTARD, seed=5, wobble=0.16), blob_c=blob((900, 700), CREAM, seed=7), cloud=blob((1150, 820), CREAM2, seed=9, wobble=0.14))
    elif style == 'kinetic':
        assets = dict(bg=dark_bg(), pcard=photo_card(shots[0]), icon=icon_card_img())
    elif style == 'plans':
        from make_promos import card_dark
        assets = dict(big=big_word(t['big']), big2=big_word(t['big2']), card=card_dark(t, shots[0]), pcard=photo_card(shots[1]), icon=icon_card_img(), wm=wordmark(INK))
    n = int(TOTAL * FPS)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', str(audio),
           '-map', '0:v', '-map', '1:a', '-t', str(TOTAL), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        tt = i / FPS
        if style == 'pixel': fr = pixel_portrait(t, tt, **assets)
        elif style == 'dark': fr = dark_centred(t, tt, **assets)
        elif style == 'blobs': fr = blobs_style(t, tt, **assets)
        elif style == 'plans': fr = plans_style(t, tt, **assets)
        else: fr = kinetic_style(t, tt, **assets)
        # a quick dip at each section change
        for cut in (T1, T2, T3):
            dt = abs(tt - cut)
            if dt < 0.18: fr = Image.blend(fr, Image.new('RGBA', (W, H), (20, 24, 14, 255)), (1 - dt / 0.18) * 0.7)
        proc.stdin.write(fr.convert('RGB').tobytes())
    proc.stdin.close(); proc.wait(); print('wrote', out.name)

if __name__ == '__main__':
    styles = sys.argv[1].split(',') if len(sys.argv) > 1 else ['plans', 'pixel', 'dark', 'blobs', 'kinetic']
    keys = sys.argv[2].split(',') if len(sys.argv) > 2 else [t['key'] for t in THEMES]
    for style in styles:
        for t in THEMES:
            if t['key'] in keys: render(style, t)
