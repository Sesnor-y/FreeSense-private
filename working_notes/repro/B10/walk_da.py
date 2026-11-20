import sys, collections; sys.path.insert(0,'.')
import pandas as pd
from streamlit.testing.v1 import AppTest
import core.data as core_data, utils.ui_shell as ui_shell
raw=pd.read_excel('example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx')
class U: name='DA_chocolates_sensochoc.xlsx'
def patched():
    import core.data as core_data, utils.ui_shell as ui_shell, pandas as pd
    raw=pd.read_excel('example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx')
    class U: name='x.xlsx'
    ui_shell.render_data_upload_section=lambda *a,**k: U()
    core_data.load_data=lambda f: raw.copy()
    import app
at=AppTest.from_file('/var/home/Lukas/Projects/RATA-Flow-App/app.py',default_timeout=300)
ui_shell.render_data_upload_section=lambda *a,**k: U()
core_data.load_data=lambda f: raw.copy()
at.run()
def summary(tag):
    c=collections.Counter()
    for node in at.main:
        pass
    def walk(n):
        for ch in getattr(n,'children',{}).values() if isinstance(getattr(n,'children',None),dict) else []:
            c[type(ch).__name__ if type(ch).__name__!='UnknownElement' else 'Unknown:'+ch.type]+=1
            walk(ch)
    walk(at.main)
    print(tag, dict(c))
summary('landing')
print('landing captions:',[x.value for x in at.caption][:20])
print('sidebar buttons:',[b.label for b in at.sidebar.button])
[b for b in at.button if b.key=='ui_home_card_Descriptive'][0].click().run()
at.selectbox(key="da_assessor").set_value("Panelist").run()
at.selectbox(key="da_product").set_value("Product").run()
at.selectbox(key="da_replicate").set_value("Session").run()
at.number_input(key="da_scale_max").set_value(10).run()
[b for b in at.button if b.key=='da_run_analysis'][0].click().run(timeout=300)
print('exc',at.exception)
for step in range(1,9):
    at.session_state['current_step']=step
    at.run(timeout=300)
    summary(f'step{step}')
    print('  info:',[i.value[:90] for i in at.info])
    print('  warning:',[i.value[:90] for i in at.warning])
