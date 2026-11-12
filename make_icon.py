from PIL import Image, ImageDraw, ImageFilter
import os, math
S = 4  # supersample

def pen(L, W, body, dark, light):
    m = int(W * 0.8)
    im = Image.new("RGBA", (L + 2 * m, W + 2 * m), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0 = m
    cy = m + W // 2
    r = W // 2
    # body
    d.rounded_rectangle([x0 + L * 0.07, cy - r, x0 + L * 0.80, cy + r], radius=r * 0.55, fill=body)
    d.rounded_rectangle([x0 + L * 0.07, cy + r * 0.25, x0 + L * 0.80, cy + r], radius=r * 0.55, fill=dark)
    d.rectangle([x0 + L * 0.07 + r, cy + r * 0.25, x0 + L * 0.80 - r, cy + r * 0.45], fill=body)
    d.rounded_rectangle([x0 + L * 0.10, cy - r * 0.72, x0 + L * 0.77, cy - r * 0.38], radius=r * 0.2, fill=light)
    # clip
    d.rounded_rectangle([x0 + L * 0.20, cy - r * 1.08, x0 + L * 0.50, cy - r * 0.8], radius=r * 0.15, fill=(235, 235, 235, 255))
    # cap
    d.rounded_rectangle([x0, cy - r * 0.95, x0 + L * 0.12, cy + r * 0.95], radius=r * 0.5, fill=(40, 40, 46, 255))
    # metal ring
    d.rectangle([x0 + L * 0.80, cy - r * 0.98, x0 + L * 0.85, cy + r * 0.98], fill=(210, 212, 218, 255))
    # wood cone
    d.polygon([(x0 + L * 0.85, cy - r * 0.9), (x0 + L * 0.985, cy), (x0 + L * 0.85, cy + r * 0.9)], fill=(236, 208, 160, 255))
    # lead tip
    d.polygon([(x0 + L * 0.945, cy - r * 0.28), (x0 + L, cy), (x0 + L * 0.945, cy + r * 0.28)], fill=(30, 30, 30, 255))
    return im

def rot(im, ang):
    return im.rotate(ang, resample=Image.BICUBIC, expand=True)

def shadowed(im):
    a = im.split()[3].filter(ImageFilter.GaussianBlur(10 * S))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * 0.45)))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 14 * S))
    out.alpha_composite(im)
    return out

def pens_layer(size, scale):
    N = size * S
    layer = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    L = int(N * 0.70 * scale)
    W = int(L * 0.115)
    p1 = shadowed(rot(pen(L, W, (230, 57, 70, 255), (170, 30, 45, 255), (255, 150, 150, 255)), 40))
    p2 = shadowed(rot(pen(L, W, (29, 111, 224, 255), (18, 70, 160, 255), (140, 190, 255, 255)), -40))
    for p in (p1, p2):
        layer.alpha_composite(p, ((N - p.width) // 2, (N - p.height) // 2))
    return layer

def bg(size):
    N = size
    im = Image.new("RGB", (N, N))
    px = im.load()
    for y in range(N):
        for x in range(N):
            dx, dy = (x - N * 0.5) / N, (y - N * 0.42) / N
            t = min(1, math.hypot(dx, dy) * 1.5)
            c0, c1 = (46, 100, 70), (18, 44, 30)
            px[x, y] = tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3))
    return im

os.makedirs("assets", exist_ok=True)
SIZE = 1024
base = bg(SIZE).convert("RGBA")
fg_full = pens_layer(SIZE, 1.25).resize((SIZE, SIZE), Image.LANCZOS)
base.alpha_composite(fg_full)
base.convert("RGB").save("assets/icon-only.png")
fg = pens_layer(SIZE, 1.1).resize((SIZE, SIZE), Image.LANCZOS)
fg.save("assets/icon-foreground.png")
print("ok")
