#!/usr/bin/env python3
"""Five 30s FitB landscape promos in the two uploaded styles.

  0-6s   dark green, words of the headline land one by one, gold word underlined  (alt style)
  6-13s  sage page, a giant pixel word slides behind a typed pixel caption          (original style)
  13-24s sage page, dark card with a phone screen, three points light up           (original style)
  24-30s dark green close: icon card, "Free. No paywall, no trial.", fitb.social    (alt style)
"""
import math, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = Path('/tmp/claude-0/-home-user/f2431104-f768-5341-9abb-88e318700789/scratchpad/promo')
A = Path('/tmp/claude-0/-home-user-buddy-up-train/f2431104-f768-5341-9abb-88e318700789/scratchpad/ads')
U = Path('/root/.claude/uploads/f2431104-f768-5341-9abb-88e318700789')
OUT = S / 'out'; OUT.mkdir(exist_ok=True)
MUSIC = A / 'out' / 'fitb-music-30-norm.wav'
W, H, FPS = 1920, 1080, 30
SAGE = (221, 228, 213); GREEN = (123, 164, 40); INK = (30, 36, 20)
DARK = (46, 59, 38); DARK2 = (36, 47, 30); GOLD = (217, 182, 74); WHITE = (255, 255, 255)
INTER = '/usr/share/fonts/opentype/inter/InterDisplay-{}.otf'
PIX = '/usr/share/fonts/opentype/unifont/unifont.otf'
LOGO = Image.open(A / 'logo-full.png').convert('RGBA')
ICON = Image.open(A / 'logo-icon.png').convert('RGBA')

def inter(w, size): return ImageFont.truetype(INTER.format(w), size)
def pix(size): return ImageFont.truetype(PIX, size)
def ease(t): return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))
def clamp01(x): return max(0.0, min(1.0, x))

def shot_by_prefix(prefix):
    return next(p for p in U.iterdir() if p.name.startswith(prefix))

PROMOS = [
    dict(key='tracking', head=['Tracking,', 'minus the', 'hassle.'], gold='hassle.', big='TRACK',
         caption='LOG A MEAL\nFROM ONE PHOTO', card='Snap it.\nLogged.',
         points=['Calories and protein from one photo', 'Water, steps, sleep and workouts', 'Your day score, 0 to 100'],
         shots=['0bd33d40', 'fa4f4d1d', '6ac5ae12']),
    dict(key='trainers', head=['A trainer,', 'minus the', 'guesswork.'], gold='guesswork.', big='TRAINER',
         caption='FIND A TRAINER\nAT YOUR LEVEL', card='Real coaches.\nReal bookings.',
         points=['Verified trainers near you', 'Prices and availability up front', 'Book and pay in the app'],
         shots=['99adf839', 'f870b486', '8643bee3']),
    dict(key='gym', head=['Your gym,', 'minus the', 'queue.'], gold='queue.', big='GYM',
         caption='CLASSES YOU CAN\nBOOK IN A TAP', card='Find a gym.\nFill your week.',
         points=['Gyms by town with live timetables', 'Reserve a class in one tap', 'Trainers at every gym'],
         shots=['ddf6a2a5', 'd1b71f80', '9f37e178']),
    dict(key='recovery', head=['Recovery,', 'minus the', 'burnout.'], gold='burnout.', big='RECOVER',
         caption='SLEEP, WATER\nAND REST, TRACKED', card='Rest is part\nof the plan.',
         points=['Sleep and recovery check-ins', 'Meditations and mobility', 'Rest days that count'],
         shots=['fde66f60', '9756f970', '5a90a4c4']),
    dict(key='weight-loss', head=['Weight loss,', 'minus the', 'guesswork.'], gold='guesswork.', big='WEIGHT',
         caption='THE SCALE IS\nNOT THE SCORE', card='Trend,\nnot one number.',
         points=['Weigh in weekly, see the trend', 'A weekly review adjusts your target', 'A buddy who checks in'],
         shots=['0bd33d40', 'ef8ffbfc', 'ee64cb03']),
]

# ---------- assets ----------
def phone(shot_path, height):
    """A phone frame with the app screen inside (status bar and home bar cropped)."""
    im = Image.open(shot_path).convert('RGB')
    w, h = im.size
    im = im.crop((0, int(h * 0.04), w, int(h * 0.985)))
    sw = round(height * 0.47); im = im.resize((sw, round(sw * im.height / im.width)), Image.LANCZOS)
    if im.height > height - 28: im = im.crop((0, 0, sw, height - 28))
    bez = 14
    ph = Image.new('RGBA', (sw + 2 * bez, im.height + 2 * bez), (0, 0, 0, 0))
    d = ImageDraw.Draw(ph)
    d.rounded_rectangle([0, 0, ph.width - 1, ph.height - 1], radius=54, fill=(24, 26, 20, 255))
    mask = Image.new('L', im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=40, fill=255)
    ph.paste(im, (bez, bez), mask)
    return ph

def shadowed(img, blur=28, off=(0, 18), alpha=110):
    pad = blur * 3
    base = Image.new('RGBA', (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    a = img.split()[3].point(lambda v: v * alpha // 255)
    sh.paste((0, 0, 0, 255), (pad + off[0], pad + off[1]), a)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(sh); base.alpha_composite(img, (pad, pad))
    return base

def big_word(word):
    """Giant pixel letters, rendered small and scaled with nearest neighbour so the blocks stay crisp."""
    f = pix(64)
    tw = int(f.getlength(word))
    im = Image.new('RGBA', (tw + 8, 70), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4, -6), word, font=f, fill=GREEN + (255,))
    k = 17
    return im.resize((im.width * k, im.height * k), Image.NEAREST)

def wordmark(colour):
    f = pix(64)
    im = Image.new('RGBA', (320, 70), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); d.text((0, -6), 'F I T B', font=f, fill=colour + (255,))
    d.rectangle([250, 18, 282, 50], fill=colour + (255,))
    return im.resize((160, 35), Image.LANCZOS)

def pixel_text(text, size, colour, spacing=1.25):
    """Pixel mono caption rendered at 2x then scaled down for even stems."""
    f = pix(size * 2)
    lines = text.split('\n')
    lh = int(size * 2 * spacing)
    w = max(int(f.getlength(l)) for l in lines) + 8
    im = Image.new('RGBA', (w, lh * len(lines) + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines): d.text((4, i * lh - size * 0.2), l, font=f, fill=colour + (255,))
    return im.resize((im.width // 2, im.height // 2), Image.LANCZOS)

def dark_bg():
    bg = Image.new('RGB', (W, H), DARK)
    glow = Image.new('L', (W, H), 0)
    ImageDraw.Draw(glow).ellipse([W * 0.15, -H * 0.3, W * 0.85, H * 1.1], fill=60)
    glow = glow.filter(ImageFilter.GaussianBlur(220))
    bg = Image.composite(Image.new('RGB', (W, H), (58, 74, 48)), bg, glow)
    return bg.convert('RGBA')

def card_dark(p, shot):
    """The dark green card: headline with the gold word, phone below, like the uploaded promo."""
    cw, ch = 560, 760
    c = Image.new('RGBA', (cw, ch), DARK2 + (255,))
    d = ImageDraw.Draw(c)
    lg = LOGO.resize((round(LOGO.width * 44 / LOGO.height), 44), Image.LANCZOS)
    c.alpha_composite(lg, (36, 32))
    f = inter('Bold', 44); y = 110
    for line in p['card'].split('\n'):
        d.text((36, y), line, font=f, fill=WHITE); y += 52
    ph = phone(shot, 520)
    c.alpha_composite(ph, ((cw - ph.width) // 2, ch - ph.height + 70))
    mask = Image.new('L', (cw, ch), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=28, fill=255)
    out = Image.new('RGBA', (cw, ch), (0, 0, 0, 0)); out.paste(c, (0, 0), mask)
    return shadowed(out)

