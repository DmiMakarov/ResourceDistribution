import logging

import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.Logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

pages = [st.Page("./frontend/setting_page.py", title="Загрузка данных", default=True, icon=":material/settings:"),
         st.Page("./frontend/result_page.py", title="Расчёт производственного плана", icon=":material/terminal:")]

current_page = st.navigation(pages=pages, position="hidden")
st.set_page_config(layout="wide")
num_cols = max(len(pages) + 1, 8)
columns = st.columns(num_cols, vertical_alignment="bottom")

columns[0].write("August")

for col, page in zip(columns[1:], pages):
    col.page_link(page, icon=page.icon)

st.title(f"{current_page.icon} {current_page.title}")

current_page.run()

#logger.info("Start app")