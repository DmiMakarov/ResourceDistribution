import streamlit as st
import pandas as pd
import os

st.markdown("Настройка рассчёта")
st.sidebar.markdown("Настройка рассчёта")

def get_available_details() -> pd.DataFrame:
    path: str = './data/tech_map/'
    files: list[str] = []
    for filename in os.listdir(path):
            if (filename.endswith(".xlsx") or filename.endswith(".xls")) and filename.startswith('Тех_карта'): 
                files.append(filename.replace('Тех_карта_', '').replace('.xlsx', '').replace('.xls', '').replace('_', ' '))

    data: pd.DataFrame = pd.DataFrame({'Деталь': files})
    data['Количество'] = 1
    data['Добавить в рассчёт'] = True

    return data
     
edited_df = st.data_editor(get_available_details(), hide_index=True)
