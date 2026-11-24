#!/bin/bash
# endlock.sh IN.mp4 TARGET.png OUT.mp4 : crossfade the last 4 frames into TARGET so the clip ends exactly on it
set -e
S=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=x $1)
N=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 $1)
OFF=$(python3 -c "print(round(($N-4)/24,4))")
ffmpeg -v error -y -i $1 -loop 1 -t 0.25 -i $2 -filter_complex "[0:v]fps=24,format=yuv420p,settb=1/24[a];[1:v]scale=${S/x/:},setsar=1,fps=24,format=yuv420p,settb=1/24[b];[a][b]xfade=transition=fade:duration=0.1667:offset=$OFF[v]" -map "[v]" -an -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p $3
