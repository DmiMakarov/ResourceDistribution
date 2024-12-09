"""Define TechMap reader"""
from __future__ import annotations

import pandas as pd

from calcs.operation import ConveyorOperation, Operation
import logging

logger: logging.Logger = logging.getLogger(__name__)

class TechMap:
    """
    Parse technical map for detail and prepare necessary data
    """
    def __init__(self) -> None:
        self.columns: set[str] = {"Изделие", "Кол-во изделий", "Компонент", "Подразделение", "Кол-во", "Ед. изм.", "Цена", "Сумма", "Поставщик", "Tпз"}
        #TODO(me): move to params
        #002
        self.conveyor_operations: dict[str, dict[str, int]] = {"Окрашивание порошком": [
                                                                                        {
                                                                                            "ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx": 
                                                                                                {
                                                                                                    "minute_per_element": 15, 
                                                                                                    "max_count": 23, 
                                                                                                    "standard_time": 180
                                                                                                }
                                                                                        },
                                                                                        {
                                                                                            "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx": 
                                                                                                {
                                                                                                    "minute_per_element": 15, 
                                                                                                    "max_count": 50, 
                                                                                                    "standard_time": 11 * 50 * 60 / 212
                                                                                                }
                                                                                        }]
                                                                }
        self.name: str | None = None

    def from_excel(self, filepath: str = "../data/tech_map/Тех_карта_ЗМС_ДМГС_6_00_000_02_01_Дверь_тип_6_990х2040_левая.xlsx") -> None:
        data: pd.DataFrame = pd.read_excel(io=filepath)
        data[["Кол-во", "Tпз"]] = data[["Кол-во", "Tпз"]].fillna(0)

        diff_columns: set[str] = self.columns.difference(set(data.columns))

        if len(diff_columns) != 0:
            err: str = f"В технической картe {filepath} отсутсвуют необходимые заголовки: {diff_columns}"
            raise ValueError(err)

        #Skip last None line
        if pd.isna(data.iloc[data.shape[0] - 1]["Изделие"]):
            data = data.iloc[:data.shape[0] - 1, :]

        index_to_split = data[data["Изделие"].str.contains("Работа")].index[0]
        self.detail: pd.DataFrame = data.iloc[1:index_to_split, :]
        self.operations: pd.DataFrame = data.iloc[index_to_split + 1:, :]

        self.name = data.iloc[2]["Изделие"].replace("-", "").replace(" ", "").replace("(", "").replace(")", "").replace("_", "").replace(".", "") + ".xlsx"

    def get_operations(self) -> list[Operation | ConveyorOperation]:
        operations: list[Operation | ConveyorOperation] = []
        current_operation: dict = {}

        for _, operation_row in self.operations.iterrows():

            if pd.isna(operation_row["Компонент"]):
                operation_full_name: str = operation_row["Изделие"]
                current_operation = {"name": operation_full_name[0:operation_full_name.find("Сумма:") - 1]}

                continue

            current_operation["count"] = operation_row["Кол-во"] / operation_row["Кол-во изделий"]
            current_operation["add_time"] = float(operation_row["Tпз"])

            if current_operation["name"] in self.conveyor_operations:
                
                conveyor_params: dict = {}

                for params in self.conveyor_operations[current_operation["name"]]:
                    if self.name in params:
                        conveyor_params = params[self.name]

                if len(conveyor_params) == 0:
                    err: str = f"Not found conveyor params for {self.name}"
                    logger.error(err)
                    raise ValueError(err)
                
                logger.info(current_operation)

                operation: ConveyorOperation = ConveyorOperation(name=current_operation["name"],
                                                                 standard_time=conveyor_params["standard_time"] / 60,
                                                                 tpz=current_operation["add_time"],
                                                                 time_per_element=conveyor_params["minute_per_element"] / 60,
                                                                 max_count=conveyor_params["max_count"])
            else:
                operation: Operation = Operation(name=current_operation["name"],
                                                 standard_time=current_operation["count"],
                                                 tpz=current_operation["add_time"])

            operations.append(operation)

        return operations