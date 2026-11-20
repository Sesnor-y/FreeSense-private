import sys; sys.path.insert(0,'.')
import plotly.colors as pc
def hx(c):
    c=c.strip()
    if c.startswith('rgb'):
        return tuple(int(float(x)) for x in c[c.index('(')+1:-1].split(',')[:3])
    named={'lightgrey':'#D3D3D3','white':'#FFFFFF'}
    c=named.get(c,c).lstrip('#'); return tuple(int(c[i:i+2],16) for i in (0,2,4))
def lum(rgb):
    def ch(v):
        v/=255; return v/12.92 if v<=0.03928 else ((v+0.055)/1.055)**2.4
    r,g,b=map(ch,rgb); return 0.2126*r+0.7152*g+0.0722*b
def cr(a,b):
    la,lb=lum(hx(a) if isinstance(a,str) else a),lum(hx(b) if isinstance(b,str) else b)
    hi,lo=max(la,lb),min(la,lb); return (hi+0.05)/(lo+0.05)
def blend(fg,bg,alpha):
    f,b=hx(fg),hx(bg); return tuple(round(alpha*x+(1-alpha)*y) for x,y in zip(f,b))
pairs=[('light text on bg','#0F172A','#FFFFFF'),('light text on secondaryBg','#0F172A','#F8FAFC'),
('teal on white (link/text/accent)','#0D9488','#FFFFFF'),('white on teal (primary button)','#FFFFFF','#0D9488'),
('teal on light secondaryBg','#0D9488','#F8FAFC'),
('dark text on dark bg','#F1F5F9','#0F172A'),('dark text on dark secondaryBg','#F1F5F9','#1E293B'),
('teal on dark bg','#0D9488','#0F172A'),('teal on dark secondaryBg','#0D9488','#1E293B'),
('light borderColor on white (non-text)','#E2E8F0','#FFFFFF'),('dark borderColor on dark bg (non-text)','#334155','#0F172A'),
('plot BASE_TEXT on white','#1a1a1a','#FFFFFF'),('plot DARK_TEXT on dark bg','#F1F5F9','#0F172A'),
('plot muted #555555 on white','#555555','#FFFFFF'),('plot muted dark #94A3B8 on dark bg','#94A3B8','#0F172A'),
('grid lightgrey on white (non-text)','lightgrey','#FFFFFF'),('grid dark #334155 on dark bg','#334155','#0F172A'),
('NEUTRAL_FALLBACK #888888 on white','#888888','#FFFFFF'),('NEUTRAL_FALLBACK on dark','#888888','#0F172A'),
]
for n,a,b in pairs: print(f"{cr(a,b):6.2f}  {n}")
# captions: Streamlit fadedText60 = textColor at 60% opacity (verify)
for n,t,bg in [('light caption (text 60% alpha) on white','#0F172A','#FFFFFF'),('dark caption (text 60% alpha) on dark bg','#F1F5F9','#0F172A')]:
    print(f"{cr(blend(t,bg,0.6),hx(bg)):6.2f}  {n} (assumes 60% alpha)")
from utils.colours import PRODUCT_PALETTES, CLUSTER_PALETTES, GROUP_PALETTES, DRIVER_COLOUR_MAP
for name,pal in list(PRODUCT_PALETTES.items()):
    w=[round(cr(c,'#FFFFFF'),2) for c in pal]; d=[round(cr(c,'#0F172A'),2) for c in pal]
    print('PRODUCT',name,'min on white',min(w),'n<3:',sum(x<3 for x in w),'/',len(w),' min on dark',min(d),'n<3:',sum(x<3 for x in d))
for name,pal in list(CLUSTER_PALETTES.items()):
    w=[round(cr(c,'#FFFFFF'),2) for c in pal]; d=[round(cr(c,'#0F172A'),2) for c in pal]
    print('CLUSTER',name,'min on white',min(w),'n<3:',sum(x<3 for x in w),'/',len(w),' min on dark',min(d),'n<3:',sum(x<3 for x in d))
print({k:round(cr(v,'#FFFFFF'),2) for k,v in DRIVER_COLOUR_MAP.items()})
print('colourblind yellow F0E442 on white',round(cr('#F0E442','#FFFFFF'),2))
print('---options')
for c in ['#0F766E','#115E59','#0D9488']:
    print(c,'white-on',round(cr('#FFFFFF',c),2),'on dark bg',round(cr(c,'#0F172A'),2),'on dark2',round(cr(c,'#1E293B'),2))
print('sidebar caption light',round(cr(blend('#0F172A','#F8FAFC',0.6),hx('#F8FAFC')),2))
print('sidebar caption dark',round(cr(blend('#F1F5F9','#1E293B',0.6),hx('#1E293B')),2))
print('---misc')
for c,bg in [('#856404','#0F172A'),('#856404','#FFFFFF'),('#dc3545','#FFFFFF'),('#dc3545','#0F172A'),('#28a745','#FFFFFF'),('#28a745','#0F172A'),('#F1F5F9','#ffe0e0'),('#0F172A','#ffe0e0'),('#9e9e9e','#FFFFFF'),('#9e9e9e','#0F172A')]:
    print(c,'on',bg,round(cr(c,bg),2))
