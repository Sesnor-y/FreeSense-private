from streamlit.testing.v1 import AppTest
at=AppTest.from_file('/var/home/Lukas/Projects/RATA-Flow-App/app.py',default_timeout=120).run()
print([s.value for s in at.main.subheader])
