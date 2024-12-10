"""
Define ShiftOPeration class

Main idea is to accumulate info about previous operation during one shift
"""

import datetime

class ShiftOperation():

    def __init__(self,
                 operation_name: str,
                 detail_per_hour: dict[str, float],
                 prev_operations: dict[str, int],
                 next_operations: set[str],
                 ) -> None:
        self.operation_name: str = operation_name
        self.detail_per_hour: dict[str, float] = detail_per_hour
        #for parallel operations

        self.prev_operations: dict[str, dict[str, int]] = prev_operations
        self._next_operations: dict[str, set[str]] = next_operations

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
             is_night: bool,
             prev_empty: bool,
             detail_name: str) -> tuple[int, bool]:

        min_available_details: int = min([value for _, value in  self.prev_operation[detail_name].items()])

        if (min_available_details / self.detail_per_hour[detail_name] <= 12 ) and not prev_empty:
            return 0, False

        day_available: bool = is_night
        night_available: bool = is_night

        for dt, is_day in self.fill_dates:
            if dt == date:
                if is_day:
                    day_available = False
                else:
                    night_available = False

        if not day_available and night_available:
            return 0, False

        details_in_this_date: int = int(min(self.detail_per_hour[detail_name] * 12 * (day_available + night_available),
                                        min_available_details / self.detail_per_hour[detail_name]))
        self.fill_dates.append((date, is_night))

        #по идее с нескольких источников должно заполняться равномерн, то есть ноль тогда, когда везде ноль
        for op in self.prev_operations[detail_name]:
            self.prev_operations[detail_name][op] -= min_available_details

            prev_empty = prev_empty and (self.prev_operations[detail_name][op] == 0)

        return details_in_this_date, prev_empty


#что мне теперь надо для вычислений
#1. Составить конфигурации всех деталей
#2. Заполнить detail_per_hour (идеально по конфигу, но пофиг, пока так сделаем)
#3. Написать цикл вычислений
#4. Собрать в одну таблицу

class ShiftCalc:

    def __init__(self,
                 shifts: list[ShiftOperation]):
        self.shifts: list[ShiftOperation] = shifts

    def calc():
        while true:
            current_date+=1

            if total_doors == required_doors:
                break