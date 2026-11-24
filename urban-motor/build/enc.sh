#!/bin/bash
# enc.sh d|m N : desktop dN.mp4 -> escena-N.mp4 (1080p, -g 8) ; mobile mN.mp4 -> escena-N-m.mp4 (720w portrait, -g 4)
set -e
K=$1; N=$2; A=../assets
if [ "$K" = d ]; then
  ffmpeg -v error -y -i d$N.mp4 -an -vf "scale=1280:-2,unsharp=5:5:0.5" -c:v libx264 -pix_fmt yuv420p -crf 23 -preset slow -g 8 -movflags +faststart $A/vid/escena-$N.mp4
  python3 -c "from PIL import Image; Image.open('d${N}_first.png').convert('RGB').resize((1600,900)).save('$A/escenas/escena-$N.webp', quality=80)"
else
  ffmpeg -v error -y -i m$N.mp4 -an -vf "scale=720:-2,unsharp=5:5:0.3" -c:v libx264 -pix_fmt yuv420p -crf 25 -preset slow -g 4 -movflags +faststart $A/vid/escena-$N-m.mp4
  python3 -c "from PIL import Image; im=Image.open('m${N}_first.png').convert('RGB'); im.resize((720,int(720*im.height/im.width))).save('$A/escenas/escena-$N-m.webp', quality=80)"
fi
