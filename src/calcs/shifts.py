"""
Define ShiftOPeration class

Main idea is to accumulate info about previous operation during one shift
"""
import copy
import datetime

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
                                    "Слесарь по сборке|Слесарная": 0
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
                                    "Слесарь по сборке|Сборочная": 0,
                                    "Эл. Сварщик и п/авт машин|Сварка полуавтоматом в среде защитного газа (MIG)": 0
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
                                 {"Слесарь по сборке|Упаковочная"}
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

    "Планирование", "Обратное планирование (день)", "Обратное планирование (день + ночь)"

    @classmethod
    def from_str(cls, val: str):
        if val == "Планирование":
            return cls.DEFAULT
        elif val == "Обратное планирование (день)":
            return cls.ONLY_DAY
        elif val == "Обратное планирование (день)":
            return cls.WITH_NIGHT
        else:
            raise ValueError("Неизвестный тип заказов")

@dataclass
class Order:

    order_name: str
    operations: dict[str, pd.DataFrame]
    details_count: dict[str, int]
    date_range: tuple[datetime.date, datetime.date | None]
    

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

        for dt, is_night_, count in self.tmp_fill_dates:
            if dt == date:
                if is_night_:

                    hours_available = 11 - count

                    if hours_available < self.detail_per_hour[detail_name]:
                        night_available = False
                else:
                    
                    hours_available = 11 - count

                    if hours_available < self.detail_per_hour[detail_name]:
                        day_available = False

        if not day_available and not night_available:
            return 0, False

        details_in_this_date: int = int(min([self.detail_per_hour[detail_name] * 11 * (day_available + night_available),
                                            min_available_details, hours_available * self.detail_per_hour[detail_name]]))
        if details_in_this_date > 0:
            self.tmp_fill_dates.append((date, is_night,
                                        details_in_this_date / self.detail_per_hour[detail_name]))
            
            if order_name not in self.orders_fill_dates:
                self.orders_fill_dates[order_name] = [(date, is_night, details_in_this_date / self.detail_per_hour[detail_name])]
            else:
                self.orders_fill_dates[order_name].append((date, is_night, details_in_this_date / self.detail_per_hour[detail_name]))
            
        #по идее с нескольких источников должно заполняться равномерн, то есть ноль тогда, когда везде ноль
        for op in self.prev_operations[detail_name]:
            self.prev_operations[detail_name][op] -= details_in_this_date

            prev_empty = prev_empty and (self.prev_operations[detail_name][op] == 0)

        return details_in_this_date, prev_empty

    def clear(self)-> None:
        for detail in self.prev_operations:
            for prev_operation in self.prev_operations[detail]:
                self.prev_operations[detail][prev_operation] = 0
        self.fill_dates = []
        self.detail_per_hour = {}

    def clear_prev_operations(self) -> None:
        for detail in self.prev_operations:
            for prev_operation in self.prev_operations[detail]:
                self.prev_operations[detail][prev_operation] = 0
        
        self.detail_per_hour = {}

    def clean_order(self, order_name: str) -> None:
        self.tmp_fill_dates = []
        self.orders_fill_dates[order_name] = {}

    def approve_order(self) -> None:
        self.fill_dates.extend(self.tmp_fill_dates)
        self.tmp_fill_dates = []

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
                    order_type: OrderType) -> bool:
        """
        А теперь вопрос - если мы храним текущие данные, то как делать, если не помещается?
        быстрое решение - сделать tmp_fill_date 
        """
        is_fill: dict[str, bool] = {}

        details_to_compute: list[str] = list(order.operations.keys())

        for detail in details_to_compute:
            is_fill[detail] = False

        self.__fill_operations(operations=order.operations, input_count=order.details_count, details=details_to_compute)
        self.__fill_start(details_count=order.details_count)

        current_date: datetime.date =  copy.copy(order.date_range[0])
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

                    for op_name in next_names:
                        for j in range(i + 1, len(self.shifts[detail])):
                            if self.shifts[detail][j].operation_name == op_name:
                                self.shifts[detail][j].prev_operations[detail][operation.operation_name] += count

                if prev_empty:
                    is_fill[detail] = True

            is_full = True
            for _, val in is_fill.items():
                is_full = is_full and val

            if order_type == OrderType.WITH_NIGHT:
                if is_night:
                    current_date += datetime.timedelta(days=1)

                is_night = not is_night
            else:
                current_date += datetime.timedelta(days=1)

        return is_full

    def calc(self,
             orders: list[Order],
             order_types: list[OrderType]) -> dict[str, pd.DataFrame]:
            
            details: set[str] = set()

            answ: dict[str, pd.DataFrame] = {}

            for order_type, order in zip(order_types, orders):

                if order.date_range[1] is None:
                    order.date_range = (order.date_range[0], order.date_range[0] + datetime.timdelta(days=365 * 42))

                is_full: bool = self._order_calc(order=order, order_type=order_type)

                if not is_full:
                    self._clean_order(order_name=order.order_name)
                    self._clear_prev_operations()
                    self._order_calc(order=order, order_type=OrderType.WITH_NIGHT)

                self._approve_order()

                order_details: set = set(order.details_count.keys())
                details.update(order_details)
                answ[order.order_name] = self.__prepare_answ(details=order_details, order_name=order.order_name)

            answ["total"] = self.__prepare_answ(details=details, order_name=None)

            self.clear()

            return answ

    def _clean_order(self,
                    order_name: str) -> None:

        for detail in self.shifts:
            for operation in self.shifts[detail]:
                operation.clean_order(order_name=order_name)

    def _approve_order(self) -> None:

        for detail in self.shifts:
            for operation in self.shifts[detail]:
                operation.approve_order()

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

        current_date: datetime.date =  copy.copy(date_range[0])

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

            current_date: datetime.date =  copy.copy(date_range[0])
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

        for detail in details:
            for shift_operation in self.shifts[detail]:
                if shift_operation.detail_per_hour.get(detail, None) is None:
                    shift_operation.detail_per_hour[detail] = input_count[detail] /  \
                                                               operations[detail][operations[detail]["Operation"] == shift_operation.operation_name.split("|")[1]]["Time"].to_numpy()[0]
                else:
                    shift_operation.detail_per_hour[detail] += input_count[detail] /  \
                                                               operations[detail][operations[detail]["Operation"] == shift_operation.operation_name.split("|")[1]]["Time"].to_numpy()[0]

    def __fill_start(self,
                     details_count: dict[str, int]) -> None:
        #fiil start with detail count
        for detail in details_count:
            start_ops_: list[str] = START_OPS[detail]

            for start_op in start_ops_:
                for op in self.shifts[detail]:
                    if op.operation_name == start_op:
                        op.prev_operations[detail]["Start"] += details_count[detail]

                        break

    def __prepare_answ(self, details: list[str], order_name: str | None = None) -> pd.DataFrame:

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
        base_range = [(min_date + datetime.timedelta(days=i)).strftime("%d-%m-%Y") for i in range((max_date - min_date).days + 1)]
        columns: list = [[date + " День", date + " Ночь"] \
                          for date in base_range]
        columns = [item for row in columns for item in row]
        dates = pd.DataFrame(columns=columns, dtype=float)
        merged = pd.concat([staff_table, dates]).fillna(0.0)

        new_op_dates = {}

        for val, dates in operations_dates.items():
            tmp = []
            for date, is_night, count in dates:
                if is_night:
                    tmp.append((date.strftime("%d-%m-%Y") + " Ночь", count))
                else:
                    tmp.append((date.strftime("%d-%m-%Y") + " День", count))
            new_op_dates[val] = tmp

        for val, dates in new_op_dates.items():
            dates_ = [date[0] for date in dates]
            count = [count[1] for count in dates]
            merged.loc[(merged["Сотрудник"] == val.split("|")[0]) &
                   (merged["Операция"] == val.split("|")[1]), dates_] += count

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