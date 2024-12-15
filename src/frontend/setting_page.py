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

with st.container():
    edited_df = st.data_editor(get_available_details(),
                               hide_index=True,
                               key=st.session_state.edit_table)

with st.container():

    today: datetime.date = datetime.datetime.now(
            tz=datetime.timezone(datetime.timedelta(hours=3), name='МСК'),
            ).today()

    dates_range: tuple[datetime.date, datetime.date] = st.date_input(
                                                                    "Выберете интервал расчёта",
                                                                    (today, today + relativedelta(months=1)),
                                                                     format="DD.MM.YYYY",
                                                                    )

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
    data_map[num_calc] = f"{dates_range[0].strftime('%d.%m.%Y')} - {dates_range[1].strftime('%d.%m.%Y')}"
    st.write(f"Номер расчёта {num_calc}")

    Path.mkdir(f'./data/results/{num_calc}')

    run_calcs(request_id=num_calc, input_details=edited_df, date_range=dates_range)

    with Path("./data/results/last.json").open("w") as file:
        json.dump(calcs_list, file)

    with Path("./data/results/dates.json").open("w") as file:
        json.dump(data_map, file)

    st.session_state.calc_result += 1
    #st.switch_page("./frontend/result_page.py")

st.button(label="Начать расчёт", on_click=start_calc)
