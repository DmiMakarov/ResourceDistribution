import datetime
import json
import logging
import os
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st
from dateutil.relativedelta import relativedelta

from middleware.run_calcs import run_calcs

logger: logging.Logger = logging.getLogger(__name__)

st.markdown("Загрузка данных")
st.sidebar.markdown("В этом разделе определяются параметры расчёта, такие как: изделия, которые следует произвести, их количество, временной промежуток расчёта.")

if "edit_table" not in st.session_state:
    st.session_state.edit_table = 0

if "num_orders" not in st.session_state:
    st.session_state.num_orders = 0

if "calc_result" not in st.session_state:
    st.session_state.calc_result = 0

def get_available_details() -> pd.DataFrame:
    path: str = "./data/tech_map/"

    def replaces(x: str) -> str:
        return x.replace("Тех_карта_", "").replace(".xlsx", "").replace(".xls", "").replace("_", " ")

    files: list[str] = [replaces(file) for file in os.listdir(path) if  \
                         (file.endswith((".xlsx", ".xls"))) and file.startswith("Тех_карта")]

    data: pd.DataFrame = pd.DataFrame({"Изделие": files})
    data["Количество"] = 1
    data["расчитать"] = True
    #logger.info(st.session_state.edit_table)

    return data

"""
## Технические карты изделий
"""

with st.container():
    uploaded_files = st.file_uploader(label="upload_tech_map", accept_multiple_files=True,
                                      label_visibility="hidden")

    for uploaded_file in uploaded_files:
        #TODO(me): add validation
        #001
        info: str = f"adding uploaded file: {uploaded_file.name}"
        logger.info(info)
        pd.read_excel(BytesIO(uploaded_file.read())).to_excel(f"./data/tech_map/{uploaded_file.name}")

    if len(uploaded_files) > 0:
        st.session_state.edit_table = st.session_state.edit_table + 1

def update_num_orders():
    st.session_state.edit_table = st.session_state.edit_table + 1

with st.container():
    st.session_state.num_orders = st.number_input("Введите количество заказов", value=1, min_value=1)
    
    st.button(label="Применить", on_click=update_num_orders)

def start_calc() -> None:

    with Path("./data/results/last.json").open("r") as file:
        calcs_list: list[int] = json.loads(file.read())

    with Path("./data/results/dates.json").open("r") as file:
        data_map: dict[int, str] = json.loads(file.read())

    if len(calcs_list) > 0:
        num_calc: int = max(calcs_list) + 1
    else:
        num_calc = 0

    for i in range(num_calc, 100000):
        if not os.path.exists(f'./data/results/{i}'):
            num_calc = i
            break

    calcs_list.append(num_calc)
    
    data_map_: dict[str, str] = {}

    for key, val in edited_df.items():
        data_map_[key] = f"{val[2][0].strftime('%d.%m.%Y')}"
        
        if val[2][1] is not None:
            data_map_[key] += f"- {val[2][1].strftime('%d.%m.%Y')}"
    
    data_map[num_calc] = data_map_
    st.write(f"Номер расчёта {num_calc}")

    Path.mkdir(f'./data/results/{num_calc}')

    run_calcs(request_id=num_calc, input_details=edited_df)

    with Path("./data/results/last.json").open("w") as file:
        json.dump(calcs_list, file)

    with Path("./data/results/dates.json").open("w") as file:
        json.dump(data_map, file)

    st.session_state.calc_result += 1
    #st.switch_page("./frontend/result_page.py")

with st.container(key=st.session_state.edit_table):
    details = get_available_details()

    today: datetime.date = datetime.datetime.now(
                                                tz=datetime.timezone(datetime.timedelta(hours=3), name='МСК'),
                                                ).today()
    
    edited_df: dict[str, tuple[pd.DataFrame, str, tuple[datetime.date, datetime.date]]] = {}
    
    for i in range(st.session_state.num_orders):
        name: str = st.text_input("Имя заказа")

        edited_df_ = st.data_editor(details, hide_index=True)

        option = st.selectbox(
                              "Тип расчёта",
                              ("Планирование", "Обратное планирование (день)", "Обратное планирование (день + ночь)"),
                              index=None
                             )

        if option == "Планирование":
            dates_range: tuple[datetime.date, datetime.date] = st.date_input(
                                                                            "Выберете интервал расчёта",
                                                                            (today, today + relativedelta(months=1)),
                                                                             format="DD.MM.YYYY",
                                                                            )
        else:
            date_calc: datetime.date = st.date_input("Дата старта", today)
            dates_range = [date_calc, None]
        
        edited_df[name] = (edited_df_, option, dates_range)
    

#with st.container():
#    edited_df = st.data_editor(get_available_details(),
#                               hide_index=True,
#                               key=st.session_state.edit_table)
#
#    st.button(label="Начать расчёт", on_click=start_calc)
#
#with st.container():
#
#    today: datetime.date = datetime.datetime.now(
#            tz=datetime.timezone(datetime.timedelta(hours=3), name='МСК'),
#            ).today()
#
#    dates_range: tuple[datetime.date, datetime.date] = st.date_input(
#                                                                    "Выберете интервал расчёта",
#                                                                    (today, today + relativedelta(months=1)),
#                                                                     format="DD.MM.YYYY",
#                                                                    )
#

st.button(label="Начать расчёт", on_click=start_calc)
