import sys, math
from PIL import Image, ImageChops, ImageStat
a=Image.open(sys.argv[1]).convert('RGB'); b=Image.open(sys.argv[2]).convert('RGB').resize(a.size)
d=ImageStat.Stat(ImageChops.difference(a,b)); mse=sum(x*x for x in d.rms)/3
print('seam PSNR', round(10*math.log10(255**2/max(mse,1e-9)),1))
