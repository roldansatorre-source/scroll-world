#!/bin/bash
# splice.sh NAME A BRIDGE B : NAME frames [0..A] + BRIDGE[1..] crossfaded (4 frames) into NAME frames [B..]  -> NAME.mp4 (original kept as NAME_uncut.mp4)
set -e
N=$1; A=$2; BR=$3; B=$4
[ -f ${N}_uncut.mp4 ] || cp $N.mp4 ${N}_uncut.mp4
S=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=x ${N}_uncut.mp4)
BN=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 $BR)
OFF=$(python3 -c "print(round(($A+1+$BN-1-4)/24,4))")
ffmpeg -v error -y -i ${N}_uncut.mp4 -i $BR -filter_complex "\
[0:v]trim=start_frame=0:end_frame=$((A+1)),setpts=PTS-STARTPTS,fps=24,format=yuv420p[a];\
[1:v]scale=${S/x/:},setsar=1,trim=start_frame=1,setpts=PTS-STARTPTS,fps=24,format=yuv420p[b];\
[0:v]trim=start_frame=$B,setpts=PTS-STARTPTS,fps=24,format=yuv420p[c];\
[a][b]concat=n=2:v=1,settb=1/24[ab];[c]settb=1/24[c2];[ab][c2]xfade=transition=fade:duration=0.1667:offset=$OFF[v]" -map "[v]" -an -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p $N.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 $N.mp4
ffmpeg -v error -i $N.mp4 -vf "select='gte(scene,0)',metadata=print:file=-" -f null - 2>/dev/null | grep -o "scene_score=[0-9.]*" | sort -t= -k2 -rn | head -1
