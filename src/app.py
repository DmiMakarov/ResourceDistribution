import logging

import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.Logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

pg = st.navigation([st.Page("./frontend/setting_page.py", title="Настройки рассчётов"),
                    st.Page("./frontend/result_page.py", title="Результаты рассчётов")])
pg.run()
logger.info("Start app")