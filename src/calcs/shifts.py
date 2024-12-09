"""
Define ShiftOPeration class

Main idea is to accumulate info about previous operation during one shift
"""

import datetime

class ShiftOperation():

    def __init__(self,
                 operation_name: str,
                 detail_per_hour: float,
                 prev_operations: dict[str, int],
                 next_operations: set[str],
                 has_night: bool = True
                 ) -> None:
        self.operation_name: str = operation_name
        self.detail_per_hour: float = detail_per_hour
        self.has_night = has_night
        #for parallel operations

        self.prev_operations: dict[str, int] = prev_operations
        self._next_operations: set[str] = next_operations

        #Day - false, Night - True
        self.fill_dates: list[tuple[datetime.date, bool]] = []

    #кладём все смены в один массив последовательно так, чтобы
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
             prev_empty: bool) -> tuple[int, bool]:

        min_available_details: int = min([value for _, value in  self.prev_operations])

        if (min_available_details / self.detail_per_hour <= 12 + self.has_night * 12) and not prev_empty:
            return 0, False

        details_in_this_date: int = min(self.detail_per_hour * (12 + self.has_night * 12),
                                        min_available_details / self.detail_per_hour)
        self.fill_dates.append((date, False))

        if self.has_night:
            self.fill_dates.append((date, True))

        #по идее с нескольких источников должно заполняться равномерн, то есть ноль тогда, когда везде ноль
        for op in self.prev_operations:
            self.prev_operations[op] -= min_available_details

            prev_empty = prev_empty and (self.prev_operations[op] == 0)

        return details_in_this_date, prev_empty


class ShiftBuilder:

    def __init__(self):
        self.shifts: list[ShiftOperation] = []

    def calc():
        while true:
            current_date+=1

            if total_doors == required_doors:
                break