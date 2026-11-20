import sys, json, warnings, struct, time, re
warnings.filterwarnings("ignore"); sys.path.insert(0,".")
import plotly.graph_objects as go, plotly.io as pio
from utils.plot_theme import export_figure, _PRESETS
S=sys.argv[1]; mod=sys.argv[2]; wanted=sys.argv[3].split(",")
figs=json.load(open(f"{S}/figs_{mod}.json"))
seen=set()
def fonts(d, acc):
    if isinstance(d, dict):
        for k,v in d.items():
            if k=='size' and isinstance(v,(int,float)) and 'font' in str(acc[-1:]): pass
            if k.endswith('font') or k=='font':
                if isinstance(v, dict) and 'size' in v: acc.append(v['size'])
            fonts(v, acc)
    elif isinstance(d, list):
        for x in d: fonts(x, acc)
for key, js, wide in figs:
    if key in seen or (wanted!=['all'] and key not in wanted): continue
    seen.add(key)
    fig = pio.from_json(js)
    sizes=[]; fonts(json.loads(js), sizes)
    lw, lh = fig.layout.width, fig.layout.height
    for preset in ("word","powerpoint"):
        t=time.time()
        png = export_figure(fig, preset, fmt="png", wide=wide)
        w,h = struct.unpack(">II", png[16:24])
        open(f"{S}/img/{mod}_{key}_{preset}.png","wb").write(png)
        spec=_PRESETS[preset]; css_w = spec["wide_width"] if wide else spec["width"]
        page_in = (9.0 if wide else 6.5) if preset=="word" else 13.33
        pt_per_px = page_in*72/css_w
        base=17
        print(f"{key} {preset} wide={wide} layout=({lw}x{lh}) -> {w}x{h}px, {w/page_in:.0f} dpi at {page_in}in; base 17px={base*pt_per_px:.1f}pt; min font {min(sizes) if sizes else None}px={(min(sizes) if sizes else 0)*pt_per_px:.1f}pt; {time.time()-t:.1f}s")
    svg = export_figure(fig, "word", fmt="svg", wide=wide)
    open(f"{S}/img/{mod}_{key}_word.svg","wb").write(svg)
    print("   svg bytes", len(svg), "embedded fonts/text elems:", svg.count(b"<text"), "font-family Arial" , b"Arial" in svg)
