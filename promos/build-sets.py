#!/usr/bin/env python3
"""Five promo sets, one per reference style, five themes each, 24 s, no two videos laid out the same.

Every video is built from the same timing (0-5 hook, 5-12 feature, 12-18 points, 18-24 close) but each
theme takes a different route through its style: letters run the other way, the phone scrolls the app
or plays a real member clip, three phones fan out, cards swap sides, colours shift, the close changes.
"""
import glob, math, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, str(Path(__file__).parent))
from make_promos import (S, A, U, W, H, FPS, SAGE, GREEN, INK, DARK, DARK2, GOLD, WHITE, LOGO, ICON,
                         inter, pix, ease, clamp01, shot_by_prefix, shadowed, big_word, wordmark, pixel_text, dark_bg, icon_card_img)
from make_sets import (THEMES, serif, receipt_card, blob, fade_layer, text_layer, centred,
                       OLIVE, OLIVE_DARK, SAGE2, MUSTARD, CREAM, CREAM2, TOTAL, T1, T2, T3)

OUT = S / 'sets2'; OUT.mkdir(exist_ok=True)
SW, SH = 340, 720          # phone screen size every source is rendered at
CLIPS = {'tracking': [5, 10, 40], 'trainers': [11, 4, 17], 'gym': [41, 6, 22], 'recovery': [49, 25, 2], 'weight-loss': [15, 26, 45]}
PALETTE = [  # per theme: (dark bg, accent, light bg) so the same style never wears the same colours twice
    ((46, 59, 38), GOLD, SAGE), ((38, 50, 44), (214, 196, 120), (223, 229, 220)), ((52, 58, 34), (236, 190, 40), (229, 230, 212)),
    ((40, 48, 52), (190, 206, 150), (222, 230, 226)), ((44, 56, 36), GOLD, (226, 230, 214)),
]

# ---------------- screen sources ----------------
class Screen:
    """What is on a phone screen at time t: a still, a scrolling app page, or a member clip."""
    def __init__(self, kind, src, dur=6.0):
        self.kind, self.dur = kind, dur
        if kind in ('still', 'scroll'):
            im = Image.open(src).convert('RGB'); w, h = im.size
            im = im.crop((0, int(h * 0.04), w, int(h * 0.985))); im = im.resize((SW, round(SW * im.height / im.width)), Image.LANCZOS)
            self.im = im
        else:
            self.paths = sorted(glob.glob(f'{S}/clipframes/{src:02d}/*.jpg')); self._cache = {}
    def at(self, t):
        if self.kind == 'still': return self.im.crop((0, 0, SW, SH))
        if self.kind == 'scroll':
            y = int((self.im.height - SH) * (0.5 - 0.5 * math.cos(math.pi * clamp01(t / self.dur)))); return self.im.crop((0, y, SW, y + SH))
        i = int(t * FPS) % len(self.paths)
        if i not in self._cache:
            if len(self._cache) > 40: self._cache.clear()
            self._cache[i] = Image.open(self.paths[i]).convert('RGB')
        return self._cache[i]

def phone_img(screen_im, scale=1.0):
    bez = 14; r = 50
    ph = Image.new('RGBA', (SW + 2 * bez, SH + 2 * bez), (0, 0, 0, 0))
    ImageDraw.Draw(ph).rounded_rectangle([0, 0, ph.width - 1, ph.height - 1], radius=r, fill=(24, 26, 20, 255))
    mask = Image.new('L', (SW, SH), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, SW - 1, SH - 1], radius=36, fill=255)
    ph.paste(screen_im, (bez, bez), mask)
    ImageDraw.Draw(ph).rounded_rectangle([SW // 2 - 40 + bez, bez + 10, SW // 2 + 40 + bez, bez + 30], radius=10, fill=(24, 26, 20, 255))
    if scale != 1.0: ph = ph.resize((int(ph.width * scale), int(ph.height * scale)), Image.LANCZOS)
    return ph

def fan(screens, t, scale=0.72):
    """Three phones fanned out, the middle one forward."""
    layer = Image.new('RGBA', (1100, 900), (0, 0, 0, 0))
    for i, (sc, ang, dx, dy) in enumerate(zip(screens, (-14, 0, 14), (-250, 0, 250), (60, 0, 60))):
        ph = phone_img(sc.at(t), scale).rotate(ang, expand=True, resample=Image.BICUBIC)
        layer.alpha_composite(shadowed(ph, blur=20, alpha=100), (550 - ph.width // 2 + dx - 60, 40 + dy))
    return layer

def white_card(inner, w, h, bg=(247, 248, 243), radius=16):
    c = Image.new('RGBA', (w, h), bg + (255,))
    lg = LOGO.resize((round(LOGO.width * 46 / LOGO.height), 46), Image.LANCZOS); c.alpha_composite(lg, (34, 30))
    c.alpha_composite(inner, ((w - inner.width) // 2, (h - inner.height) // 2 + 30))
    mask = Image.new('L', (w, h), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0)); out.paste(c, (0, 0), mask)
    return shadowed(out, blur=24, alpha=80)

def photo_bg(w, h, tint):
    bg = Image.new('RGBA', (w, h), (236, 238, 230, 255))
    g = Image.new('RGBA', (w, h), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    gd.ellipse([w * 0.55, -h * 0.2, w * 1.3, h * 0.9], fill=tint + (255,)); gd.ellipse([-w * 0.2, h * 0.5, w * 0.5, h * 1.3], fill=(220, 226, 205, 255))
    bg.alpha_composite(g.filter(ImageFilter.GaussianBlur(70)))
    lg = LOGO.resize((round(LOGO.width * 56 / LOGO.height), 56), Image.LANCZOS); bg.alpha_composite(lg, (36, 32))
    return bg

def photo_card(screen, t, w=920, h=560, tilt=-8, tint=(190, 204, 160)):
    bg = photo_bg(w, h, tint)
    ph = phone_img(screen.at(t), 0.62).rotate(tilt, expand=True, resample=Image.BICUBIC)
    bg.alpha_composite(shadowed(ph, blur=22, alpha=120), (w // 2 - 40, 20))
    mask = Image.new('L', (w, h), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=26, fill=255)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0)); out.paste(bg, (0, 0), mask)
    return shadowed(out, alpha=130)

def dark_card(title, screen, t, w=560, h=760, bg=DARK2):
    c = Image.new('RGBA', (w, h), bg + (255,)); d = ImageDraw.Draw(c)
    lg = LOGO.resize((round(LOGO.width * 44 / LOGO.height), 44), Image.LANCZOS); c.alpha_composite(lg, (36, 32))
    f = inter('Bold', 44); y = 110
    for line in title.split('\n'): d.text((36, y), line, font=f, fill=WHITE); y += 52
    ph = phone_img(screen.at(t), 0.66); c.alpha_composite(ph, ((w - ph.width) // 2, h - ph.height + 70))
    mask = Image.new('L', (w, h), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=28, fill=255)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0)); out.paste(c, (0, 0), mask)
    return shadowed(out)

def points_block(points, t, t0, font, colour, x, y0, gap, marker='tick', accent=GREEN, step=1.6):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for i, pt in enumerate(points):
        a = ease((t - t0 - i * step) / 0.5)
        if a <= 0: continue
        y = y0 + i * gap + int((1 - a) * 24); al = int(255 * a)
        if marker == 'tick':
            d.rounded_rectangle([x, y + 6, x + 42, y + 48], radius=10, fill=accent + (al,)); d.line([(x + 11, y + 28), (x + 20, y + 37), (x + 33, y + 17)], fill=WHITE + (al,), width=5)
            d.text((x + 64, y), pt, font=font, fill=colour + (al,))
        elif marker == 'num':
            d.text((x, y), f'0{i + 1}', font=font, fill=accent + (al,)); d.text((x + 90, y), pt, font=font, fill=colour + (al,))
        else:
            d.text((x, y), ('> ' if marker == 'pix' else '— ') + (pt.upper() if marker == 'pix' else pt), font=font, fill=colour + (al,))
    return layer

def close_scene(t, tt, variant, bg_col, fg, accent, icon):
    fr = Image.new('RGBA', (W, H), bg_col + (255,))
    a = ease(tt / 0.6)
    if variant == 0:
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(icon, ((W - icon.width) // 2, 180 + int((1 - a) * 40))); fade_layer(fr, layer, a)
        for i, (txt, font, col) in enumerate([('Free. No paywall, no trial.', inter('Bold', 92), fg), ('fitb.social', inter('Medium', 54), accent)]):
            la = ease((tt - 0.6 - i * 0.5) / 0.5)
            if la > 0: centred(fr, txt, font, col, 600 + i * 120 + int((1 - la) * 30), la)
    elif variant == 1:
        lock = Image.new('RGBA', (620, 170), (0, 0, 0, 0)); ic = ICON.resize((150, round(150 * ICON.height / ICON.width)), Image.LANCZOS)
        card = Image.new('RGBA', (170, 170), (0, 0, 0, 0)); ImageDraw.Draw(card).rounded_rectangle([0, 0, 169, 169], radius=36, fill=(255, 255, 255, 255)); card.alpha_composite(ic, (10, 10))
        lock.alpha_composite(card, (0, 0)); ImageDraw.Draw(lock).text((200, 18), 'FitB', font=inter('Bold', 120), fill=fg)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(lock, ((W - lock.width) // 2 + 40, 330 + int((1 - a) * 30))); fade_layer(fr, layer, a)
        b = ease((tt - 0.5) / 0.5)
        if b > 0:
            centred(fr, ' '.join(t['head']), inter('SemiBold', 56), fg, 560, b); centred(fr, 'Free on iPhone and Android.', inter('SemiBold', 46), accent, 650, b)
    else:
        big = big_word('FITB'); soft = big.copy(); soft.putalpha(soft.split()[3].point(lambda v: int(v * 0.9 * a)))
        fr.alpha_composite(soft, ((W - big.width) // 2, (H - big.height) // 2 - 120))
        b = ease((tt - 0.5) / 0.5)
        if b > 0:
            l1 = pixel_text('FREE. NO PAYWALL, NO TRIAL.', 56, fg); l2 = pixel_text('FITB.SOCIAL', 46, accent)
            la = Image.new('RGBA', (W, H), (0, 0, 0, 0)); la.alpha_composite(l1, ((W - l1.width) // 2, 760)); la.alpha_composite(l2, ((W - l2.width) // 2, 850)); fade_layer(fr, la, b)
    return fr

# ================= style 1: plans (landscape pixel page) =================
def plans(t, v, tt, X):
    bgc, acc, light = PALETTE[v]; fr = Image.new('RGBA', (W, H), light + (255,))
    ltr = 1 if v % 2 == 0 else -1  # letters run right-to-left on even themes, left-to-right on odd
    if tt < T1:
        p = tt / T1; x = (W + 40 - (W + X['big'].width + 80) * p) if ltr > 0 else (-X['big'].width - 40 + (W + X['big'].width + 80) * p)
        fr.alpha_composite(X['big'], (int(x), (H - X['big'].height) // 2 + (0 if v % 3 else -120)))
        if v % 3 == 2:  # some themes get the caption typed already in the hook
            n = int(clamp01((tt - 1.0) / 1.5) * len(t['caption'])); fr.alpha_composite(pixel_text(t['caption'][:n], 60, INK), (130, 760))
    elif tt < T2:
        x = W * 0.1 - (tt - T1) / 7 * X['big2'].width * 0.45; fr.alpha_composite(X['big2'], (int(x), H - X['big2'].height + 200))
        a = ease((tt - T1) / 0.7); layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        if v % 3 == 0:   # dark card, phone scrolling the app
            c = dark_card(t['card'], X['scr'][0], tt - T1); layer.alpha_composite(c, ((W - c.width) // 2, (H - c.height) // 2 + int((1 - a) * 80)))
        elif v % 3 == 1: # three phones fanned, member clip in the middle
            f3 = fan([X['scr'][1], X['clip'][0], X['scr'][2]], tt - T1); layer.alpha_composite(f3, ((W - f3.width) // 2, 80 + int((1 - a) * 80)))
        else:            # white product card with a clip playing, off to the right
            ph = phone_img(X['clip'][0].at(tt - T1), 0.8); c = white_card(ph, 560, 820); layer.alpha_composite(c, (W - c.width - 120, (H - c.height) // 2 + int((1 - a) * 80)))
            fr.alpha_composite(pixel_text(t['big'] + '\n' + t['rows'][1], 110, INK), (120, 300))
        fade_layer(fr, layer, a)
    elif tt < T3:
        x = -X['big'].width * 0.35 - (tt - T2) / 6 * X['big'].width * 0.25
        soft = X['big'].copy(); soft.putalpha(soft.split()[3].point(lambda q: q * 55 // 100)); fr.alpha_composite(soft, (int(x), H - X['big'].height + 260))
        n = int(clamp01((tt - T2 - 0.1) / 1.2) * len(t['caption']))
        side_right = v % 2 == 0
        cx = 130 if side_right else W - 820
        if t['caption'][:n].strip(): fr.alpha_composite(pixel_text(t['caption'][:n], 60, INK), (cx, 190))
        fr.alpha_composite(points_block(t['points'], tt, T2 + 1.4, pix(38), INK, cx, 420, 64, marker='pix', step=1.2))
        a = ease((tt - T2) / 0.7); layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        pc = photo_card(X['clip'][1] if v % 2 else X['scr'][1], tt - T2, tilt=-8 if v % 2 else 6, tint=acc if v % 2 else (190, 204, 160))
        px = (W - pc.width - 60 + int((1 - a) * 120)) if side_right else (60 - int((1 - a) * 120))
        layer.alpha_composite(pc, (px, (H - pc.height) // 2 + 20)); fade_layer(fr, layer, a)
    else:
        return close_scene(t, tt - T3, [2, 0, 1, 2, 0][v], light, INK, GREEN, X['icon'])
    fr.alpha_composite(X['wm'], (W - X['wm'].width - 110, 90)); return fr

# ================= style 2: pixel (video 1: portrait page on blurred sides) =================
PW, PH = 1080, 1920
def pixel(t, v, tt, X):
    bgc, acc, light = PALETTE[v]; fr = Image.new('RGBA', (PW, PH), light + (255,))
    cap = '\n'.join(l.upper() for l in t['head']); rows = X['rows']
    if tt < T1:
        d1 = 1 if v % 2 == 0 else -1
        p1, p2 = ease(tt / 4.6), ease(tt / 5.2)
        x1 = (PW + 40 - (PW + rows[0].width + 200) * p1) if d1 > 0 else (-rows[0].width + (PW + rows[0].width + 200) * p1)
        x2 = (PW + 300 - (PW + rows[1].width + 300) * p2) if d1 > 0 else (-rows[1].width - 300 + (PW + rows[1].width + 300) * p2)
        fr.alpha_composite(rows[0], (int(x1), 120)); fr.alpha_composite(rows[1], (int(x2), 1080))
        n = int(clamp01((tt - 0.8) / 1.6) * len(cap))
        if cap[:n].strip(): fr.alpha_composite(pixel_text(cap[:n], 58, INK), (120, 700 if v % 2 == 0 else 480))
    elif tt < 10.0:
        k = ease((tt - T1) / 0.6); small = pixel_text(cap, int(58 - 22 * k), INK); fr.alpha_composite(small, (int(120 - 20 * k), int(700 - 560 * k)))
        x = PW * 0.4 - (tt - T1) / 5.0 * (X['free'].width + PW); fr.alpha_composite(X['free'], (int(x), 1180))
        a = ease((tt - T1 - 0.2) / 0.6); layer = Image.new('RGBA', (PW, PH), (0, 0, 0, 0))
        src = X['clip'][0] if v % 2 else X['scr'][0]
        if v % 3 == 1: c = fan([X['scr'][1], src, X['scr'][2]], tt - T1, 0.62); layer.alpha_composite(c, ((PW - c.width) // 2, 500 + int((1 - a) * 80)))
        else: c = white_card(phone_img(src.at(tt - T1), 0.85), 620, 900); layer.alpha_composite(c, ((PW - c.width) // 2, 440 + int((1 - a) * 80)))
        fade_layer(fr, layer, a)
    elif tt < 14.0:
        z = ease((tt - 10.0) / 1.6); sc = 0.85 + 1.9 * z; src = X['clip'][0] if v % 2 else X['scr'][0]
        pb = phone_img(src.at(tt - T1), sc); fr.alpha_composite(pb, ((PW - pb.width) // 2, int(520 - z * 900)))
        x = PW * 0.4 - (tt - T1) / 5.0 * (X['free'].width + PW); fr.alpha_composite(X['free'], (int(x), 1180))
    elif tt < 19.0:
        x = -rows[1].width * 0.25 - (tt - 14.0) / 5.0 * rows[1].width * 0.35; fr.alpha_composite(rows[1], (int(x), -260))
        a = ease((tt - 14.0) / 0.6); layer = Image.new('RGBA', (PW, PH), (0, 0, 0, 0))
        pc = photo_card(X['clip'][1] if v % 2 == 0 else X['scr'][1], tt - 14, w=900, h=540, tilt=-8 if v % 2 else 7, tint=acc)
        pc = pc.resize((int(pc.width * 0.78), int(pc.height * 0.78)), Image.LANCZOS)
        layer.alpha_composite(pc, ((PW - pc.width) // 2, 560 + int((1 - a) * 60))); fade_layer(fr, layer, a)
        n = int(clamp01((tt - 14.6) / 1.4) * len(t['caption']))
        if t['caption'][:n].strip(): fr.alpha_composite(pixel_text(t['caption'][:n], 62, INK), (120, 1280))
        for i, pt in enumerate(t['points']):
            pa = ease((tt - 16.2 - i * 0.8) / 0.4)
            if pa > 0: fr.alpha_composite(pixel_text('> ' + pt.upper(), 30, INK), (120, 1480 + i * 70))
    else:
        a = ease((tt - 19.0) / 0.6); layer = Image.new('RGBA', (PW, PH), (0, 0, 0, 0))
        layer.alpha_composite(X['icon'], ((PW - X['icon'].width) // 2, 700 + int((1 - a) * 60))); fade_layer(fr, layer, a)
        b = ease((tt - 19.8) / 0.5)
        if b > 0:
            l1 = pixel_text('FREE. NO PAYWALL.', 52, INK); l2 = pixel_text('FITB.SOCIAL', 44, GREEN)
            la = Image.new('RGBA', (PW, PH), (0, 0, 0, 0)); la.alpha_composite(l1, ((PW - l1.width) // 2, 1120)); la.alpha_composite(l2, ((PW - l2.width) // 2, 1200)); fade_layer(fr, la, b)
    fr.alpha_composite(X['wm'], (PW - X['wm'].width - 70, 70))
    small = fr.resize((480, 270), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BICUBIC)
    small.alpha_composite(fr.resize((608, 1080), Image.LANCZOS), ((W - 608) // 2, 0)); return small

# ================= style 3: dark centred (receipt card) =================
def dark(t, v, tt, X):
    bgc, acc, light = PALETTE[v]; fr = X['bg'].copy(); f = inter('Bold', 92); fp = inter('Bold', 72)
    left = v % 2 == 1  # odd themes: everything left-aligned with the card on the right
    def put(txt, font, col, y, a=1.0):
        if left: fr.alpha_composite(text_layer(txt, font, col, 120, y, a))
        else: centred(fr, txt, font, col, y, a)
    if tt < T1:
        a = ease(tt / 0.5)
        put(t['head'][0] + ' ' + t['head'][1], f, WHITE, 300 + int((1 - a) * 30), a); put(t['head'][2], f, WHITE, 410 + int((1 - a) * 30), a)
        b = ease((tt - 0.9) / 0.4)
        if b > 0:
            txt = "And it's FREE."; tw = fp.getlength(txt); sc = 0.6 + 0.4 * b; pw, ph_ = int((tw + 70) * sc), int(110 * sc)
            cx = 120 + (tw + 70) / 2 if left else W / 2
            layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(layer).rounded_rectangle([cx - pw / 2, 600 - ph_ / 2, cx + pw / 2, 600 + ph_ / 2], radius=14, fill=acc + (int(255 * b),)); fr.alpha_composite(layer)
            if b > 0.85: fr.alpha_composite(text_layer(txt, fp, DARK2, cx - tw / 2, 556))
        if v % 2 == 0:  # a phone with a clip fades in behind the centred title on even themes
            c = ease((tt - 1.8) / 0.8)
            if c > 0:
                ph = phone_img(X['clip'][0].at(tt), 0.5); layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(ph, (W - ph.width - 140, 640 + int((1 - c) * 40))); fade_layer(fr, layer, c * 0.95)
    elif tt < T3:
        a = ease((tt - T1) / 0.6); card = X['card']
        if left:
            layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(card, (W - card.width - 100, (H - card.height) // 2 + int((1 - a) * 40))); fade_layer(fr, layer, a)
            b = ease((tt - T1 - 0.5) / 0.5)
            if b > 0: put(t['feature'], inter('Bold', 70), WHITE, 300, b); put(t['sub'], inter('Medium', 38), acc, 400, b)
            if tt > T2: fr.alpha_composite(points_block(t['points'], tt, T2, inter('Medium', 38), WHITE, 120, 520, 90, marker='num', accent=acc, step=1.5))
        else:
            sc = 0.9 + 0.1 * a; c = card.resize((int(card.width * sc), int(card.height * sc)), Image.LANCZOS)
            layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(c, ((W - c.width) // 2 - (220 if tt > T2 else 0), 40 + int((1 - a) * 40))); fade_layer(fr, layer, a)
            b = ease((tt - T1 - 0.5) / 0.5)
            if b > 0 and tt <= T2: centred(fr, t['feature'], inter('Bold', 76), WHITE, 800, b); centred(fr, t['sub'], inter('Medium', 40), acc, 900, b)
            if tt > T2:  # the card slides left and a clip phone joins it on the right, points under
                c2 = ease((tt - T2) / 0.6); ph = phone_img(X['clip'][1].at(tt - T2), 0.72)
                layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(shadowed(ph, blur=20, alpha=120), (W // 2 + 180 + int((1 - c2) * 200), 40)); fade_layer(fr, layer, c2)
                fr.alpha_composite(points_block(t['points'], tt, T2 + 0.4, inter('Medium', 36), WHITE, 420, 820, 70, marker='dash', accent=acc, step=1.4))
    else:
        return close_scene(t, tt - T3, [1, 0, 1, 2, 1][v], bgc, WHITE, acc, X['icon'])
    return fr

# ================= style 4: blobs (serif, organic shapes) =================
def blobs(t, v, tt, X):
    bgc, acc, light = PALETTE[v]; fs = serif('Bold', 120)
    pal = [(OLIVE, SAGE2, OLIVE_DARK, MUSTARD, CREAM), ((60, 84, 60), (120, 160, 110), (40, 60, 44), (210, 170, 60), (244, 236, 210)),
           ((96, 100, 40), (160, 170, 90), (64, 68, 28), (230, 190, 50), (238, 232, 200)), ((70, 80, 90), (140, 160, 150), (50, 60, 70), (200, 180, 90), (236, 236, 224)), (OLIVE, SAGE2, OLIVE_DARK, MUSTARD, CREAM)][v]
    c_bg, c_star, c_dark, c_must, c_cream = pal
    if tt < T1:
        fr = Image.new('RGBA', (W, H), c_bg + (255,)); a = ease(tt / 0.6); sc = 0.7 + 0.3 * a
        st = X['star'].resize((int(X['star'].width * sc), int(X['star'].height * sc)), Image.LANCZOS)
        pos = ((W - st.width) // 2, (H - st.height) // 2) if v % 2 == 0 else (W - st.width - 80, (H - st.height) // 2)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(st, pos); fade_layer(fr, layer, a)
        b = ease((tt - 0.4) / 0.5)
        if b > 0:
            lines = t['serif_head'].split('\n')
            for i, l in enumerate(lines):
                if v % 2 == 0: centred(fr, l, fs, CREAM2, (H - 140 * len(lines)) // 2 + i * 140, b)
                else: fr.alpha_composite(text_layer(l, fs, CREAM2, 120, (H - 140 * len(lines)) // 2 + i * 140, b))
    elif tt < T3:
        fr = Image.new('RGBA', (W, H), c_dark + (255,)); a = ease((tt - T1) / 0.7)
        bl = X['blob'].resize((int(X['blob'].width * (0.8 + 0.2 * a)), int(X['blob'].height * (0.8 + 0.2 * a))), Image.LANCZOS)
        right = v % 2 == 0
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(bl, (W - bl.width + 120, H - bl.height + 160) if right else (-120, H - bl.height + 160)); fade_layer(fr, layer, a)
        b = ease((tt - T1 - 0.3) / 0.6); layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        if v % 3 == 0: pc = photo_card(X['clip'][0], tt - T1, tilt=-8, tint=(220, 200, 120))
        elif v % 3 == 1: pc = fan([X['scr'][0], X['clip'][0], X['scr'][1]], tt - T1, 0.66)
        else: pc = white_card(phone_img(X['scr'][0].at(tt - T1) if tt < T2 else X['clip'][1].at(tt - T2), 0.78), 560, 760, bg=c_cream)
        layer.alpha_composite(pc, (W - pc.width - 60 + int((1 - b) * 60), (H - pc.height) // 2) if right else (60 - int((1 - b) * 60), (H - pc.height) // 2)); fade_layer(fr, layer, b)
        tx = 120 if right else W - 760
        if tt > T2: fr.alpha_composite(points_block(t['points'], tt, T2, serif('Bold', 36), CREAM2, tx, 340, 100, marker='num', accent=c_must))
        else:
            c = ease((tt - T1 - 0.8) / 0.5)
            if c > 0:
                for i, l in enumerate(t['serif_two'].split('\n')): fr.alpha_composite(text_layer(l, serif('Bold', 96), CREAM2, tx, 330 + i * 115, c))
    else:
        fr = Image.new('RGBA', (W, H), c_cream + (255,)); a = ease((tt - T3) / 0.7)
        cl = X['cloud'].resize((int(X['cloud'].width * (0.85 + 0.15 * a)), int(X['cloud'].height * (0.85 + 0.15 * a))), Image.LANCZOS)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(cl, ((W - cl.width) // 2, (H - cl.height) // 2 + 40)); fade_layer(fr, layer, a)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(X['icon_small'], ((W - X['icon_small'].width) // 2, 560)); fade_layer(fr, layer, a)
        b = ease((tt - T3 - 0.5) / 0.5)
        if b > 0:
            centred(fr, 'FitB', serif('Bold', 140), c_must, 300, b)
            centred(fr, ['Free. No paywall, no trial.', 'Free on iPhone and Android.', 'Download free today.', 'Start free, today.', 'Free. Every size welcome.'][v] + '  ·  fitb.social', serif('Bold', 48), c_dark, 820, b)
    return fr

# ================= style 5: kinetic (gold word, photo card) =================
def kinetic(t, v, tt, X):
    bgc, acc, light = PALETTE[v]; fr = X['bg'].copy(); f = inter('Bold', 150); right = v % 2 == 0
    if tt < T2:
        shift = ease((tt - T1) / 0.8) if tt > T1 else 0.0; lines = t['head']; lh = 165; y0 = (H - lh * 3) // 2 - 20
        for i, line in enumerate(lines):
            a = ease((tt - 0.35 * i - 0.2) / 0.45)
            if a <= 0: continue
            colour = acc if line == t['gold'] else WHITE
            font = f if shift == 0 else ImageFont.truetype(f.path, int(150 - 60 * shift)); tw = font.getlength(line)
            xt = 110 if right else W - 110 - tw * (1 - 0.0)
            xc = (W - tw) / 2 * (1 - shift) + xt * shift; y = (y0 + i * lh + (1 - a) * 40) * (1 - shift) + (280 + i * 110) * shift
            fr.alpha_composite(text_layer(line, font, colour, xc, y, a))
            if line == t['gold'] and shift == 0:
                u = ease((tt - 0.35 * i - 0.9) / 0.5)
                if u > 0: ImageDraw.Draw(fr).rectangle([xc, y + 158, xc + tw * u, y + 168], fill=acc)
        if shift > 0:
            layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); pc = X['pcard'](tt - T1)
            px = (W - pc.width - 80 + int((1 - shift) * 200)) if right else (80 - int((1 - shift) * 200))
            layer.alpha_composite(pc, (px, (H - pc.height) // 2)); fade_layer(fr, layer, shift)
    elif tt < T3:
        for i, line in enumerate(t['head']):
            font = inter('Bold', 90); tw = font.getlength(line)
            fr.alpha_composite(text_layer(line, font, acc if line == t['gold'] else WHITE, 110 if right else W - 110 - tw, 280 + i * 110))
        pc = X['pcard'](tt - T1); fr.alpha_composite(pc, (W - pc.width - 80, (H - pc.height) // 2) if right else (80, (H - pc.height) // 2))
        fr.alpha_composite(points_block(t['points'], tt, T2, inter('Medium', 40), WHITE, 110 if right else W - 760, 660, 70, marker='dash' if v % 2 else 'tick', accent=acc))
    else:
        return close_scene(t, tt - T3, [0, 2, 0, 1, 0][v], bgc, WHITE, acc, X['icon'])
    return fr

STYLES = {'plans': plans, 'pixel': pixel, 'dark': dark, 'blobs': blobs, 'kinetic': kinetic}

def assets(style, t, v):
    shots = [shot_by_prefix(p) for p in t['shots']]
    scr = [Screen('scroll', shots[(v + i) % 5], dur=6.0) for i in range(3)]
    clip = [Screen('clip', n) for n in CLIPS[t['key']]]
    bgc, acc, light = PALETTE[v]
    X = dict(scr=scr, clip=clip, icon=icon_card_img(), wm=wordmark(INK))
    if style in ('plans', 'pixel'):
        X.update(big=big_word(t['big']), big2=big_word(t['big2']), rows=(big_word(t['rows'][0]), big_word(t['rows'][1])), free=big_word('FREE'))
    if style in ('dark', 'kinetic'):
        bg = Image.new('RGB', (W, H), bgc); glow = Image.new('L', (W, H), 0)
        ImageDraw.Draw(glow).ellipse([W * (0.15 + 0.1 * v), -H * 0.3, W * (0.85 + 0.1 * v), H * 1.1], fill=60); glow = glow.filter(ImageFilter.GaussianBlur(220))
        X['bg'] = Image.composite(Image.new('RGB', (W, H), tuple(min(255, c + 14) for c in bgc)), bg, glow).convert('RGBA')
    if style == 'dark': X['card'] = receipt_card(t['receipt'])
    if style == 'blobs':
        ic = Image.new('RGBA', (150, 150), (255, 255, 255, 255)); i2 = ICON.resize((100, round(100 * ICON.height / ICON.width)), Image.LANCZOS); ic.alpha_composite(i2, (25, 25))
        m = Image.new('L', (150, 150), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, 149, 149], radius=24, fill=255); ism = Image.new('RGBA', (150, 150), (0, 0, 0, 0)); ism.paste(ic, (0, 0), m)
        pal = [(SAGE2, MUSTARD, CREAM2), ((120, 160, 110), (210, 170, 60), (244, 236, 210)), ((160, 170, 90), (230, 190, 50), (238, 232, 200)), ((140, 160, 150), (200, 180, 90), (236, 236, 224)), (SAGE2, MUSTARD, CREAM2)][v]
        X.update(icon_small=shadowed(ism, alpha=90), star=blob((1000, 1000), pal[0], seed=3 + v, spikes=8 + 2 * v, wobble=0.05), blob=blob((1500, 1300), pal[1], seed=5 + v, wobble=0.14 + 0.03 * v), cloud=blob((1150, 820), pal[2], seed=9 + v, wobble=0.14))
    if style == 'kinetic':
        kinds = [lambda tt: photo_card(clip[0], tt, tilt=-8, tint=acc), lambda tt: fan([scr[0], clip[0], scr[1]], tt, 0.7), lambda tt: photo_card(scr[0], tt, tilt=6, tint=acc),
                 lambda tt: white_card(phone_img(clip[1].at(tt), 0.8), 560, 780), lambda tt: dark_card(t['card'], clip[0], tt, bg=(30, 38, 26))][v]
        X['pcard'] = kinds
    return X

def render(style, t, v):
    X = assets(style, t, v); out = OUT / f"fitb-{style}-{t['key']}-24s.mp4"
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', str(S / 'music' / f'{style}.wav'),
           '-map', '0:v', '-map', '1:a', '-t', str(TOTAL), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE); fn = STYLES[style]
    for i in range(int(TOTAL * FPS)):
        tt = i / FPS; fr = fn(t, v, tt, X)
        for cut in (T1, T2, T3):
            dt = abs(tt - cut)
            if dt < 0.18: fr = Image.blend(fr, Image.new('RGBA', (W, H), (20, 24, 14, 255)), (1 - dt / 0.18) * 0.7)
        proc.stdin.write(fr.convert('RGB').tobytes())
    proc.stdin.close(); proc.wait(); print('wrote', out.name)

if __name__ == '__main__':
    styles = sys.argv[1].split(',') if len(sys.argv) > 1 else list(STYLES)
    keys = sys.argv[2].split(',') if len(sys.argv) > 2 else [t['key'] for t in THEMES]
    for style in styles:
        for v, t in enumerate(THEMES):
            if t['key'] in keys: render(style, t, v)
