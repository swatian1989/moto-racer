"""
Generate the Google Play feature graphic (1024x500) for Musa Moto Racer.

    python store/make_store_art.py  ->  store/feature-graphic.png

Play also wants a 512x512 icon, which is already icons/icon-512.png.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
W, H = 1024, 500
SS = 2                      # supersample, then downscale for clean edges

STOPS = [(0.00, (0x24, 0x1a, 0x4a)), (0.32, (0x5a, 0x3a, 0x7a)),
         (0.55, (0xc8, 0x5a, 0x6a)), (0.74, (0xff, 0x8a, 0x4a)),
         (0.88, (0xff, 0xc0, 0x6a)), (1.00, (0xff, 0xe7, 0xa8))]


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def sky_at(t):
    for i in range(len(STOPS) - 1):
        p0, c0 = STOPS[i]
        p1, c1 = STOPS[i + 1]
        if p0 <= t <= p1:
            return lerp(c0, c1, (t - p0) / (p1 - p0))
    return STOPS[-1][1]


def font(size, bold=True):
    for name in (("ariblk.ttf", "impact.ttf", "arialbd.ttf") if bold else ("arial.ttf",)):
        p = os.path.join(r"C:\Windows\Fonts", name)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def glow_text(img, xy, text, fnt, fill, glow, spread=9, anchor="mm"):
    """Draw text with a soft glow, the way the game's own title looks."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for r in range(spread, 0, -1):
        a = int(70 * (1 - r / float(spread)) ** 1.5)
        for dx, dy in ((-r, 0), (r, 0), (0, -r), (0, r),
                       (-r, -r), (r, -r), (-r, r), (r, r)):
            d.text((xy[0] + dx, xy[1] + dy), text, font=fnt,
                   fill=glow + (a,), anchor=anchor)
    img.alpha_composite(layer)
    ImageDraw.Draw(img).text(xy, text, font=fnt, fill=fill + (255,), anchor=anchor)


def main():
    w, h = W * SS, H * SS
    img = Image.new("RGBA", (w, h), (0x1a, 0x12, 0x30, 255))
    d = ImageDraw.Draw(img, "RGBA")

    horizon = int(h * 0.62)
    for y in range(horizon):
        d.line([(0, y), (w, y)], fill=sky_at(y / horizon) + (255,))

    # sun low on the horizon with a wide halo
    sx, sy, sr = int(w * 0.5), int(horizon * 0.9), int(h * 0.105)
    halo = int(sr * 6.5)
    g = Image.new("L", (64, 64))
    gp = g.load()
    for gy in range(64):
        for gx in range(64):
            dist = min(1.0, math.hypot((gx - 31.5) / 31.5, (gy - 31.5) / 31.5))
            gp[gx, gy] = int(190 * (1 - dist) ** 2.6)
    g = g.resize((halo, halo), Image.LANCZOS)
    glow = Image.new("RGBA", (halo, halo), (255, 150, 70, 0))
    glow.putalpha(g)
    img.alpha_composite(glow, (sx - halo // 2, sy - halo // 2))
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(0xff, 0xf2, 0xc0, 255))

    # sea
    for y in range(horizon, h):
        t = (y - horizon) / float(h - horizon)
        d.line([(0, y), (w, y)], fill=lerp((0x1a, 0x4a, 0x6e), (0x0a, 0x1e, 0x3a), t) + (255,))
    for y in range(horizon, h):
        t = (y - horizon) / float(h - horizon)
        gw = int(w * (0.02 + t * 0.10))
        a = int(140 * (1 - t) ** 1.4)
        if a > 2:
            d.line([(sx - gw, y), (sx + gw, y)], fill=(255, 220, 150, a))

    # road running to the horizon
    top_w, bot_w = int(w * 0.045), int(w * 0.46)
    d.polygon([(sx - top_w, horizon), (sx + top_w, horizon),
               (sx + bot_w, h), (sx - bot_w, h)], fill=(0x2a, 0x26, 0x30, 255))
    yy = horizon
    while yy < h:
        t = (yy - horizon) / float(h - horizon)
        seg = int(h * (0.02 + t * 0.13))
        lw = int(w * (0.002 + t * 0.016))
        d.polygon([(sx - lw, yy), (sx + lw, yy),
                   (sx + int(lw * 1.6), min(h, yy + seg)),
                   (sx - int(lw * 1.6), min(h, yy + seg))],
                  fill=(0xff, 0xd2, 0x3a, 255))
        yy += int(seg * 2.0)

    # rider, small, at the bottom of the road
    u = h * 0.062
    by = int(h * 0.93)
    SIL = (0x12, 0x0c, 0x1e, 255)
    d.ellipse([sx - u * 1.5, by - u * 0.2, sx + u * 1.5, by + u * 0.2], fill=(0, 0, 0, 130))
    d.rounded_rectangle([sx - u * .42, by - u * 1.5, sx + u * .42, by],
                        radius=u * .3, fill=(0x0a, 0x0a, 0x0a, 255))
    d.polygon([(sx - u * .62, by - u * 1.3), (sx + u * .62, by - u * 1.3),
               (sx + u * .46, by - u * 2.2), (sx - u * .46, by - u * 2.2)],
              fill=(0xd0, 0x14, 0x00, 255))
    d.rounded_rectangle([sx - u * .3, by - u * 1.62, sx + u * .3, by - u * 1.44],
                        radius=u * .07, fill=(0xff, 0x3a, 0x2a, 255))
    d.polygon([(sx - u * .86, by - u * 2.86), (sx + u * .86, by - u * 2.86),
               (sx + u * .55, by - u * 2.0), (sx - u * .55, by - u * 2.0)], fill=SIL)
    for s in (-1, 1):
        d.polygon([(sx + s * u * .8, by - u * 2.8), (sx + s * u * .5, by - u * 2.74),
                   (sx + s * u * .95, by - u * 1.95), (sx + s * u * 1.26, by - u * 2.02)],
                  fill=SIL)
    hr = u * .47
    hy = by - u * 3.24
    d.ellipse([sx - hr, hy - hr, sx + hr, hy + hr], fill=(0xe8, 0xe8, 0xe8, 255))
    d.ellipse([sx - hr * .8, hy - hr * .16, sx + hr * .8, hy + hr * .72],
              fill=(0x22, 0x1a, 0x0a, 255))

    # scrim so the type stays readable over the sky
    scrim = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    top = int(h * 0.34)
    for y in range(top):
        sd.line([(0, y), (w, y)],
                fill=(0x10, 0x08, 0x20, int(70 * (1 - y / float(top)) ** 1.6)))
    img.alpha_composite(scrim)

    glow_text(img, (w // 2, int(h * 0.13)), "MUSA", font(int(h * 0.075)),
              (0xff, 0x8a, 0x4a), (0xff, 0x6a, 0x00), spread=7)
    glow_text(img, (w // 2, int(h * 0.28)), "MOTO RACER", font(int(h * 0.19)),
              (0xff, 0xd2, 0x3a), (0xff, 0x6a, 0x00), spread=11)
    glow_text(img, (w // 2, int(h * 0.42)), "C O A S T L I N E", font(int(h * 0.062)),
              (0xff, 0xff, 0xff), (0x00, 0x00, 0x00), spread=4)

    out = os.path.join(HERE, "feature-graphic.png")
    img.convert("RGB").resize((W, H), Image.LANCZOS).save(out, optimize=True)
    print("feature graphic: %s  (%dx%d, %.0f KB)"
          % (out, W, H, os.path.getsize(out) / 1024))


if __name__ == "__main__":
    main()
