"""Flatten AI ghosting in the empty background around the diorama (mobile chain).
Per column, find where the scene starts (top) and ends (bottom) using a blurred
difference from the background colour (flat walls register, blocky ghosts don't),
then replace everything outside with the smoothed background colour, feathered.
usage: clean_bg.py in.mp4 out.mp4"""
import sys, subprocess, numpy as np
from scipy.ndimage import uniform_filter, minimum_filter1d, maximum_filter1d
src, dst = sys.argv[1], sys.argv[2]
W, H = 720, 1280
fps = subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=r_frame_rate','-of','csv=p=0',src],capture_output=True,text=True).stdout.strip()
rd = subprocess.Popen(['ffmpeg','-loglevel','error','-i',src,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
frames=[]
while True:
    b = rd.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    frames.append(np.frombuffer(b,np.uint8).reshape(H,W,3).astype(np.float32))
n=len(frames)
bgs=np.array([np.median(f[0:40,60:660].reshape(-1,3),0) for f in frames])
k=9; pad=np.pad(bgs,((k,k),(0,0)),mode='edge'); bgs=np.array([pad[i:i+2*k+1].mean(0) for i in range(n)])
TH, MARG, FEA = 24, 14, 24
top=np.zeros((n,W)); bot=np.zeros((n,W))
for i,(f,bg) in enumerate(zip(frames,bgs)):
    d=uniform_filter(np.abs(f-bg).max(2),size=21)
    m=d>TH
    has=m.any(0)
    t=np.where(has,m.argmax(0),H); b=np.where(has,H-1-m[::-1].argmax(0),0)
    top[i]=minimum_filter1d(t,121); bot[i]=maximum_filter1d(b,121)
# temporal smoothing (min/max then mean) so the boundary never jitters
def tsmooth(a,fn):
    p=np.pad(a,((k,k),(0,0)),mode='edge'); a2=np.array([fn(p[i:i+2*k+1],0) for i in range(n)])
    p=np.pad(a2,((k,k),(0,0)),mode='edge'); return np.array([p[i:i+2*k+1].mean(0) for i in range(n)])
top=tsmooth(top,np.min); bot=tsmooth(bot,np.max)
ys=np.arange(H)[:,None].astype(np.float32)
wr=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',fps,'-i','-',
                     '-c:v','libx264','-crf','14','-preset','slow','-pix_fmt','yuv420p',dst],stdin=subprocess.PIPE)
for f,t,b,bg in zip(frames,top,bot,bgs):
    a_top=np.clip(((t-MARG)-ys)/FEA,0,1); a_bot=np.clip((ys-(b+MARG))/FEA,0,1)
    a=np.maximum(a_top,a_bot)
    # side bands: flatten near-background pixels (stripe artifacts) without touching the scene
    d=uniform_filter(np.abs(f-bg).max(2),size=9)
    band=np.zeros(W,np.float32); band[:28]=1; band[-28:]=1
    a=np.maximum(a, band[None,:]*np.clip((40-d)/15,0,1))[:,:,None]
    wr.stdin.write(np.clip(f*(1-a)+bg*a,0,255).astype(np.uint8).tobytes())
wr.stdin.close(); wr.wait(); print(n,'frames ok')
