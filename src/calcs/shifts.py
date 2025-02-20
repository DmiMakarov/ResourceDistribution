"""
Define ShiftOPeration class

Main idea is to accumulate info about previous operation during one shift
"""
import copy
import tqdm 
import datetime
import itertools

import numpy as np
import pandas as pd


from dataclasses import dataclass
from enum import Enum
#count: int = params["people"]
#prev_operations: dict[str, dict[str, int]] = params["prev_operations"]
#next_operations:dict[str, set[str]]

MAP_OPERATIONS: dict[str, dict] = {
            "Оператор станок с пу/лазер|Лазерная резка листа":
             {
             "machine": 1,
             "people": 1,
             "prev_operations": {"ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {
                                    "Start": 0
                                 },
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {
                                 },
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {
                                    "Start": 0
                                 }
                                 },
             "next_operations": {
                                 "ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {"Оператор станок с пу/гибка|Листогибочная"},
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {},
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {"Оператор станок с пу/гибка|Листогибочная",
                                  "Оператор станок с пу/гибка|Вальцовочная"}
                                }
            },
            "Станочник широкого профиля|Вертикально-фрезерная":
             {"machine": 1,
             "people": 1,
             "prev_operations": {"ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {
                                 },
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {
                                    "Станочник широкого профиля|Токарная": 0
                                 }
                                 },
             "next_operations": {
                                 "ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {},
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {"Оператор окрасочно-сушильной линии и агрегата|Окрашивание порошком"}
                                }
            },
            "Станочник широкого профиля|Токарная":
             {"machine": 1,
             "people": 1,
             "prev_operations": {"ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {
                                 },
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {
                                    "Слесарь по сборке|Ленточно-отрезная": 0
                                 }
                                 },
             "next_operations": {
                                 "ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {},
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {"Станочник широкого профиля|Вертикально-фрезерная"}
                                }
            },
            "Слесарь по сборке|Сборочная":
             {"machine": 5,
             "people": 5,
             "prev_operations": {"ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {
                                    "Оператор окрасочно-сушильной линии и агрегата|Окрашивание порошком": 0
                                 },
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {
                                    "Оператор окрасочно-сушильной линии и агрегата|Окрашивание порошком": 0
                                 },
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {
                                    "Оператор станок с пу/гибка|Листогибочная": 0,
                                    "Слесарь по сборке|Слесарная": 0,
                                    "Эл. Сварщик и п/авт машин|Сварка полуавтоматом в среде защитного газа (MIG)": 0
                                 }

                                 },
             "next_operations": {
                                 "ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {"Слесарь по сборке|Упаковочная"},
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {},
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {"Слесарь по сборке|Упаковочная"}
                                }
            },
            "Слесарь по сборке|Упаковочная":
             {"machine": 2,
             "people": 2,
             "prev_operations": {"ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {
                                    "Слесарь по сборке|Сборочная": 0
                                 },
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {
                                 },
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {
                                    "Слесарь по сборке|Сборочная": 0
                                 }
                                 },
             "next_operations": {
                                 "ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {},
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {},
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {}
                                }
            },
            "Слесарь по сборке|Ленточно-отрезная":
             {"machine": 1,
             "people": 1,
             "prev_operations": {"ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {
                                 },
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {
                                    "Start": 0
                                 },
                                  "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {
                                    "Start": 0
                                 }
                                 },
             "next_operations": {
                                 "ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {},
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {"Станочник широкого профиля|Токарная"},
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {"Эл. Сварщик и п/авт машин|Сварка полуавтоматом в среде защитного газа (MIG)"}
                                }
            },
            "Слесарь по сборке|Слесарная":
             {"machine": 1,
             "people": 1,
             "prev_operations": {"ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {
                                 },
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {
                                 },
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {
                                    "Start": 0
                                 }
                                 },
             "next_operations": {
                                 "ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {},
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {},
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {
                                    "Слесарь по сборке|Сборочная"
                                 }
                                }
            },
            "Эл. Сварщик и п/авт машин|Сварка полуавтоматом в среде защитного газа (MIG)":
             {#4 человека на 1 посту, можно распараллелить на 4 операции
              "machine": 4,
              "people": 4,
              "prev_operations": {"ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {
                                    "Оператор станок с пу/гибка|Листогибочная": 0
                                 },
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {
                                 },
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {"Оператор станок с пу/гибка|Листогибочная": 0,
                                  "Слесарь по сборке|Ленточно-отрезная": 0,
                                  "Оператор станок с пу/гибка|Вальцовочная": 0}
                                 },
             "next_operations": {
                                 "ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {"Оператор окрасочно-сушильной линии и агрегата|Окрашивание порошком"},
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {},
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {"Слесарь по сборке|Сборочная"}
                                }
            },
            "Оператор станок с пу/гибка|Листогибочная":
             {"machine": 1,
             "people": 1,
             "prev_operations": {"ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {
                                    "Оператор станок с пу/лазер|Лазерная резка листа": 0
                                 },
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {
                                 },
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {"Оператор станок с пу/лазер|Лазерная резка листа": 0}
                                 },
             "next_operations": {
                                 "ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {"Эл. Сварщик и п/авт машин|Сварка полуавтоматом в среде защитного газа (MIG)"},
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {},
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {"Слесарь по сборке|Сборочная",
                                  "Эл. Сварщик и п/авт машин|Сварка полуавтоматом в среде защитного газа (MIG)"}
                                }
            },
            "Оператор станок с пу/гибка|Вальцовочная":
             {"machine": 1,
             "people": 1,
             "prev_operations": {"ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {
                                 },
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {
                                 },
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {"Оператор станок с пу/лазер|Лазерная резка листа": 0}
                                 },
             "next_operations": {
                                 "ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {"Слесарь по сборке|Сборочная"},
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {},
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {"Эл. Сварщик и п/авт машин|Сварка полуавтоматом в среде защитного газа (MIG)"}
                                }
            },
            "Оператор окрасочно-сушильной линии и агрегата|Окрашивание порошком":
             {"machine": 1,
             "people": 6,
             "prev_operations": {"ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {
                                    "Эл. Сварщик и п/авт машин|Сварка полуавтоматом в среде защитного газа (MIG)": 0
                                 },
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {
                                    "Станочник широкого профиля|Вертикально-фрезерная": 0
                                 }
                                 },
             "next_operations": {
                                 "ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":
                                 {"Слесарь по сборке|Сборочная"},
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {"Слесарь по сборке|Сборочная"}
                                }
            }
        }

START_OPS: dict[str, list[str]] = {
    "ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx":  ["Оператор станок с пу/лазер|Лазерная резка листа"],
    "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx": ["Слесарь по сборке|Ленточно-отрезная"],
    "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx": ["Оператор станок с пу/лазер|Лазерная резка листа",
                                                             "Слесарь по сборке|Ленточно-отрезная",
                                                             "Слесарь по сборке|Слесарная"]
}

class OrderType(Enum):
    """
    default - сначала посчитать только с дневными, потом с дневными и ночными
    only_day - только дневные без ограничения конечной даты
    with_night - дневные и ночные смены без ограничения конечных дат
    """
    DEFAULT=0
    ONLY_DAY=1
    WITH_NIGHT=2
    REVERSE_ONLY_DAY=3
    REVERSE_WITH_NIGHT=4

    "Планирование", "Обратное планирование (день)", "Обратное планирование (день + ночь)"

    @classmethod
    def from_str(cls, val: str):
        if val == "Планирование":
            return cls.DEFAULT
        elif val == "Прямое планирование (день)":
            return cls.ONLY_DAY
        elif val == "Прямое планирование (день + ночь)":
            return cls.WITH_NIGHT
        elif val == "Обратное планирование (день)":
            return cls.REVERSE_ONLY_DAY
        elif val == "Обратное планирование (день + ночь)":
            return cls.REVERSE_WITH_NIGHT
        else:
            raise ValueError("Неизвестный тип заказов")

@dataclass
class Order:

    order_name: str
    operations: dict[str, pd.DataFrame]
    details_count: dict[str, int]
    date_range: tuple[datetime.date, datetime.date | None]

    def __hash__(self):
        return hash(self.order_name)


class ShiftOperation:

    def __init__(self,
                 count: int,
                 operation_name: str,
                 detail_per_hour: dict[str, float],
                 prev_operations: dict[str, int],
                 next_operations: set[str],
                 ) -> None:
        self.count: int = count
        self.operation_name: str = operation_name
        self.detail_per_hour: dict[str, float] = detail_per_hour
        #for parallel operations

        self.prev_operations: dict[str, dict[str, int]] = prev_operations
        self.next_operations: dict[str, set[str]] = next_operations

        #Day - false, Night - True
        self.fill_dates: list[tuple[datetime.date, bool, float]] = []
        self.tmp_fill_dates: list[tuple[datetime.date, bool, float]] = []
        self.orders_fill_dates: dict[str, list[tuple[datetime.date, bool, float]]] = {}

    @classmethod
    def from_dict(cls,
                  operation_name: str,
                  params: dict) -> 'ShiftOperation':
        count: int = params["people"]
        prev_operations: dict[str, dict[str, int]] = params["prev_operations"]
        next_operations: dict[str, set[str]] = params["next_operations"]

        return cls(
                    count=count,
                    operation_name=operation_name,
                    detail_per_hour={},
                    prev_operations=prev_operations,
                    next_operations=next_operations
                  )

    #кладём все смены в один массив
    # последовательно так, чтобы
    #все смены, которые входят в эту смену, были до
    #плюс считаем, что билдер определяет, может ли начаться операция в текущий день, или уже в следующий
    #правило определения, попадает ли смена в этот день или уже в следующий:
    #предыдущая смену успела сделать столько, чтобы набралось работы на 12/24 часа
    #Короче, на вход дата, смотрит в prev_operations, если набирается деталей на полные сутки/смену, то работаем, иначе не работаем
    #а что делать, когда последние итерации? (то есть когда недостаточно)
    #Прокинуть сигнал, что пусто
    #prev_empty = prev_empty  & prev_empty
    #TODO расширить prev_empty до словаря (надо ли)
    def next(self,
             date: datetime.date,
             is_night: bool,
             prev_empty: bool,
             detail_name: str,
             order_name: str) -> tuple[int, bool]:

        min_available_details: int = min([value for _, value in  self.prev_operations[detail_name].items()])

        if not prev_empty:

            if min_available_details / self.detail_per_hour[detail_name] < 11:
                return 0, False

            is_enough: bool = True

            for op_name in self.prev_operations[detail_name]:
                if op_name == "Start":
                    prev_empty = True
                    break
                # если требуемое количество деталей для 12 делается меньше,
                # чем за 6 часов, то надо запускать
                #единственное, надо как-то подвязаться к количеству деталей

                if self.detail_per_hour[detail_name] * 11 > NAME_TO_OP[op_name].detail_per_hour[detail_name] * 6 \
                   and self.prev_operations[detail_name][op_name] <= NAME_TO_OP[op_name].detail_per_hour[detail_name] * 11:
                    is_enough = False
                    break

            if not is_enough:
                return 0, False

        day_available: bool = not is_night
        night_available: bool = is_night
        hours_available: float = 11
        idx_date: int = -1

        for i, val in enumerate(self.tmp_fill_dates):
            dt, is_night_, count = val

            if dt == date:
                if is_night_ and is_night:

                    hours_available = 11 - count

                    if hours_available < self.detail_per_hour[detail_name]:
                        night_available = False
                    else:
                        idx_date = i

                if (not is_night) and (not is_night_):

                    hours_available = 11 - count

                    if hours_available < self.detail_per_hour[detail_name]:
                        day_available = False
                    else:
                        idx_date = i

        if not day_available and not night_available:
            return 0, False

        details_in_this_date: int = int(min([self.detail_per_hour[detail_name] * 11 * (day_available + night_available),
                                             min_available_details, hours_available * self.detail_per_hour[detail_name]]))
        if details_in_this_date > 0:

            if idx_date == -1:
                self.tmp_fill_dates.append((date, is_night,
                                            details_in_this_date / self.detail_per_hour[detail_name]))
            else:
                val: tuple = self.tmp_fill_dates.pop(idx_date)
                tmp_val: tuple = (val[0], val[1], val[2] + details_in_this_date / self.detail_per_hour[detail_name])
                self.tmp_fill_dates.append(tmp_val)

            if order_name not in self.orders_fill_dates:
                self.orders_fill_dates[order_name] = [(date, is_night, details_in_this_date / self.detail_per_hour[detail_name])]
            else:
                self.orders_fill_dates[order_name].append((date, is_night, details_in_this_date / self.detail_per_hour[detail_name]))

        #по идее с нескольких источников должно заполняться равномерн, то есть ноль тогда, когда везде ноль
        for op in self.prev_operations[detail_name]:
            self.prev_operations[detail_name][op] -= details_in_this_date

            prev_empty = prev_empty and (self.prev_operations[detail_name][op] == 0)

        return details_in_this_date, prev_empty

    #the same as prev, but uniformly distribute
    def next_revert(self,
                    date: datetime.date,
                    is_night: bool,
                    prev_empty: dict[str, bool],
                    detail_name: str,
                    orders_night: set[str]) -> tuple[dict[str, bool], bool]:

        #min_available_details: int = min([value for _, value in  self.prev_operations[detail_name].items()])
        #тут теперь у нас должен быть prev_ops = {"detail": {}"prev_op": {"order": count}}}
        #то есть надо проссумировать
        count_per_ops = np.zeros(len(self.prev_operations[detail_name]))
        i = 0
        #val: {"order": count}
        orders_to_count_prev: list[str] = []
        for _, val in self.prev_operations[detail_name].items():
            if is_night:
                count_per_ops[i] = sum([value for order, value in val.items() if order in orders_night])
                for order in val:
                    if val[order] > 0 and order in orders_night and prev_empty[order]:
                        orders_to_count_prev.append(order)
            else:
                count_per_ops[i] = sum(val.values())
                for order in val:
                    if val[order] > 0: #TODO надо добавить то, что учитывает ещё Prev_empty, но это слишком много
                        orders_to_count_prev.append(order)

            i += 1
        #две идентичные ситуаци
        #1. Заказ B prev_empty True, готов делать упаковочную, A не готов, ждём B
        #2. Заказ 
        #if len(orders_to_count_prev) == 0:
        #    for _, val in self.prev_operations[detail_name].items():
        #        for order in val:
        #            if val[order] > 0:
        #                orders_to_count_prev.append(order)

        

        min_available_details = np.min(count_per_ops)

        total_prev_empty: bool = False

        for order in orders_to_count_prev:
            total_prev_empty = True
            if not prev_empty[order]:
                total_prev_empty = False
                break

        if not total_prev_empty:

            if min_available_details / self.detail_per_hour[detail_name] < 11:
                op: str = list(self.prev_operations[detail_name])[0]
                orders: dict[str, int] =  copy.deepcopy(self.prev_operations[detail_name][op])

                for order in orders:
                    orders[order] = 0

                for name in orders_to_count_prev:
                    prev_empty[name] = False

                return orders, prev_empty

            is_enough: bool = True

            for op_name in self.prev_operations[detail_name]:
                if op_name == "Start":

                    for order in prev_empty:
                        prev_empty[order] = True
                    break
                # если требуемое количество деталей для 12 делается меньше,
                # чем за 6 часов, то надо запускать
                #единственное, надо как-то подвязаться к количеству деталей

                if self.detail_per_hour[detail_name] * 11 > NAME_TO_OP[op_name].detail_per_hour[detail_name] * 6 \
                   and sum(self.prev_operations[detail_name][op_name].values()) <= NAME_TO_OP[op_name].detail_per_hour[detail_name] * 11:
                    is_enough = False
                    break

            if not is_enough:
                op: str = list(self.prev_operations[detail_name])[0]
                orders: dict[str, int] =  copy.deepcopy(self.prev_operations[detail_name][op])

                for order in orders:
                    orders[order] = 0

                for name in orders_to_count_prev:
                    prev_empty[name] = False

                return orders, prev_empty

        day_available: bool = not is_night
        night_available: bool = is_night
        hours_available: float = 11
        idx_date: int = -1

        for i, val in enumerate(self.tmp_fill_dates):
            dt, is_night_, count = val

            if dt == date:
                if is_night_ and is_night:

                    hours_available = 11 - count

                    if hours_available < self.detail_per_hour[detail_name]:
                        night_available = False
                    else:
                        idx_date = i

                if (not is_night) and (not is_night_):

                    hours_available = 11 - count

                    if hours_available < self.detail_per_hour[detail_name]:
                        day_available = False
                    else:
                        idx_date = i

        if not day_available and not night_available:
            op: str = list(self.prev_operations[detail_name])[0]
            orders: dict[str, int] =  copy.deepcopy(self.prev_operations[detail_name][op])

            for order in orders:
                orders[order] = 0

            for name in orders_to_count_prev:
                    prev_empty[name] = False

            return orders, prev_empty

        details_in_this_date: int = int(min([self.detail_per_hour[detail_name] * 11 * (day_available + night_available),
                                            min_available_details, hours_available * self.detail_per_hour[detail_name]]))
        if details_in_this_date > 0:

            if idx_date == -1:
                self.tmp_fill_dates.append((date, is_night,
                                            details_in_this_date / self.detail_per_hour[detail_name]))
            else:
                val: tuple = self.tmp_fill_dates.pop(idx_date)
                tmp_val: tuple = (val[0], val[1], val[2] + details_in_this_date / self.detail_per_hour[detail_name])
                self.tmp_fill_dates.append(tmp_val)

        #по идее с нескольких источников должно заполняться равномерн, то есть ноль тогда, когда везде ноль

        op: str = list(self.prev_operations[detail_name])[0]
        orders: dict[str, int] =  self.prev_operations[detail_name][op]
        ordered_orders = dict(sorted(orders.items(), key=lambda item: item[1]))
        len_ = len(ordered_orders)
        available_details = details_in_this_date

        for order, count in ordered_orders.items():
            if is_night and order not in orders_night:
                len_ -= 1
                continue

            used = min(count, np.ceil(available_details / len_))

            if order not in self.orders_fill_dates:
                self.orders_fill_dates[order] = [(date, is_night, used / self.detail_per_hour[detail_name])]
            else:
                self.orders_fill_dates[order].append((date, is_night, used / self.detail_per_hour[detail_name]))

            ordered_orders[order] -= used
            available_details -= used
            len_ -= 1

        details_in_this_date_answ: dict[str, int] = {}

        for key, val in ordered_orders.items():
            details_in_this_date_answ[key] = orders[key] - ordered_orders[key]

        for op in self.prev_operations[detail_name]:
            self.prev_operations[detail_name][op] = copy.deepcopy(ordered_orders)

        is_empty: dict[str, bool] = {name: True for name in prev_empty}

        for _, orders in self.prev_operations[detail_name].items():

            for order, count in orders.items():
                if count > 0:
                    is_empty[order] = False
                    break

        for name in prev_empty:
            prev_empty[name] = prev_empty[name] and is_empty[name]

        return details_in_this_date_answ, prev_empty

    def clear(self)-> None:
        """Используется, чтобы очистить результаты всех расчётов"""
        for detail in self.prev_operations:
            for prev_operation in self.prev_operations[detail]:
                self.prev_operations[detail][prev_operation] = 0

        self.fill_dates = []
        self.tmp_fill_dates = []
        self.detail_per_hour = {}
        self.orders_fill_dates = {}

    def clear_prev_operations(self) -> None:
        """Не имеет смысла, потому что всегда используется с clean_order"""
        for detail in self.prev_operations:
            for prev_operation in self.prev_operations[detail]:
                self.prev_operations[detail][prev_operation] = 0

        self.detail_per_hour = {}

    def clean_order(self, order_name: str) -> None:
        """Очищает информацию о заказе. Вызывается перед перерасчётом заказа"""
        self.tmp_fill_dates = []
        self.orders_fill_dates[order_name] = []
        #start -> 0
        #details_per_hour -> 0
        for detail in self.prev_operations:
            for prev_operation in self.prev_operations[detail]:
                self.prev_operations[detail][prev_operation] = 0

        self.detail_per_hour = {}

    def approve_order(self) -> None:
        """Подтверждает заказ"""
        if len(self.tmp_fill_dates) > 0:
            self.fill_dates = copy.deepcopy(self.tmp_fill_dates)

        self.tmp_fill_dates = []

        for detail in self.prev_operations:
            for prev_operation in self.prev_operations[detail]:
                self.prev_operations[detail][prev_operation] = 0

        self.detail_per_hour = {}

    def start_order(self) -> None:
        self.tmp_fill_dates = copy.deepcopy(self.fill_dates)

#что мне теперь надо для вычислений
#1. Составить конфигурации всех деталей
#2. Заполнить detail_per_hour (идеально по конфигу, но пофиг, пока так сделаем) - done
#3. Написать цикл вычислений
#4. Собрать в одну таблицу

class ShiftCalc:
    def __init__(self,
                 shifts: dict[str, list[ShiftOperation]]) -> None:
        self.shifts: dict[str, list[ShiftOperation]] = shifts

    def _order_calc(self,
                    order: Order,
                    order_type: OrderType) -> tuple[bool, dict, datetime.date]:
        """
        А теперь вопрос - если мы храним текущие данные, то как делать, если не помещается?
        быстрое решение - сделать tmp_fill_date
        """
        details_readiness: dict = {}

        is_fill: dict[str, bool] = {}

        details_to_compute: list[str] = list(order.operations.keys())

        for detail in details_to_compute:
            is_fill[detail] = False
            details_readiness[detail] = []

        self.__fill_operations(operations=order.operations, input_count=order.details_count, details=details_to_compute)
        self.__fill_start(details_count=order.details_count)

        current_date: datetime.date =  copy.deepcopy(order.date_range[0])
        is_night: bool = False
        is_full: bool = False

        while current_date <= order.date_range[1] and not is_full:

            for detail in details_to_compute:

                if is_fill[detail]:
                    continue

                prev_empty: bool = True

                for i, operation in enumerate(self.shifts[detail]):
                    count, prev_empty = operation.next(date=current_date, is_night=is_night,
                                                       prev_empty=prev_empty, detail_name=detail,
                                                       order_name=order.order_name)
                    next_names: set[str] = operation.next_operations[detail]

                    cond: bool = (count > 0) and len(next_names) == 0 and operation.operation_name != "Слесарь по сборке|Упаковочная"
                    cond = cond or (len(next_names) == 1 and next(iter(next_names)) == "Слесарь по сборке|Упаковочная")

                    if cond:
                        details_readiness[detail].append((current_date, is_night, count))

                    for op_name in next_names:
                        for j in range(i + 1, len(self.shifts[detail])):
                            if self.shifts[detail][j].operation_name == op_name:
                                self.shifts[detail][j].prev_operations[detail][operation.operation_name] += count

                if prev_empty:
                    is_fill[detail] = True

            is_full = True
            for _, val in is_fill.items():
                is_full = is_full and val

            if order_type == OrderType.WITH_NIGHT or order_type == OrderType.REVERSE_WITH_NIGHT:
                if is_night:
                    current_date += datetime.timedelta(days=1)

                is_night = not is_night
            else:
                current_date += datetime.timedelta(days=1)

        if not is_night:
            current_date -= datetime.timedelta(days=1)

        return is_full, details_readiness, current_date

    def _reverse_order(self,
                       order: Order,
                       order_type: OrderType) -> pd.DataFrame:
        #мне нравится идея с бинпоиском точки старта
        #верхняя граница - точка старта
        #нижняя граница должна быть не слишком далёкой, но достаточно далёкой, чтобы можно было точно сказать, что ответ между
        #предлагаю ввести коэффициенты - на каждый подшипник 0.5 дняб на каждую дверь и кормушку 1.5 дня

        count_map: dict[str, float] = {
            "ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx": 1.5,
            "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx": 0.5,
            "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx": 1.5
        }

        order_details: set = set(order.details_count.keys())
        days: int = np.ceil(sum([val * order.details_count[key] for key, val in count_map.items()]))
        date_end: datetime.date = order.date_range[1]
        start_date_bs: datetime.date = date_end - datetime.timedelta(days=days)

        #while True:
        #    mid_date: datetime.date = start_date_bs + (end_date_bs - start_date_bs)/2
        long_date_end: datetime.date = date_end + datetime.timedelta(days=365*12)
        order.date_range = (start_date_bs, long_date_end)
        _, details_readiness, end_date_calc = self._order_calc(order=order, order_type=order_type)
        delta_days = (end_date_calc - date_end).days

        if delta_days != 0:
            self._clean_order(order_name=order.order_name)
            #self._clear_prev_operations()
            self._start_order(details=order_details)

            start_date_bs -= datetime.timedelta(days=delta_days)
            order.date_range = (start_date_bs, long_date_end)
            _, details_readiness, end_date_calc = self._order_calc(order=order, order_type=order_type)
            delta_days = (end_date_calc - date_end).days
            sign: bool = delta_days > 0

            while True:

                if delta_days > 0:
                    start_date_bs -= datetime.timedelta(days=1)
                elif delta_days < 0:
                    start_date_bs += datetime.timedelta(days=1)
                else:
                    break

                self._clean_order(order_name=order.order_name)
                #self._clear_prev_operations()
                self._start_order(details=order_details)
                order.date_range = (start_date_bs, long_date_end)
                _, details_readiness, end_date_calc = self._order_calc(order=order, order_type=order_type)
                delta_days = (end_date_calc - date_end).days

                new_sign: bool = delta_days > 0

                if new_sign != sign:
                    if sign or delta_days == 0:
                        break
                    else:
                        self._clean_order(order_name=order.order_name)
                        #self._clear_prev_operations()
                        order.date_range = (start_date_bs - datetime.timedelta(days=1), long_date_end)
                        _, details_readiness, end_date_calc = self._order_calc(order=order, order_type=order_type)
                        break

            order.date_range = (start_date_bs - datetime.timedelta(days=days), date_end)

        return details_readiness
    
    def __set_start_to_empty_dict(self, details: set[str]):
        for detail in details:
            if "Start" in self.shifts[detail][0].prev_operations[detail]:
                self.shifts[detail][0].prev_operations[detail]["Start"] = {}

    def backet_calc(self,
                    orders: list[Order],
                    order_types: list[OrderType]) -> tuple[dict[str, pd.DataFrame],
                                                    dict[str, pd.DataFrame]]:
        start_index: int = -1
        last_index: int  = -1
        start_dates: list[list[datetime.date]] = []
        end_dates: list[datetime.date] = []

        count_map: dict[str, float] = {
            "ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx": 0.8,
            "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx": 0.2,
            "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx": 1.5
        }

        all_details: set[str] = set()


        #12.26 02-18
        #2 закказа по 20 дверей + кормушки
        #

        for order in orders:
            for detail_ in order.details_count:
                all_details.add(detail_)

        for i, order_type in enumerate(order_types):
            if order_type == OrderType.REVERSE_ONLY_DAY or order_type == OrderType.REVERSE_WITH_NIGHT:

                if start_index == -1:
                    start_index = i

                last_index = i + 1
                days_before: int = np.ceil(sum([val * orders[i].details_count[key] for key, val in count_map.items() if key in orders[i].details_count])) * len(orders)
                start_dates.append([orders[i].date_range[1] - datetime.timedelta(days=days_before - j) for j in range(int(days_before))])
                end_dates.append(orders[i].date_range[1])
            else:
                start_dates.append([orders[i].date_range[0]])
                end_dates.append(orders[i].date_range[1])

        if last_index == -1:
            start_index = 0
            last_index = 0

        start_dates = start_dates[start_index:last_index]
        end_dates = end_dates[start_index:last_index]

        backet_order: list[Order] = orders[start_index:last_index]
        non_backet_before: list[Order] = orders[:start_index]
        non_backet_after = orders[last_index:]

        nights_orders: set[str] = set([order.order_name for i, order in enumerate(orders) if order_types[i] == OrderType.REVERSE_WITH_NIGHT or order_types[i] == OrderType.WITH_NIGHT])

        answ: dict[str, pd.DataFrame] = {}
        details_readiness: dict[str, pd.DataFrame] = {}

        if len(non_backet_before) > 0:
            answ, details_readiness = self.calc(orders=non_backet_before,
                                                order_types=order_types[:start_index],
                                                answ=answ,
                                                details_readiness=details_readiness,
                                                clean_all=False)

        #Для расчёта таким способом надо при current_date == start_date производить инициализацию start_pos
        #а дальше расчёт как обычно
        #внешний цикл - перебор вариантов (for dates in product(*start_dates))
        #второй цикл по дням
        #третий цикл внутри по проверке кого в этот день вставлять
        #Как тогда в таком варианте сделать учёт day\night в случае интервала? пока я бы убрал, потому что такого требования не было
        #А так просто надо добавить, что если count < required and current_date > end_date, то запустить цикл по дням заного

        #какие вообще тут есть циклы
        #1. Цикл по наборам дат (перебор)
        #2. Цикл по дате
        #3. Цикл по заказам
        #4. Цикл по детялям

        #вложенность циклов:
        #1. Цикл по наборам дат (перебор)
        #2. Цикл по дате
        #3. Цикл по деталям
        #Цикл по заказам неявно учтём в вычислении next для shift
        #Что делать с деталями? Наверное, стоит оставить приоритет исполнения одной детали.
        #С точки зрения производства - это самое логичное, потому что сначала работник будет делать однообразную работу. Get it?

        #Нам ещё из этого цикла надо понять, когда какой заказ закончился
        #В next мы можем выкидывать не просто quajtity, Но {"order": quantity}
        # Будет словарь {order: {detail: quantity}}, от которого будет браться информация о
        # Надо посмотреть, хешбл ли пандасовский timestamp, if yes, then i need to construct
        # dict {data: order} and then i can insert details from previous dict

        #Чтобы начать новый расчёт надо:
        #1. Скопировать все операции в tmp (ну и всё)

        # потом надо придумать, как закончить (надо будет почистить tmp, потому что потом буду всё с нуля)

        orders_count: dict[str, dict[str, int]] = {}
        details: set[str] = set()

        for order in backet_order:
            orders_count[order.order_name] = order
            details.update(order.details_count.keys())

        current_end_dates: list[datetime.date] = [datetime.date(year=1974, day=27, month=2)] * len(end_dates)
        backet_order_idxs: dict[str, int] = {order.order_name: i for i, order in enumerate(backet_order)}
        min_delta = 10000000
        min_dates: list[datetime.date] = []

        #получается, нужно делать по ночным
        print(len(list(tqdm.tqdm(itertools.product(*start_dates)))))
        for first_dates in tqdm.tqdm(itertools.product(*start_dates)):

            if len(first_dates) == 0:
                continue

            current_date = min(first_dates)
            is_night = False
            dates_order: dict[datetime.date, list[str]] = {}
            #{val: backet_order[i].order_name for i, val in enumerate(first_dates)}

            for i, val in enumerate(first_dates):
                if val in dates_order:
                    dates_order[val].append(backet_order[i].order_name)
                else:
                    dates_order[val] = [backet_order[i].order_name]

            current_orders_count: dict[str, dict[str, int]] = {order.order_name: copy.deepcopy(order.details_count) for order in backet_order}

            self._start_order(details=None)
            is_overfill: bool = False
            count_empty : int = 0

            is_fill: dict[str, bool] = {}

            for detail in details:
                is_fill[detail] = False

            self.__set_start_to_empty_dict(details=details)
            details_started: set[str] = set()
            while True:
                if current_date in dates_order:
                    for order_name in dates_order[current_date]:
                        details_to_compute = list(orders_count[order_name].details_count.keys())
                        self.__fill_operations(operations=orders_count[order_name].operations,
                                               input_count=orders_count[order_name].details_count,
                                               details=details_to_compute)
                        details_started.update(orders_count[order_name].details_count.keys())
                        self.__fill_start(details_count=orders_count[order_name].details_count, order_name=order_name)

                    del dates_order[current_date]
                    ##default cycle to push forward operations

                #что делать:
                #пройти по всем деталям
                #для всех деталей протолкнуть вперёд
                #если конец - вычесть из счётчика current_orders_count
                #проверить, пустой ли заказ. Если пустой, записать дату, как дату окончания
                #если все пустые, тогда остановить, посчитать разницу.
                #Если все нули - остановить все циклы, записать как решение
                #Если есть хоть одно превышение, то следующий вариант
                #Иначе смотрим метрику сумма модулей разностей
                for detail in details_started:
                    #TODO:продумать, как скипать детали посчитанные
                    prev_empty: dict[str, bool] = {order.order_name: True for order in backet_order}

                    for i, operation in enumerate(self.shifts[detail]):
                        order_count, prev_empty = operation.next_revert(date=current_date, is_night=is_night,
                                                                        prev_empty=prev_empty, detail_name=detail,
                                                                        orders_night=nights_orders)


                        next_names: set[str] = operation.next_operations[detail]

                        #cond: bool = (count > 0) and len(next_names) == 0 and operation.operation_name != "Слесарь по сборке|Упаковочная"

                        if len(next_names) == 0:
                            for order in order_count:
                                if order in current_orders_count:
                                    current_orders_count[order][detail] -= order_count[order]

                        for op_name in next_names:
                            for j in range(i + 1, len(self.shifts[detail])):
                                if self.shifts[detail][j].operation_name == op_name:
                                    for order in order_count:
                                        if isinstance(self.shifts[detail][j].prev_operations[detail][operation.operation_name], int):
                                            self.shifts[detail][j].prev_operations[detail][operation.operation_name] = {order: order_count[order]}
                                        else:
                                            if order in self.shifts[detail][j].prev_operations[detail][operation.operation_name]:
                                                self.shifts[detail][j].prev_operations[detail][operation.operation_name][order] += order_count[order]
                                            else:
                                                self.shifts[detail][j].prev_operations[detail][operation.operation_name][order] = order_count[order]

                    #if prev_empty:
                    #    is_fill[detail] = True

                #проверка заказа на пустоту:
                orders_to_delete: set[str] = set()

                for order, details_count in current_orders_count.items():
                    count_ = sum([count_detail for _, count_detail in details_count.items()])

                    if count_ == 0:
                        current_end_dates[backet_order_idxs[order]] = current_date
                        orders_to_delete.update(order)
                        count_empty += 1

                        if end_dates[backet_order_idxs[order]] is not None and (current_date - end_dates[backet_order_idxs[order]]).days > 0:
                            is_overfill = True

                if is_overfill:
                    break

                for order in orders_to_delete:
                    del current_orders_count[order]

                if count_empty == len(current_end_dates):
                    break

                if len(nights_orders) > 0:
                    is_night = not is_night

                    if not is_night:
                        current_date += datetime.timedelta(days=1)

                else:
                    current_date += datetime.timedelta(days=1)

            for order_name in backet_order_idxs:
                self._clean_order(order_name=order_name)

            if is_overfill:
                continue

            norm: int = sum([abs((current_end_dates[i] - end_dates[i]).days) for i in range(len(current_end_dates)) if end_dates[i] is not None])

            if norm == 0:
                min_delta = norm
                min_dates = copy.deepcopy(first_dates)
                break

            if norm <= min_delta:
                min_delta = norm
                min_dates = copy.deepcopy(first_dates)

        #TODO start reverse calc with min_dates
        if len(backet_order) > 0:
            backet_details_readiness: dict[str, dict[str, tuple]] = {}

            current_date = min(min_dates)
            is_night = False
            dates_order: dict[datetime.date, list[str]] = {}

            for i, val in enumerate(min_dates):
                if val in dates_order:
                    dates_order[val].append(backet_order[i].order_name)
                else:
                    dates_order[val] = [backet_order[i].order_name]

            current_orders_count: dict[str, dict[str, int]] = {order.order_name: copy.deepcopy(order.details_count) for order in backet_order}

            self._start_order(details=None)
            is_overfill: bool = False
            count_empty : int = 0

            is_fill: dict[str, bool] = {}

            for detail in details:
                is_fill[detail] = False

            self.__set_start_to_empty_dict(details=details)
            details_started: set[str] = set()

            while True:
                if current_date in dates_order:
                    for order_name in dates_order[current_date]:
                        details_to_compute = list(orders_count[order_name].details_count.keys())
                        self.__fill_operations(operations=orders_count[order_name].operations,
                                               input_count=orders_count[order_name].details_count,
                                               details=details_to_compute)
                        details_started.update(orders_count[order_name].details_count.keys())
                        self.__fill_start(details_count=orders_count[order_name].details_count, order_name=order_name)

                    del dates_order[current_date]
                        ##default cycle to push forward operations

                #что делать:
                #пройти по всем деталям
                #для всех деталей протолкнуть вперёд
                #если конец - вычесть из счётчика current_orders_count
                #проверить, пустой ли заказ. Если пустой, записать дату, как дату окончания
                #если все пустые, тогда остановить, посчитать разницу.
                #Если все нули - остановить все циклы, записать как решение
                #Если есть хоть одно превышение, то следующий вариант
                #Иначе смотрим метрику сумма модулей разностей
                for detail in details_started:

                    prev_empty: dict[str, bool] = {name: True for name in current_orders_count}

                    for i, operation in enumerate(self.shifts[detail]):
                        order_count, prev_empty = operation.next_revert(date=current_date, is_night=is_night,
                                                                        prev_empty=prev_empty, detail_name=detail,
                                                                        orders_night=nights_orders)


                        next_names: set[str] = operation.next_operations[detail]

                        if len(next_names) == 0:
                            for order in order_count:
                                if order in current_orders_count:
                                    current_orders_count[order][detail] -= order_count[order]
                        #cond: bool = (count > 0) and len(next_names) == 0 and operation.operation_name != "Слесарь по сборке|Упаковочная"
                        cond = (len(next_names) == 0) and ( operation.operation_name != "Слесарь по сборке|Упаковочная")
                        cond = cond or (len(next_names) == 1 and next(iter(next_names)) == "Слесарь по сборке|Упаковочная")

                        if cond:
                            for order in order_count:
                                if order_count[order] > 0:
                                    if order in backet_details_readiness:
                                        if detail in backet_details_readiness[order]:
                                            backet_details_readiness[order][detail].append((current_date, is_night, order_count[order]))
                                        else:
                                            backet_details_readiness[order][detail] = [(current_date, is_night, order_count[order])]
                                    else:
                                        backet_details_readiness[order] = {detail: [(current_date, is_night, order_count[order])]}

                        for op_name in next_names:
                            for j in range(i + 1, len(self.shifts[detail])):
                                if self.shifts[detail][j].operation_name == op_name:
                                    for order in order_count:
                                        if isinstance(self.shifts[detail][j].prev_operations[detail][operation.operation_name], int):
                                            self.shifts[detail][j].prev_operations[detail][operation.operation_name] = {order: order_count[order]}
                                        else:
                                            if order in self.shifts[detail][j].prev_operations[detail][operation.operation_name]:
                                                self.shifts[detail][j].prev_operations[detail][operation.operation_name][order] += order_count[order]
                                            else:
                                                self.shifts[detail][j].prev_operations[detail][operation.operation_name][order] = order_count[order]

                    #if prev_empty:
                    #    is_fill[detail] = True

                #проверка заказа на пустоту:
                orders_to_delete: set[str] = set()

                for order, details_count in current_orders_count.items():
                    count_ = sum([count_detail for _, count_detail in details_count.items()])

                    if count_ == 0:
                        current_end_dates[backet_order_idxs[order]] = current_date
                        orders_to_delete.update(order)
                        count_empty += 1


                for order in orders_to_delete:
                    del current_orders_count[order]

                if count_empty == len(current_end_dates):
                    break

                if len(nights_orders) > 0:
                    is_night = not is_night

                    if not is_night:
                        current_date += datetime.timedelta(days=1)

                else:
                    current_date += datetime.timedelta(days=1)

        for i, order in enumerate(backet_order):
            details = set(order.details_count.keys())
            self._approve_order(details=details)
            details_readiness[order.order_name] = self.__prepare_details_readiness(details_readiness=backet_details_readiness[order.order_name], orders_types=[order_types[start_index + i]])
            answ[order.order_name] = self.__prepare_answ(details=list(details), orders_types=[order_types[start_index + i]], order_name=order.order_name)

        if len(non_backet_after) > 0:
            answ, details_readiness = self.calc(orders=non_backet_after,
                                                   order_types=order_types[last_index:],
                                                   answ=answ,
                                                   details_readiness=details_readiness,
                                                   clean_all=False)

        answ["Итог"] = self.__prepare_answ(details=list(all_details), orders_types=order_types, order_name=None)
        self.clear()

        details_readiness["Итог"] = pd.concat(list(details_readiness.values())).fillna(0)

        detail_packed: dict[str, pd.DataFrame] = {}
        
        for detail_red in details_readiness:
            tmp = details_readiness[detail_red].copy()
            tmp = tmp.reset_index().drop(columns=["index"])
            details = tmp['Изделие']
            tmp = tmp.drop(columns=["Изделие"])
            tmp = tmp.T.cumsum()
            
            for order in tmp.columns:
                tmp["mod"] = tmp[order] // 10
                tmp["count"] = tmp.groupby("mod").cumcount()
                tmp.loc[tmp["count"]!=0, order] = 0
            
            detail_packed[detail_red] = tmp.drop(columns=["mod", "count"]).T
            detail_packed[detail_red].insert(loc=0, column="Изделие", value=details)

        return answ, details_readiness, detail_packed

    def calc(self,
             orders: list[Order],
             order_types: list[OrderType],
             answ: dict[str, pd.DataFrame] | None = None,
             details_readiness: dict[str, pd.DataFrame] | None = None,
             clean_all: bool = True) -> tuple[dict[str, pd.DataFrame],
                                              dict[str, pd.DataFrame]]:

            details: set[str] = set()

            if answ is None:
                answ: dict[str, pd.DataFrame] = {}

            if details_readiness is None:
                details_readiness: dict[str, pd.dataFrame] = {}

            for order_type, order in zip(order_types, orders):

                order_details: set = set(order.details_count.keys())

                self._start_order(details=order_details)

                if order.date_range[1] is None:
                    order.date_range = (order.date_range[0], order.date_range[0] + datetime.timedelta(days=365 * 42))

                if order_type == OrderType.REVERSE_ONLY_DAY or order_type == OrderType.REVERSE_WITH_NIGHT:
                    details_readiness_ = self._reverse_order(order=order, order_type=order_type)
                else:
                    is_full, details_readiness_, _ = self._order_calc(order=order, order_type=order_type)

                    if not is_full:
                        self._clean_order(order_name=order.order_name)
                        #self._clear_prev_operations()
                        self._start_order(details=order_details)
                        _, details_readiness_, _ = self._order_calc(order=order, order_type=OrderType.WITH_NIGHT)

                self._approve_order(details=order_details)

                details.update(order_details)
                answ[order.order_name] = self.__prepare_answ(details=order_details, orders_types=[order_type], order_name=order.order_name)
                details_readiness[order.order_name] = self.__prepare_details_readiness(details_readiness=details_readiness_, orders_types=[order_type])

            if clean_all:
                answ["Итог"] = self.__prepare_answ(details=details, orders_types=order_types, order_name=None)
                self.clear()

            return answ, details_readiness

    def _clean_order(self, order_name: str) -> None:

        for detail in self.shifts:
            for operation in self.shifts[detail]:
                operation.clean_order(order_name=order_name)

    def _start_order(self, details: set[str] | None) -> None:

        operation_checked: set(str) = set()

        if details is None:
            details = set(self.shifts.keys())

        for detail in details:
            for operation in self.shifts[detail]:
                if operation.operation_name not in operation_checked:
                    operation.start_order()
                    operation_checked.add(operation.operation_name)

    def _approve_order(self, details: set[str]) -> None:

        operation_checked: set(str) = set()

        for detail in details:
            for operation in self.shifts[detail]:
                if operation.operation_name not in operation_checked:
                    operation.approve_order()
                    operation_checked.add(operation.operation_name)


    def _clear_prev_operations(self):

        for detail in self.shifts:
            for operation in self.shifts[detail]:
                operation.clear_prev_operations()

    #строго говоря, тут всё надо распихать по струкутрам - operations, configs
    def calc_old(self,
             operations: dict[str, pd.DataFrame],
             input_count: dict[str, int],
             date_range: tuple[datetime.date, datetime.date]) -> pd.DataFrame:

        details_to_compute: list[str] = list(operations.keys())

        self.__fill_operations(operations=operations, input_count=input_count, details=details_to_compute)
        self.__fill_start(details_count=input_count)

        is_fill: dict[str, bool] = {}

        for detail in details_to_compute:
            is_fill[detail] = False

        current_date: datetime.date =  copy.deepcopy(date_range[0])

        is_full: bool = True

        while current_date <= date_range[1]:

            for detail in details_to_compute:

                if is_fill[detail]:
                    continue

                prev_empty: bool = True

                for i, operation in enumerate(self.shifts[detail]):
                    count, prev_empty = operation.next(date=current_date, is_night=False, prev_empty=prev_empty, detail_name=detail)
                    next_names: set[str] = operation.next_operations[detail]

                    for op_name in next_names:
                        for j in range(i + 1, len(self.shifts[detail])):
                            if self.shifts[detail][j].operation_name == op_name:
                                self.shifts[detail][j].prev_operations[detail][operation.operation_name] += count

                if prev_empty:
                    is_fill[detail] = True

            current_date += datetime.timedelta(days=1)

            is_full = True
            for _, val in is_fill.items():
                is_full = is_full and val

        if not is_full:

            current_date: datetime.date =  copy.deepcopy(date_range[0])
            is_night: bool = False

            for detail in details_to_compute:
                is_fill[detail] = False

            self.clear()
            self.__fill_operations(operations=operations, input_count=input_count, details=details_to_compute)
            self.__fill_start(details_count=input_count)

            while not is_full:

                for detail in details_to_compute:

                    if is_fill[detail]:
                        continue

                    prev_empty: bool = True

                    for i, operation in enumerate(self.shifts[detail]):
                        count, prev_empty = operation.next(date=current_date, is_night=is_night, prev_empty=prev_empty, detail_name=detail)
                        next_names: set[str] = operation.next_operations[detail]

                        for op_name in next_names:
                            for j in range(i + 1, len(self.shifts[detail])):
                                if self.shifts[detail][j].operation_name == op_name:
                                    self.shifts[detail][j].prev_operations[detail][operation.operation_name] += count

                    if prev_empty:
                        is_fill[detail] = True

                if is_night:
                    current_date += datetime.timedelta(days=1)

                is_night = not is_night

                is_full = True
                for _, val in is_fill.items():
                    is_full = is_full and val

        answ: pd.DataFrame = self.__prepare_answ(details=details_to_compute)

        self.clear()

        return answ

    def __fill_operations(self,
                          operations: dict[str, pd.DataFrame],
                          input_count: dict[str, int],
                          details: list[str]) -> None:
        # для каждого заказа эта скорость может быть своя
        #поэтому надо переделать под detail:order:float
        #но пока для нулевого приближения оставим так
        #и вообще эта модель жолжна работать вообще по-другому
        #или не факт, надо будет потом подумать

        for detail in details:
            for shift_operation in self.shifts[detail]:
                if shift_operation.detail_per_hour.get(detail, None) is None:
                    shift_operation.detail_per_hour[detail] = input_count[detail] /  \
                                                               operations[detail][operations[detail]["Operation"] == shift_operation.operation_name.split("|")[1]]["Time"].to_numpy()[0]
                #else:
                #    shift_operation.detail_per_hour[detail] += input_count[detail] /  \
                #                                               operations[detail][operations[detail]["Operation"] == shift_operation.operation_name.split("|")[1]]["Time"].to_numpy()[0]

    def __fill_start(self,
                     details_count: dict[str, int],
                     order_name: str | None = None) -> None:
        #fiil start with detail count
        #Assumtion that order name inserts full in one date

        for detail in details_count:
            start_ops_: list[str] = START_OPS[detail]

            for start_op in start_ops_:
                for op in self.shifts[detail]:
                    if op.operation_name == start_op:

                        if order_name is None:
                            op.prev_operations[detail]["Start"] = details_count[detail]
                        else:
                            if isinstance(op.prev_operations[detail]["Start"], int):
                                tmp_: dict[str, int] = {order_name: details_count[detail]}
                                op.prev_operations[detail]["Start"] = tmp_
                            else:
                                if order_name in op.prev_operations[detail]["Start"]:
                                    if op.prev_operations[detail]["Start"][order_name] == 0:
                                        op.prev_operations[detail]["Start"][order_name] = details_count[detail]
                                else:
                                    op.prev_operations[detail]["Start"][order_name] = details_count[detail]
                                

                        break

    def __prepare_answ(self, details: list[str], orders_types: list[OrderType], order_name: str | None = None) -> pd.DataFrame:

        has_night: bool = False
        
        for order_type in orders_types:
            if order_type == OrderType.REVERSE_WITH_NIGHT or order_type == OrderType.WITH_NIGHT:
                has_night = True
                break

        operations_checked: set[str] = set()
        operations_params: dict[str, list] = {"Сотрудник": [],
                                              "Операция": [],
                                              "Количество": []}
        operations_dates: dict[str, list[tuple[datetime.date, bool]]] = {}
        min_date: datetime.date = datetime.date(2777, 1, 1)
        max_date: datetime.date = datetime.date(1977, 1, 1)

        for detail in details:
            for operation in self.shifts[detail]:
                if operation.operation_name not in operations_checked:
                    operations_checked.add(operation.operation_name)
                    operations_params["Сотрудник"].append(operation.operation_name.split("|")[0])
                    operations_params["Операция"].append(operation.operation_name.split("|")[1])
                    operations_params["Количество"].append(operation.count)

                    fill_dates = operation.fill_dates if order_name is None else operation.orders_fill_dates[order_name]

                    operations_dates[operation.operation_name] = fill_dates

                    for date, _, _ in fill_dates:
                        min_date = min(date, min_date)
                        max_date = max(date, max_date)

        staff_table = pd.DataFrame(operations_params)
        base_range = [(min_date + datetime.timedelta(days=i)).strftime("%m-%d") for i in range((max_date - min_date).days + 1)]
        
        if has_night:
            columns: list = [[date + " День", date + " Ночь"] \
                              for date in base_range]
            columns = [item for row in columns for item in row]
        else:
            columns: list = base_range
            
        dates = pd.DataFrame(columns=columns, dtype=float)
        merged = pd.concat([staff_table, dates]).fillna(0.0)

        new_op_dates: dict[str, dict[str, int]] = {}

        for val, dates in operations_dates.items():
            tmp: dict[str, int] = {}

            for date, is_night, count in dates:
                if is_night:
                    key: str = date.strftime("%m-%d") + " Ночь"
                else:
                    if has_night:
                        key = date.strftime("%m-%d") + " День"
                    else:
                        key = date.strftime("%m-%d")

                if tmp.get(key) is None:
                    tmp[key] = count
                else:
                    tmp[key] += count

            new_op_dates[val] = tmp


        for val, dates in new_op_dates.items():
            dates_ = [date for date in dates]
            count = [count for _, count in dates.items()]

            merged.loc[(merged["Сотрудник"] == val.split("|")[0]) &
                   (merged["Операция"] == val.split("|")[1]), dates_] += count

        return merged

    def __prepare_details_readiness(self, details_readiness: dict[str, tuple], orders_types: list[OrderType]) -> pd.DataFrame:
        """a"""
        has_night: bool = False

        for order_type in orders_types:
            if order_type == OrderType.WITH_NIGHT or order_type == OrderType.REVERSE_WITH_NIGHT:
                has_night = True
                break

        min_date: datetime.date = datetime.date(2777, 1, 1)
        max_date: datetime.date = datetime.date(1977, 1, 1)

        for key, val in details_readiness.items():
            if val[0][0] < min_date:
                min_date = val[0][0]
            if val[-1][0] > max_date:
                max_date = val[-1][0]

        details: pd.DataFrame = pd.DataFrame({"Изделие" : list(details_readiness.keys())})
        base_range = [(min_date + datetime.timedelta(days=i)).strftime("%m-%d") for i in range((max_date - min_date).days + 1)]
        if has_night:    
            columns: list = [[date + " День", date + " Ночь"] \
                             for date in base_range]
            columns = [item for row in columns for item in row]
        else:
            columns = base_range

        dates = pd.DataFrame(columns=columns, dtype=float)
        merged = pd.concat([details, dates]).fillna(0)

        for key, val in details_readiness.items():
            dates_: list[str] = []
            counts: list[int] = [count for _, _, count in val]

            for date_, is_night_, count in val:
                if is_night_:
                    key_: str = date_.strftime("%m-%d") + " Ночь"
                else:
                    if has_night:
                        key_ = date_.strftime("%m-%d") + " День"
                    else:
                        key_ = date_.strftime("%m-%d")

                dates_.append(key_)

            merged.loc[merged["Изделие"] == key, dates_] += counts

        return merged

    def clear(self):
        for detail in self.shifts:
            for shift in self.shifts[detail]:
                shift.clear()

#door = [Оператор станок с пу/лазер|Лазерная резка листа, Оператор станок с пу/гибка|Листогибочная,
#        Эл. Сварщик и п/авт машин|Сварка полуавтоматом в среде защитного газа (MIG),
#        Оператор окрасочно-сушильной линии и агрегата|Окрашивание порошком,
#        Слесарь по сборке|Сборочная, Слесарь по сборке|Упаковочная]

#podshipnik =  [ Слесарь по сборке|Ленточно-отрезная, Станочник широкого профиля|Токарная,
#                Станочник широкого профиля|Вертикально-фрезерная, Оператор окрасочно-сушильной линии и агрегата|Окрашивание порошком,
#                Слесарь по сборке|Сборочная, Слесарь по сборке|Упаковочная
#

# kormushka = [Слесарь по сборке|Слесарная, Оператор станок с пу/лазер|Лазерная резка листа, Слесарь по сборке|Ленточно-отрезная,
#              Оператор станок с пу/гибка|Листогибочная, Оператор станок с пу/гибка|Вальцовочная,
#              Эл. Сварщик и п/авт машин|Сварка полуавтоматом в среде защитного газа (MIG),
#               Слесарь по сборке|Сборочная, Слесарь по сборке|Упаковочная]

laser = ShiftOperation.from_dict(operation_name="Оператор станок с пу/лазер|Лазерная резка листа",
                                 params=MAP_OPERATIONS["Оператор станок с пу/лазер|Лазерная резка листа"])
fold = ShiftOperation.from_dict(operation_name="Оператор станок с пу/гибка|Листогибочная",
                                 params=MAP_OPERATIONS["Оператор станок с пу/гибка|Листогибочная"])
welding = ShiftOperation.from_dict(operation_name="Эл. Сварщик и п/авт машин|Сварка полуавтоматом в среде защитного газа (MIG)",
                                 params=MAP_OPERATIONS["Эл. Сварщик и п/авт машин|Сварка полуавтоматом в среде защитного газа (MIG)"])
color = ShiftOperation.from_dict(operation_name="Оператор окрасочно-сушильной линии и агрегата|Окрашивание порошком",
                                 params=MAP_OPERATIONS["Оператор окрасочно-сушильной линии и агрегата|Окрашивание порошком"])
assembly = ShiftOperation.from_dict(operation_name="Слесарь по сборке|Сборочная",
                                 params=MAP_OPERATIONS["Слесарь по сборке|Сборочная"])
pack = ShiftOperation.from_dict(operation_name="Слесарь по сборке|Упаковочная",
                                 params=MAP_OPERATIONS["Слесарь по сборке|Упаковочная"])
cut = ShiftOperation.from_dict(operation_name="Слесарь по сборке|Ленточно-отрезная",
                                 params=MAP_OPERATIONS["Слесарь по сборке|Ленточно-отрезная"])
lathe = ShiftOperation.from_dict(operation_name="Станочник широкого профиля|Токарная",
                                 params=MAP_OPERATIONS["Станочник широкого профиля|Токарная"])
milling = ShiftOperation.from_dict(operation_name="Станочник широкого профиля|Вертикально-фрезерная",
                                 params=MAP_OPERATIONS["Станочник широкого профиля|Вертикально-фрезерная"])
plumb = ShiftOperation.from_dict(operation_name="Слесарь по сборке|Слесарная",
                                 params=MAP_OPERATIONS["Слесарь по сборке|Слесарная"])
rolling = ShiftOperation.from_dict(operation_name="Оператор станок с пу/гибка|Вальцовочная",
                                 params=MAP_OPERATIONS["Оператор станок с пу/гибка|Вальцовочная"])
NAME_TO_OP: dict[str, ShiftOperation] = \
{
    "Оператор станок с пу/лазер|Лазерная резка листа": laser,
    "Оператор станок с пу/гибка|Листогибочная": fold,
    "Эл. Сварщик и п/авт машин|Сварка полуавтоматом в среде защитного газа (MIG)": welding,
    "Оператор окрасочно-сушильной линии и агрегата|Окрашивание порошком": color,
    "Слесарь по сборке|Сборочная": assembly,
    "Слесарь по сборке|Упаковочная": pack,
    "Слесарь по сборке|Ленточно-отрезная": cut,
    "Станочник широкого профиля|Токарная": lathe,
    "Станочник широкого профиля|Вертикально-фрезерная": milling,
    "Слесарь по сборке|Слесарная": plumb,
    "Оператор станок с пу/гибка|Вальцовочная": rolling
}

details_to_ops: dict[str, list] = {
    "ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx": [laser, fold, welding, color, assembly, pack],
    "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx": [cut, lathe, milling, color, assembly],
    "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx": [plumb, laser, cut, fold, rolling, welding, assembly, pack]
}

shift_calc = ShiftCalc(shifts=details_to_ops)