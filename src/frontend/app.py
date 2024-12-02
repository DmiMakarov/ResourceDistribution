import streamlit as st

pg = st.navigation([st.Page("result_page.py", title="Результаты рассчётов"), st.Page("setting_page.py", title="Настройки рассчётов")])
pg.run()
