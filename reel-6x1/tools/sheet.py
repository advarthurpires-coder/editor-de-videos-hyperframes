import sys, glob
from PIL import Image, ImageDraw
d=sys.argv[1]; cols=int(sys.argv[2]) if len(sys.argv)>2 else 4
fs=sorted(glob.glob(d+'/f*.png'))
w,h=360,640
rows=(len(fs)+cols-1)//cols
sheet=Image.new('RGB',(cols*w,rows*(h+30)),'black')
dr=ImageDraw.Draw(sheet)
for i,f in enumerate(fs):
    im=Image.open(f).convert('RGB').resize((w,h))
    x=(i%cols)*w; y=(i//cols)*(h+30)
    sheet.paste(im,(x,y+30)); dr.text((x+5,y+8),f.split('_')[-1],fill='white')
sheet.save(d+'/sheet.jpg',quality=88)
