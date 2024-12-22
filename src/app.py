import logging

import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.Logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
#Найстрока расчёта -> загрузка данных, рез
pg = st.navigation([st.Page("./frontend/setting_page.py", title="Загрузка данных", default=True),
                    st.Page("./frontend/result_page.py", title="Расчёт производственного плана")])
pg.run()
logger.info("Start app")