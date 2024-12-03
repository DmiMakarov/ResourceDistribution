"""Calculate table time for input details"""
import os
from typing import TYPE_CHECKING

import pandas as pd

from calcs.detail import Detail
from middleware.tech_map import TechMap

if TYPE_CHECKING:
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

    def calc(self, details: list[Detail]) -> pd.DataFrame:
        self.read_all_tech_maps()

        operations_df: list[pd.DataFrame] = []

        for detail in details:
            detail_name: str = detail.name.replace("_", "").replace(".", "").replace("(", "").replace(")", "").replace(" ", "").replace("-", "") + ".xlsx"

            if detail_name not in self.tech_maps:
                err: str = f"Отсутсвует тех карта для изделия {detail.name}"
                raise ValueError(err)

            operations: list[Operation | ConveyorOperation] = self.tech_maps[detail_name].get_operations()

            operations_name: list[str] = []
            operations_time: list[float] = []

            for operation in operations:
                operations_name.append(operation.name)
                operations_time.append(operation.calc(detail.count))

            operations_df.append(pd.DataFrame({"Operation": operations_name, "Time": operations_time}))

        return pd.concat(operations_df).groupby(by="Operation").sum().reset_index()