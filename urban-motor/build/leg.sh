#!/bin/bash
# leg.sh NAME URL -> NAME.mp4, NAME_first.png, NAME_last.png, contact sheet in scratchpad
set -e
N=$1; URL=$2; SP=/tmp/claude-0/-home-user-scroll-world/82dd6f18-c3ff-5de2-a2bc-93aab74eb050/scratchpad
curl -sf -o $N.mp4 "$URL"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,nb_frames -of csv=p=0 $N.mp4
ffmpeg -v error -y -i $N.mp4 -vf "select=eq(n\,0)" -frames:v 1 ${N}_first.png
ffmpeg -v error -y -sseof -0.5 -i $N.mp4 -update 1 ${N}_last.png
W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 $N.mp4 | awk -F, '{print ($1>$2)?"320:-1":"-1:320"}')
ffmpeg -v error -y -i $N.mp4 -vf "fps=1,scale=$W,tile=8x1" -frames:v 1 $SP/${N}_contact.jpg
echo ok
# biggest frame-to-frame change: > 0.2 means a hard cut inside the clip
ffmpeg -v error -i $N.mp4 -vf "select='gte(scene,0)',metadata=print:file=-" -f null - 2>/dev/null | grep -B1 scene_score | paste - - | sed -E 's/.*pts_time:([0-9.]+).*scene_score=([0-9.]+).*/\2 \1/' | sort -rn | head -1 | awk '{print "max scene change", $1, "at", $2 "s", ($1>0.2?"<-- CUT":"")}'
