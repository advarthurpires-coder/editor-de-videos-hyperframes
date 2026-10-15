import numpy as np, sys, json
def proj(P,T,X,fov=40):
    P,T,X=map(np.array,(P,T,X)); f=T-P; f/=np.linalg.norm(f)
    r=np.cross(f,[0,1,0]); r/=np.linalg.norm(r); u=np.cross(r,f)
    d=X-P; x,y,z=d@r,d@u,d@f
    th=np.tan(np.radians(fov/2))
    return round(float((x/(z*th*9/16)+1)/2*1080)), round(float((1-y/(z*th))/2*1920))
def report(P,T,fov=40,extra=()):
    pts={'topC':(0,4.16,0),'botC':(0,0,0.5),'L_bot':(-3.45,0,0.5),'R_bot':(3.45,0,0.5),'L_top':(-3.45,4.16,0),'R_top':(3.45,4.16,0)}
    pts.update(dict(extra))
    print(P,T,{k:proj(P,T,v,fov) for k,v in pts.items()})
for line in sys.stdin:
    if line.strip(): report(*json.loads(line))
