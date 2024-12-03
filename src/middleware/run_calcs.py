import datetime
import logging

import pandas as pd

from calcs.calculate_shifts import calculate_shifts
from calcs.detail import Detail
from calcs.tabel_time import TableTime

logger: logging.Logger = logging.getLogger(__name__)

def run_calcs(request_id: int,
              input_details: pd.DataFrame,
              date_range: tuple[datetime.date, datetime.date]) -> None:
    """Calculate request and write answer to folder"""
    table_time: TableTime = TableTime()

    input_details = input_details[["Деталь", "Количество", "Рассчитать"]]
    input_details = input_details.loc[input_details["Рассчитать"]]

    details: list[Detail] = [Detail(name=row["Деталь"], count=int(row["Количество"])) \
                             for _, row in input_details.iterrows()]

    standart_operations_times: pd.DataFrame = table_time.calc(details=details)
    config: pd.DataFrame = pd.read_excel('./data/StaffConfig.xlsx')
    shifts: pd.DataFrame = calculate_shifts(operation_df=standart_operations_times,
                                            config=config,
                                            max_days=(date_range[1] - date_range[0]).days)

    standart_operations_times.to_excel(f"./data/results/{request_id}/operations.xlsx")
    shifts.to_excel(f"./data/results/{request_id}/shifts.xlsx")