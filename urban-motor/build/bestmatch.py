import sys, subprocess, math, numpy as np
from PIL import Image
# bestmatch.py VIDEO REF.png FROM TO -> frame index in [FROM,TO] most similar to REF
v, ref, a, b = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
r = np.asarray(Image.open(ref).convert('RGB').resize((320,180) if Image.open(ref).width>Image.open(ref).height else (180,320))).astype(float)
h, w = r.shape[:2]
raw = subprocess.run(['ffmpeg','-v','error','-i',v,'-vf',f"select='between(n,{a},{b})',scale={w}:{h}",'-vsync','0','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
fr = np.frombuffer(raw,np.uint8).reshape(-1,h,w,3).astype(float)
ps = [10*math.log10(255**2/max(((f-r)**2).mean(),1e-9)) for f in fr]
i = int(np.argmax(ps)); print(a+i, round(ps[i],1))
