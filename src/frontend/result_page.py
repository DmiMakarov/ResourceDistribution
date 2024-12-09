import os

import pandas as pd
import numpy as np
import streamlit as st

st.markdown("Результаты расчётов")
st.sidebar.markdown("Результаты рассчётов")

if "calc_result" not in st.session_state:
    st.session_state.calc_result = 0

def get_avaliable_calcs() -> list[str]:
    path: str = "./data/results"

    return [file for file in os.listdir(path) if not file.endswith('.json')]

with st.container():
    st.session_state.calc_result_df = st.selectbox(label="Номер рассчёта",
                                                   options=get_avaliable_calcs(),
                                                   key=st.session_state.calc_result)

with st.container():
    operations: pd.DataFrame = pd.read_excel(f"./data/results/{st.session_state.calc_result_df}/operations.xlsx")
    shifts: pd.DataFrame = pd.read_excel(f"./data/results/{st.session_state.calc_result_df}/shifts.xlsx")

    operations['Time'] = np.round(operations['Time'], 1)
    """## Количество нормо-часов операций"""
    st.dataframe(data=operations.drop(columns=["Unnamed: 0"]), key=st.session_state.calc_result_df)
    """## Смены"""
    st.dataframe(data=shifts.drop(columns=["Unnamed: 0"]), key=st.session_state.calc_result_df)