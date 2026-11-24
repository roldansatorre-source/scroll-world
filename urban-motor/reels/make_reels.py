"""Build three vertical 1080x1920 reels for Urban Motor from the site's footage.

Run from urban-motor/:  python3 reels/make_reels.py
Outputs reels/reel-1-logo.mp4, reels/reel-2-proceso.mp4, reels/reel-3-antes-despues.mp4
"""
import os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 24
B = 'build'
OUT = 'reels'
FONT = '/usr/share/fonts/opentype/inter/Inter-'
BLUE, BLUE_D, BLACK, GREY = (47, 107, 255), (31, 79, 214), (11, 13, 18), (201, 206, 216)
TMP = tempfile.mkdtemp()


def font(w, s): return ImageFont.truetype(f'{FONT}{w}.otf', s)


def sh(*a): subprocess.run(a, check=True)


def text_layer(lines, y, anchor='mm', shadow=True):
    """Transparent full-frame PNG with stacked lines: [(text, weight, size, colour), ...]."""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for t, w, s, c in lines:
        f = font(w, s)
        if shadow:
            sh_im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(sh_im).text((W // 2, y + 4), t, font=f, fill=(0, 0, 0, 200), anchor=anchor)
            im.alpha_composite(sh_im.filter(ImageFilter.GaussianBlur(10)))
        d.text((W // 2, y), t, font=f, fill=c, anchor=anchor)
        y += int(s * 1.18)
    return im


def save(im, name):
    p = os.path.join(TMP, name); im.save(p); return p


def stripe(im, y=150, h=26):
    """Diagonal brand stripe across the frame."""
    s = Image.new('RGBA', (W * 2, h), BLUE + (255,)).rotate(-8, expand=True)
    im.alpha_composite(s, (-W // 2, y))
    return im


def end_card(path, secs=3.2):
    """Black card: logo, tagline, towns, WhatsApp and Instagram."""
    im = Image.new('RGBA', (W, H), BLACK + (255,))
    stripe(im, 260)
    logo = Image.open('assets/marca/logo-um.png').convert('RGBA')
    logo = logo.resize((560, int(560 * logo.height / logo.width)))
    im.alpha_composite(logo, ((W - logo.width) // 2, 620))
    d = ImageDraw.Draw(im)
    f = font('ExtraBold', 64)
    x = W // 2; y = 860
    # two-tone wordmark
    u, m = 'URBAN ', 'MOTOR'
    wu = d.textlength(u, font=f); wm = d.textlength(m, font=f)
    d.text((x - (wu + wm) / 2, y), u, font=f, fill=(255, 255, 255))
    d.text((x - (wu + wm) / 2 + wu, y), m, font=f, fill=BLUE)
    im.alpha_composite(text_layer([
        ('Limpieza, pulido y restauración', 'SemiBold', 48, (255, 255, 255)),
        ('a domicilio', 'SemiBold', 48, (255, 255, 255)),
        ('Alcoi · Cocentaina · Muro', 'Medium', 40, GREY),
    ], 1040, shadow=False))
    pill = Image.new('RGBA', (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle((170, 1350, W - 170, 1470), radius=60, fill=(37, 211, 102))
    pd.text((W // 2, 1410), 'WhatsApp 614 18 05 75', font=font('Bold', 52), fill=(255, 255, 255), anchor='mm')
    pd.text((W // 2, 1560), '@urbanmotoralcoy', font=font('SemiBold', 44), fill=GREY, anchor='mm')
    pd.text((W // 2, 1640), 'De lunes a viernes', font=font('Medium', 38), fill=BLUE, anchor='mm')
    im.alpha_composite(pill)
    img = save(im, 'end.png')
    sh('ffmpeg', '-v', 'error', '-y', '-loop', '1', '-t', str(secs), '-i', img,
       '-vf', f'fps={FPS},format=yuv420p,fade=t=in:st=0:d=0.35', '-c:v', 'libx264', '-crf', '18', path)


def clip(src, ss, dur, path, overlay=None, ov_in=0.25, ov_dur=None, speed=1.0):
    """Cut a vertical segment, fit to 1080x1920, optional text overlay fading in."""
    vf = f'[0:v]setpts=PTS/{speed},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},format=yuv420p[v]'
    cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', str(ss), '-t', str(dur * speed), '-i', src]
    if overlay:
        od = ov_dur or (dur - ov_in)
        cmd += ['-loop', '1', '-t', str(dur), '-i', overlay]
        vf += (f';[1:v]format=rgba,fade=t=in:st={ov_in}:d=0.35:alpha=1,'
               f'fade=t=out:st={ov_in + od - 0.35}:d=0.35:alpha=1[o];[v][o]overlay=0:0:shortest=1[v2]')
        out = '[v2]'
    else:
        out = '[v]'
    sh(*cmd, '-filter_complex', vf, '-map', out, '-an', '-c:v', 'libx264', '-crf', '18', '-t', str(dur), path)


def concat(parts, out):
    lst = os.path.join(TMP, os.path.basename(out) + '.txt')
    with open(lst, 'w') as f:
        f.writelines(f"file '{os.path.abspath(p)}'\n" for p in parts)
    sh('ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst,
       '-f', 'lavfi', '-t', '60', '-i', 'anullsrc=r=44100:cl=stereo', '-shortest',
       '-c:v', 'libx264', '-crf', '20', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-r', str(FPS),
       '-c:a', 'aac', '-b:a', '64k', '-movflags', '+faststart', out)


def label(t, sub=None):
    lines = [(t, 'ExtraBold', 92, (255, 255, 255))]
    if sub: lines.append((sub, 'SemiBold', 44, (220, 228, 255)))
    return save(text_layer(lines, 1500), f'lbl_{abs(hash(t))}.png')


def main():
    os.makedirs(OUT, exist_ok=True)
    end = os.path.join(TMP, 'end.mp4'); end_card(end)

    # ---------- Reel 1: dirty logo gets cleaned ----------
    p = []
    q = os.path.join(TMP, 'r1a.mp4'); clip(f'{B}/lm.mp4', 0, 3.2, q, save(text_layer([('¿Tu coche está así?', 'ExtraBold', 88, (255, 255, 255))], 1520), 'r1t1.png'), 0.3); p.append(q)
    q = os.path.join(TMP, 'r1b.mp4'); clip(f'{B}/lm.mp4', 3.2, 6.8, q, save(text_layer([('Lo dejamos', 'ExtraBold', 104, (255, 255, 255)), ('como nuevo.', 'ExtraBold', 104, BLUE)], 1440), 'r1t2.png'), 3.4, 3.2); p.append(q)
    q = os.path.join(TMP, 'r1c.mp4'); clip(f'{B}/tm.mp4', 0, 5, q, save(text_layer([('Voy yo.', 'ExtraBold', 96, (255, 255, 255)), ('Tu coche no se mueve.', 'Bold', 60, (255, 255, 255))], 1480), 'r1t3.png'), 2.4); p.append(q)
    p.append(end)
    concat(p, f'{OUT}/reel-1-logo.mp4')

    # ---------- Reel 2: fast process montage ----------
    p = []
    q = os.path.join(TMP, 'r2t.mp4'); clip(f'{B}/xm1.mp4', 0.5, 2.4, q, save(text_layer([('Así trabajo.', 'ExtraBold', 110, (255, 255, 255)), ('A domicilio en Alcoi y comarca', 'SemiBold', 46, (220, 228, 255))], 1460), 'r2t0.png'), 0.2); p.append(q)
    for i, (src, ss, dur, t, sub) in enumerate([
        ('xm2', 3.2, 2.6, 'Interior', 'Cepillo, aspirado y vapor'),
        ('xm3', 4.0, 2.4, 'Lavado a mano', 'Sin manguera'),
        ('pm_lock', 4.2, 2.8, 'Pulido', 'Fuera marcas y rayas'),
        ('xm5', 2.5, 2.4, 'Llantas y cuero', 'Restauración'),
        ('xm6', 4.0, 2.4, 'Motos', 'Y cascos'),
        ('xm8', 4.0, 2.8, 'Rotulación', 'Vinilos y furgonetas'),
    ]):
        q = os.path.join(TMP, f'r2_{i}.mp4'); clip(f'{B}/{src}.mp4', ss, dur, q, label(t, sub), 0.15); p.append(q)
    p.append(end)
    concat(p, f'{OUT}/reel-2-proceso.mp4')

    # ---------- Reel 3: real before/after with a blue wipe ----------
    pairs = [('interior', 'Limpieza de interiores'), ('faros', 'Restauración de faros'), ('pulido', 'Pulido de carrocería')]
    fdir = os.path.join(TMP, 'r3'); os.makedirs(fdir, exist_ok=True)
    n = 0
    head = text_layer([('Trabajos reales', 'ExtraBold', 96, (255, 255, 255))], 200, shadow=False)
    for name, title in pairs:
        a = Image.open(f'assets/fotos/{name}-antes.jpg').convert('RGB')
        b = Image.open(f'assets/fotos/{name}-despues.jpg').convert('RGB')
        PW, PH = 1000, int(1000 * a.height / a.width)
        PH = min(PH, 1300)
        def fit(im):
            r = max(PW / im.width, PH / im.height); im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1))
            x = (im.width - PW) // 2; y = (im.height - PH) // 2; return im.crop((x, y, x + PW, y + PH))
        a, b = fit(a), fit(b)
        frames = int(3.8 * FPS)
        for k in range(frames):
            t = k / frames
            wipe = min(1, max(0, (t - 0.2) / 0.55))           # 0..1 reveal
            zoom = 1 + 0.04 * t
            canvas = Image.new('RGBA', (W, H), BLACK + (255,))
            stripe(canvas, 1740, 20)
            canvas.alpha_composite(head)
            im = a.copy(); xcut = int(PW * wipe)
            if xcut > 0: im.paste(b.crop((0, 0, xcut, PH)), (0, 0))
            im = im.resize((int(PW * zoom), int(PH * zoom))).crop((int(PW * (zoom - 1) / 2), int(PH * (zoom - 1) / 2), int(PW * (zoom - 1) / 2) + PW, int(PH * (zoom - 1) / 2) + PH))
            ox, oy = (W - PW) // 2, 360
            canvas.alpha_composite(im.convert('RGBA'), (ox, oy))
            d = ImageDraw.Draw(canvas)
            if 0 < wipe < 1:
                lx = ox + int(PW * wipe); d.rectangle((lx - 4, oy, lx + 4, oy + PH), fill=BLUE)
            tag_f = font('Bold', 36)
            d.rounded_rectangle((ox + 24, oy + 24, ox + 200, oy + 84), radius=30, fill=(11, 13, 18, 200)); d.text((ox + 112, oy + 54), 'ANTES', font=tag_f, fill=(255, 255, 255), anchor='mm')
            if wipe > 0.6:
                d.rounded_rectangle((ox + PW - 240, oy + 24, ox + PW - 24, oy + 84), radius=30, fill=BLUE); d.text((ox + PW - 132, oy + 54), 'DESPUÉS', font=tag_f, fill=(255, 255, 255), anchor='mm')
            d.text((W // 2, oy + PH + 90), title, font=font('ExtraBold', 64), fill=(255, 255, 255), anchor='mm')
            canvas.convert('RGB').save(f'{fdir}/{n:05d}.png'); n += 1
    r3 = os.path.join(TMP, 'r3.mp4')
    sh('ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', f'{fdir}/%05d.png', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', r3)
    concat([r3, end], f'{OUT}/reel-3-antes-despues.mp4')
    print('done')



if __name__ == '__main__':
    main()
