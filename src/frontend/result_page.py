import os

import pandas as pd
import numpy as np
from io import BytesIO
import streamlit as st
from streamlit_javascript import st_javascript

st_theme = st_javascript("""window.getComputedStyle(window.parent.document.getElementsByClassName("stApp")[0]).getPropertyValue("color-scheme")""")
if st_theme == "dark":
    base_color: str = "black"
else:
    base_color: str = "white"

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'})
    worksheet.set_column('A:A', None, format1)
    writer.close()
    processed_data = output.getvalue()

    return processed_data

st.markdown("Рассчёт производственного плана")
st.sidebar.markdown("Результаты рассчётов производственного плана. Результаты включают в себя суммарное количество нормо-часов на операцию и распределение смен по дням")

if "calc_result" not in st.session_state:
    st.session_state.calc_result = 0

def get_avaliable_calcs() -> list[str]:
    path: str = "./data/results"

    return [file for file in os.listdir(path) if not file.endswith('.json')]

def color_survived(val):
    color = base_color
    if val == 'Да':
        color = 'green'
    if val == 'Нет':
        color = 'red'
    return f'background-color: {color}'

with st.container():
    st.session_state.calc_result_df = st.selectbox(label="Номер рассчёта",
                                                   options=get_avaliable_calcs(),
                                                   key=st.session_state.calc_result)

with st.container():
    operations: pd.DataFrame = pd.read_excel(f"./data/results/{st.session_state.calc_result_df}/operations.xlsx").drop(columns=["Unnamed: 0"])
    shifts: pd.DataFrame = pd.read_excel(f"./data/results/{st.session_state.calc_result_df}/shifts.xlsx").drop(columns=["Unnamed: 0"]).style.applymap(color_survived)

    operations['Time'] = np.round(operations['Time'], 1)
    """## Количество нормо-часов операций"""
    st.dataframe(data=operations, key=st.session_state.calc_result_df)
    st.download_button(label='Скачать',
                                data=to_excel(operations) ,
                                file_name= 'operations.xlsx')
    """## Смены"""
    st.dataframe(data=shifts,
                 key=st.session_state.calc_result_df)
    st.download_button(label='Скачать',
                       data=to_excel(shifts) ,
                       file_name= 'shiftss.xlsx')