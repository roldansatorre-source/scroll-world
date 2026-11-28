#!/bin/bash
# usage: leg.sh <name e.g. s1 | s1-m> <url>
set -e
cd /home/user/scroll-world/baremo
n=$1; url=$2
curl -fsSL -m 180 "$url" -o src/leg_$n.mp4
ffprobe -v error -show_entries stream=width,height -show_entries format=duration -of compact src/leg_$n.mp4
ffmpeg -loglevel error -y -ss 0 -i src/leg_$n.mp4 -frames:v 1 frames/${n}_first.png
ffmpeg -loglevel error -y -sseof -0.15 -i src/leg_$n.mp4 -frames:v 1 frames/${n}_last.png
for t in 2 4 6; do ffmpeg -loglevel error -y -ss $t -i src/leg_$n.mp4 -frames:v 1 frames/${n}_t$t.png; done
python3 - "$n" <<'PY'
import sys; from PIL import Image
n=sys.argv[1]; fs=[f'frames/{n}_{s}.png' for s in ['first','t2','t4','t6','last']]
ims=[Image.open(f).convert('RGB') for f in fs]; w,h=ims[0].size
tw=480; th=int(h*tw/w)
sheet=Image.new('RGB',(len(ims)*(tw+8),th),'white')
for i,im in enumerate(ims): sheet.paste(im.resize((tw,th)),(i*(tw+8),0))
sheet.save(f'frames/{n}_sheet.jpg',quality=82); print('sheet ok')
PY
