"""Calculate table time for input details"""
import os
from typing import TYPE_CHECKING

import pandas as pd

from calcs.detail import Detail
from middleware.tech_map import TechMap

from calcs.operation import ConveyorOperation, Operation


class TableTime:
    """Calculate table time for input details"""
    def __init__(self) -> None:
        self.tech_maps: dict[str, TechMap] = {}
        self.read_all_tech_maps()

    def read_all_tech_maps(self) -> None:
        """Read all tech maps"""
        path: str = "./data/tech_map"

        for filename in os.listdir(path):
            if (filename.endswith((".xlsx", ".xls"))) and filename.startswith("Тех_карта"):
                name: str = filename.replace("_", "").replace("Техкарта", "")
                self.tech_maps[name] = TechMap()
                self.tech_maps[name].from_excel(path + "/" + filename)

    def calc(self, details: list[Detail]) -> dict[str, pd.DataFrame]:
        self.read_all_tech_maps()

        operations_df: dict[str, pd.DataFrame] = {}

        for detail in details:
            detail_name: str = detail.name.replace("_", "").replace(".", "").replace("(", "").replace(")", "").replace(" ", "").replace("-", "") + ".xlsx"

            if detail_name not in self.tech_maps:
                err: str = f"Отсутсвует тех карта для изделия {detail.name}"
                raise ValueError(err)

            operations: list[Operation | ConveyorOperation] = self.tech_maps[detail_name].get_operations()

            operations_name: list[str] = []
            operations_time: list[float] = []

            for operation in operations:
                if isinstance(operation, ConveyorOperation) and operation.name in operations_name:
                    continue

                operations_name.append(operation.name)
                operations_time.append(operation.calc(detail.count))

            df = pd.DataFrame({"Operation": operations_name, "Time": operations_time})

            if detail_name == "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                map_values: dict[str, str] = {
                                                "Зачистная": "Слесарная",
                                                "Зачистная / снять усиление": "Слесарная",
                                                "Лазерная резка трубы": "Вальцовочная",
                                                "Ленточношлифовальная": "Слесарная",
                                                "Сварка вольфрамом в среде защитного газа (TIG)": "Сварка полуавтоматом в среде защитного газа (MIG)",
                                                "Сварочная роботизированная": "Сварка полуавтоматом в среде защитного газа (MIG)",
                                                "Слесарная / зачистить торец после лазер.резки, притупить кромки": "Слесарная"
                                                }

                df = df.rename(map_values)

            operations_df[detail_name] = df.groupby('Operation').sum().reset_index()

        return operations_df