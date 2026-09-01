"""
Replace Capacitor's placeholder launcher icons and splash screens with the
game's own artwork.

Run after `npx cap add android` (which regenerates the defaults):

    python mobile/make_android_assets.py
"""

import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RES = os.path.join(HERE, "android", "app", "src", "main", "res")

SRC_FULL = os.path.join(ROOT, "icons", "icon-512.png")
BG = (0x1a, 0x12, 0x30)

# ic_launcher / ic_launcher_round, then the 108dp adaptive foreground
LAUNCHER = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
FOREGROUND = {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}
SPLASH_PORT = {"mdpi": (320, 480), "hdpi": (480, 800), "xhdpi": (720, 1280),
               "xxhdpi": (960, 1600), "xxxhdpi": (1280, 1920)}


def round_mask(size):
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).ellipse([0, 0, size * 4 - 1, size * 4 - 1], fill=255)
    return m.resize((size, size), Image.LANCZOS)


def main():
    art = Image.open(SRC_FULL).convert("RGBA")
    n = 0

    for density, size in LAUNCHER.items():
        d = os.path.join(RES, "mipmap-" + density)
        os.makedirs(d, exist_ok=True)
        square = art.resize((size, size), Image.LANCZOS)
        square.save(os.path.join(d, "ic_launcher.png"))
        rnd = square.copy()
        rnd.putalpha(round_mask(size))
        rnd.save(os.path.join(d, "ic_launcher_round.png"))
        n += 2

    # Adaptive foreground: the launcher crops this to whatever shape the phone
    # uses, and only the middle ~66% is guaranteed visible, so the artwork has
    # to sit inside that safe zone on a transparent canvas.
    for density, size in FOREGROUND.items():
        d = os.path.join(RES, "mipmap-" + density)
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        inner = int(size * 0.66)
        art_small = art.resize((inner, inner), Image.LANCZOS)
        mask = round_mask(inner)
        canvas.paste(art_small, ((size - inner) // 2, (size - inner) // 2), mask)
        canvas.save(os.path.join(d, "ic_launcher_foreground.png"))
        n += 1

    # background layer colour behind that foreground
    with open(os.path.join(RES, "drawable", "ic_launcher_background.xml"), "w",
              encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
                '    <color name="ic_launcher_background">#1A1230</color>\n</resources>\n')

    # Splash: the icon centred on the game's background colour, so the launch
    # screen matches the first frame instead of flashing white.
    for density, (w, h) in SPLASH_PORT.items():
        for orient, size in (("port", (w, h)), ("land", (h, w))):
            d = os.path.join(RES, "drawable-%s-%s" % (orient, density))
            os.makedirs(d, exist_ok=True)
            sp = Image.new("RGB", size, BG)
            icon = int(min(size) * 0.34)
            im = art.resize((icon, icon), Image.LANCZOS)
            m = round_mask(icon)
            sp.paste(im, ((size[0] - icon) // 2, (size[1] - icon) // 2), m)
            sp.save(os.path.join(d, "splash.png"))
            n += 1

    base = Image.new("RGB", (480, 800), BG)
    icon = int(480 * 0.34)
    im = art.resize((icon, icon), Image.LANCZOS)
    base.paste(im, ((480 - icon) // 2, (800 - icon) // 2), round_mask(icon))
    base.save(os.path.join(RES, "drawable", "splash.png"))
    n += 1

    print("wrote %d Android image assets" % n)


if __name__ == "__main__":
    main()
