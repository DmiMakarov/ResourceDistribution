import logging

import numpy as np
import pandas as pd

logger: logging.Logger = logging.getLogger()

def calculate_shifts(operation_df: pd.DataFrame, config: pd.DataFrame, max_days: int = 30) -> pd.DataFrame:
    """
    Calculate shifts

    operation_df - df of calculated times for operations
    config - config with machines and operations
    """
    merged_times: pd.DataFrame = (config.rename(columns={"Операция" : "Operation"})
                                  .merge(operation_df, on=["Operation"], how="right"))
    unknown_operations: list = merged_times[merged_times["Станок"].isna()]["Operation"].to_list()

    #logger.info(merged_times)
    #logger.info(unknown_operations)

    if len(unknown_operations) > 0:
        merged_times = merged_times.loc[~merged_times.isin(unknown_operations)]
        warn: str = f"Skipped folowing operations: {unknown_operations}. Didnt find them into configs"
        logger.warning(warn)

    merged_times["time_per_machine"] = merged_times["Time"] / merged_times["Количество станков"]
    merged_times = merged_times.loc[np.repeat(merged_times.index, merged_times["Количество станков"])]

    merged_times["num_shifts"] = np.ceil(merged_times["Time"] / 12)
    merged_times["num_max_days"] = np.floor(merged_times["num_shifts"] / max_days)
    merged_times["num_night_shift"] = merged_times["num_max_days"] // 2 * max_days  + (merged_times["num_shifts"] - merged_times["num_max_days"] * max_days) * (merged_times["num_max_days"] % 2)
    merged_times["num_day_shift"] = merged_times["num_shifts"] - merged_times["num_night_shift"]

    return merged_times[["Специалист", "Количество людей", "num_day_shift", "num_night_shift"]]