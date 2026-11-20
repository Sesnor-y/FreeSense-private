from streamlit.testing.v1 import AppTest
at=AppTest.from_file('/var/home/Lukas/Projects/RATA-Flow-App/app.py',default_timeout=120).run()
at.selectbox(key='colour_palette_selector').set_value('Colour-blind safe').run()
at.radio(key='ui_export_format').set_value('png').run()
print('before', at.session_state['global_colour_palette'], at.session_state['export_format'])
at.button(key='ui_sb_about').click().run()
print('about open; selector present?', any(s.key=='colour_palette_selector' for s in at.selectbox))
at.button(key='ui_sidebar_readme_back').click().run()
print('after back', at.session_state['global_colour_palette'], at.session_state['export_format'], at.selectbox(key='colour_palette_selector').value)
# methods overlay too
at.button(key='ui_sb_open_methods').click().run(); at.button(key='ui_sidebar_readme_back').click().run()
print('after methods', at.session_state['global_colour_palette'])
