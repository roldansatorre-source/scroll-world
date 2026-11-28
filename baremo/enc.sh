#!/bin/bash
# usage: enc.sh <k>   (encodes leg_s<k> + leg_s<k>-m and posters)
set -e; cd /home/user/scroll-world/baremo; k=$1; A=site/assets
ffmpeg -loglevel error -y -i src/leg_s$k.mp4 -an -vf "unsharp=5:5:0.6:5:5:0.0" -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -g 8 -keyint_min 8 -sc_threshold 0 -movflags +faststart $A/vid/s$k.mp4
ffmpeg -loglevel error -y -i src/leg_s$k-m.mp4 -an -vf "scale=720:-2,unsharp=5:5:0.6:5:5:0.0" -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p -g 4 -keyint_min 4 -sc_threshold 0 -movflags +faststart $A/vid/s$k-m.mp4
python3 -c "
from PIL import Image
Image.open('frames/s${k}_first.png').convert('RGB').save('$A/s$k-p.webp',quality=84)
Image.open('frames/s${k}-m_first.png').convert('RGB').save('$A/s$k-pm.webp',quality=84)"
ls -la $A/vid/s$k*.mp4 $A/s$k-p*.webp
