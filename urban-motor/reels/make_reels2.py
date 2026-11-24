"""Second batch of reels: slow-motion drop, foam, van wrap. Run from urban-motor/: python3 reels/make_reels2.py"""
import os
from make_reels import clip, concat, end_card, save, text_layer, TMP, OUT, BLUE

S = 'build/reels2'
end = os.path.join(TMP, 'end.mp4'); end_card(end)

def reel(name, src, parts):
    """parts: list of (ss, dur, speed, overlay_lines|None, ov_in)"""
    out = []
    for i, (ss, dur, sp, lines, ov_in) in enumerate(parts):
        ov = save(text_layer(lines, 1480), f'{name}{i}.png') if lines else None
        q = os.path.join(TMP, f'{name}{i}.mp4'); clip(src, ss, dur, q, ov, ov_in, speed=sp); out.append(q)
    concat(out + [end], f'{OUT}/{name}.mp4')

W, B = (255, 255, 255), BLUE
if __name__ == '__main__':
    reel('reel-4-gota', f'{S}/gota.mp4', [
        (0, 9.5, 1.0, [('Así queda', 'ExtraBold', 100, W), ('tu pintura.', 'ExtraBold', 100, B)], 4.5)])
    reel('reel-5-espuma', f'{S}/espuma.mp4', [
        (0, 9.5, 1.0, [('Lavado a mano.', 'ExtraBold', 96, W), ('Sin manguera, en tu puerta.', 'Bold', 54, W)], 4.0)])
    reel('reel-6-furgoneta', f'{S}/furgo.mp4', [
        (2.4, 7.6, 1.0, [('Tu furgoneta,', 'ExtraBold', 96, W), ('tu mejor anuncio.', 'ExtraBold', 96, B)], 4.0)])
    print('done')
