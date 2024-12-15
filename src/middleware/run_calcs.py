import datetime
import logging

import pandas as pd

#from calcs.calculate_shifts import calculate_shifts
from calcs.shifts import shift_calc
from calcs.detail import Detail
from calcs.tabel_time import TableTime

#logger: logging.Logger = logging.getLogger(__name__)

def run_calcs(request_id: int,
              input_details: pd.DataFrame,
              date_range: tuple[datetime.date, datetime.date]) -> None:
    """Calculate request and write answer to folder"""
    table_time: TableTime = TableTime()

    input_details = input_details[["Изделие", "Количество", "расчитать"]]
    input_details = input_details.loc[input_details["расчитать"]]
    input_details[["Изделие", "Количество"]].to_excel(f"./data/results/{request_id}/input.xlsx")

    details: list[Detail] = [Detail(name=row["Изделие"], count=int(row["Количество"])) \
                             for _, row in input_details.iterrows()]

    standart_operations_times: dict[str, pd.DataFrame] = table_time.calc(details=details)
    #config: pd.DataFrame = pd.read_excel('./data/StaffConfig.xlsx')
    #shifts: pd.DataFrame = calculate_shifts(operation_df=standart_operations_times,
    #                                        config=config,
    #                                        max_days=(date_range[1] - date_range[0]).days)
    input_count: dict[str, int] = {}
    for detail in details:
        input_count[detail.name.replace("_", "").replace(".", "").replace("(", "").replace(")", "").replace(" ", "").replace("-", "") + ".xlsx"] = detail.count

    shifts = shift_calc.calc(operations=standart_operations_times, input_count=input_count, date_range=date_range)
    df_operations_times: pd.DataFrame = pd.concat([value for _, value in standart_operations_times.items()]).groupby("Operation").sum().reset_index()
    df_operations_times.to_excel(f"./data/results/{request_id}/operations.xlsx")
    shifts.to_excel(f"./data/results/{request_id}/shifts.xlsx")