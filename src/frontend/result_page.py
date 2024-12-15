import os

import pandas as pd
import numpy as np
from io import BytesIO
import streamlit as st
from streamlit_javascript import st_javascript
from pathlib import Path
import json

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

    return sorted([int(file) for file in os.listdir(path) if not file.endswith('.json')], reverse=True)

def color_survived(val):
    color = base_color

    if isinstance(val, float) | isinstance(val , int):
        if val == 0.0:
            color = 'red'
        else:
            color = 'green'

    return f'background-color: {color}'

def delete_calc():
    path: str = "./data/results"
    files: list[str] = [file for file in os.listdir(path) if not file.endswith('.json')]

    for file in files:
        os.remove(path=f"{path}/{file}/input.xlsx")
        os.remove(path=f"{path}/{file}/operations.xlsx")
        os.remove(path=f"{path}/{file}/shifts.xlsx")
        Path.rmdir(f"{path}/{file}")

    with Path("./data/results/dates.json").open("w") as file:
        json.dump({}, file)

    with Path("./data/results/last.json").open("w") as file:
        json.dump([], file)

with st.container():
    st.button(label="Очистить расчёты", on_click=delete_calc)


with st.container():
    st.session_state.calc_result_df = st.selectbox(label="Номер рассчёта",
                                                   options=get_avaliable_calcs(),
                                                   key=st.session_state.calc_result)

with st.container():
    if st.session_state.calc_result_df is not None:
        input: pd.DataFrame = pd.read_excel(f"./data/results/{st.session_state.calc_result_df}/input.xlsx").drop(columns=["Unnamed: 0"])
        operations: pd.DataFrame = pd.read_excel(f"./data/results/{st.session_state.calc_result_df}/operations.xlsx").drop(columns=["Unnamed: 0"])
        shifts: pd.DataFrame = pd.read_excel(f"./data/results/{st.session_state.calc_result_df}/shifts.xlsx").drop(columns=["Unnamed: 0"])

        with Path("./data/results/dates.json").open("r") as file:
            data_map: dict[int, str] = json.loads(file.read())

        operations['Time'] = np.round(operations['Time'], 1)
        """## Конфигурация расчёта"""
        st.write(data_map[str(st.session_state.calc_result_df)])
        st.dataframe(data=input, key=st.session_state.calc_result_df)

        """## Количество нормо-часов операций"""
        st.dataframe(data=operations, key=st.session_state.calc_result_df)
        st.download_button(label='Скачать',
                                    data=to_excel(operations) ,
                                    file_name= 'operations.xlsx')
        """## Смены"""
        st.dataframe(data=shifts.style.applymap(color_survived).format(precision=1),
                     key=st.session_state.calc_result_df)
        st.download_button(label='Скачать',
                           data=to_excel(shifts) ,
                           file_name= 'shiftss.xlsx')
