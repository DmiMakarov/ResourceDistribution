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

if "calc_result_df" not in st.session_state:
    st.session_state.calc_result_df = None

if "calc_order" not in st.session_state:
    st.session_state.calc_order = None

def get_avaliable_calcs() -> list[str]:
    path: str = "./data/results"

    return sorted([int(file) for file in os.listdir(path) if not file.endswith('.json')], reverse=True)

def get_available_options(order_num: int) -> list[str]:
    with Path("./data/results/orders.json").open("r") as file:
        orders: dict[int, list[str]] = json.loads(file.read())

    answ = orders[str(order_num)]
    answ.append("Показать всё")

    return answ

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
        try:
            os.remove(path=f"{path}/{file}/input.xlsx")
        except OSError:
            pass

        try:
            os.remove(path=f"{path}/{file}/operations.xlsx")
        except OSError:
            pass

        try:
            os.remove(path=f"{path}/{file}/shifts.xlsx")
        except OSError:
            pass
        
        try:
            os.remove(path=f"{path}/{file}/readiness.xlsx")
        except OSError:
            pass
        
        Path.rmdir(f"{path}/{file}")

    with Path("./data/results/dates.json").open("w") as file:
        json.dump({}, file)

    with Path("./data/results/last.json").open("w") as file:
        json.dump([], file)
    
    with Path("./data/results/orders.json").open("w") as file:
        json.dump({}, file)

with st.container():
    st.button(label="Очистить расчёты", on_click=delete_calc)


with st.container():
    st.session_state.calc_result_df = st.selectbox(label="Номер рассчёта",
                                                   options=get_avaliable_calcs(),
                                                   key=st.session_state.calc_result)

with st.container():

    if st.session_state.calc_result_df is not None:
        st.session_state.calc_order = st.selectbox(label="Выберете заказ",
                                                   options=get_available_options(st.session_state.calc_result_df),
                                                   key=st.session_state.calc_result_df)

with st.container():
    if st.session_state.calc_result_df is not None:
        input_: dict[str, pd.DataFrame] = pd.read_excel(f"./data/results/{st.session_state.calc_result_df}/input.xlsx", sheet_name=None)
        operations: dict[str, pd.DataFrame] = pd.read_excel(f"./data/results/{st.session_state.calc_result_df}/operations.xlsx", sheet_name=None)
        shifts: dict[str, pd.DataFrame] = pd.read_excel(f"./data/results/{st.session_state.calc_result_df}/shifts.xlsx", sheet_name=None)
        details_readiness: dict[str, pd.DataFrame] = pd.read_excel(f"./data/results/{st.session_state.calc_result_df}/readiness.xlsx", sheet_name=None)

    if st.session_state.calc_order is not None and st.session_state.calc_result_df is not None:

        with Path("./data/results/dates.json").open("r") as file:
            data_map: dict[int, dict[str, str]] = json.loads(file.read())

        """# Конфигурация расчёта"""

        if st.session_state.calc_order != "Показать всё" and st.session_state.calc_order != "Итог":
            input__ = [st.session_state.calc_order]
        elif st.session_state.calc_order == "Показать всё":
            input__ = list(input_.keys())
        else:
            input__ = []

        for order_name in input__:

            if order_name == "Итог":
                continue

            st.write(f"## Конфигурация заказа {order_name}")
            operations[order_name]['Time'] = np.round(operations[order_name]['Time'], 1)
            
            st.markdown(data_map[str(st.session_state.calc_result_df)][order_name], unsafe_allow_html=True)
            st.dataframe(data=input_[order_name], key=st.session_state.calc_result_df)

            st.write(f"## Количество нормо-часов операций для заказа {order_name}")
            st.dataframe(data=operations[order_name], key=st.session_state.calc_result_df)
            st.download_button(label='Скачать',
                               data=to_excel(operations[order_name]) ,
                               file_name= 'operations.xlsx',
                               key=f"operation_{order_name}")
            st.write(f"## Смены для заказа {order_name}")
            st.dataframe(data=shifts[order_name].style.applymap(color_survived).format(precision=1),
                         key=st.session_state.calc_result_df)
            st.download_button(label='Скачать',
                               data=to_excel(shifts[order_name]) ,
                               file_name= 'shifts.xlsx',
                               key=f"shift_{order_name}")

            st.write(f"## Готовность деталей для заказа {order_name}")
            st.dataframe(data=details_readiness[order_name].style.applymap(color_survived).format(precision=0),
                         key=st.session_state.calc_result_df)
            st.download_button(label='Скачать',
                               data=to_excel(details_readiness[order_name]) ,
                               file_name= 'details_readiness.xlsx',
                               key=f"details_{order_name}")

        if st.session_state.calc_order == "Итог" or st.session_state.calc_order == "Показать всё":

            st.write(f"## Конфигурация заказа")
            operations["Итог"]['Time'] = np.round(operations["Итог"]['Time'], 1)
            st.dataframe(data=input_["Итог"], key=st.session_state.calc_result_df)
        
            st.write("## Суммарное количество нормо-часов операций")
            st.dataframe(data=operations["Итог"], key=st.session_state.calc_result_df)
            st.download_button(label='Скачать',
                               data=to_excel(operations["Итог"]) ,
                               file_name= 'operations.xlsx',
                               key="operation_total")
            st.write("## Итоговые смены")
            st.dataframe(data=shifts["Итог"].style.applymap(color_survived).format(precision=1),
                         key=st.session_state.calc_result_df)
            st.download_button(label='Скачать',
                               data=to_excel(shifts["Итог"]) ,
                               file_name= 'shiftss.xlsx',
                                   key="shift_total")
        
