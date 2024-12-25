import datetime
import logging

import pandas as pd


#from calcs.calculate_shifts import calculate_shifts
from calcs.shifts import shift_calc, Order, OrderType
from calcs.detail import Detail
from calcs.tabel_time import TableTime


logger: logging.Logger = logging.getLogger()

def run_calcs(request_id: int,
              input_details: dict[str, tuple[pd.DataFrame, str, tuple[datetime.date, datetime.date]]]) -> None:
 
    table_time: TableTime = TableTime()
    orders: list[tuple[Order, int]] = []
    orders_type: list[OrderType] = []

    input_to_write: dict[str, pd.DataFrame] = {}
    operations_to_write: dict[str, pd.DataFrame] = {}

    details_to_details: dict[str ,str] = {}

    for order_name, vals in input_details.items():
        input_to_write[order_name] = vals[0][["Изделие", "Количество", "Расчитать"]]
        input_to_write[order_name] = input_to_write[order_name].loc[input_to_write[order_name]["Расчитать"]][["Изделие", "Количество"]]

        details: list[Detail] = [Detail(name=row["Изделие"], count=int(row["Количество"])) \
                                 for _, row in input_to_write[order_name].iterrows()]



        tmp_operations: dict[str, pd.DataFrame] = table_time.calc(details=details)

        input_count: dict[str, int] = {}
        for detail in details:
            after: str = detail.name.replace("_", "").replace(".", "").replace("(", "").replace(")", "").replace(" ", "").replace("-", "") + ".xlsx"
            input_count[after] = detail.count

            if after not in details_to_details:
                details_to_details[after] = detail.name.replace("_", " ")

        orders.append((Order(order_name=order_name, operations=tmp_operations, details_count=input_count, date_range=vals[2]), vals[3]))
        orders_type.append(OrderType.from_str(vals[1]))

        operations_to_write[order_name] = pd.concat([value for _, value in tmp_operations.items()]).groupby("Operation").sum().reset_index()

    orders = sorted(orders, key=lambda order: order[1])
    input_to_write["Итог"] = pd.concat([val for _, val in input_to_write.items()]).groupby(by="Изделие").sum().reset_index()
    operations_to_write["Итог"] = pd.concat([val for _, val in operations_to_write.items()]).groupby(by="Operation").sum().reset_index()

    with pd.ExcelWriter(f"./data/results/{request_id}/input.xlsx") as writer:
        for name, df in input_to_write.items():
            df.to_excel(writer, sheet_name=name, index=False)

    shifts, order_readiness = shift_calc.calc(orders=[order for order, _ in orders], order_types=orders_type)
    
    for key in order_readiness:
        order_readiness[key] = order_readiness[key].replace(details_to_details)

    with pd.ExcelWriter(f"./data/results/{request_id}/operations.xlsx") as writer:
        for name, df in operations_to_write.items():
            df.to_excel(writer, sheet_name=name, index=False)

    with pd.ExcelWriter(f"./data/results/{request_id}/shifts.xlsx") as writer:
        for name, df in shifts.items():
            df.to_excel(writer, sheet_name=name, index=False)

    with pd.ExcelWriter(f"./data/results/{request_id}/readiness.xlsx") as writer:
        for name, df in order_readiness.items():
            df.to_excel(writer, sheet_name=name, index=False)

def run_calcs_old(request_id: int,
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

    shifts = shift_calc.calc_old(operations=standart_operations_times, input_count=input_count, date_range=date_range)
    df_operations_times: pd.DataFrame = pd.concat([value for _, value in standart_operations_times.items()]).groupby("Operation").sum().reset_index()
    df_operations_times.to_excel(f"./data/results/{request_id}/operations.xlsx")

    shifts.to_excel(f"./data/results/{request_id}/shifts.xlsx")