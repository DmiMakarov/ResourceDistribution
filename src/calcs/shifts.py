"""
Define ShiftOPeration class

Main idea is to accumulate info about previous operation during one shift
"""
import copy
import datetime

import pandas as pd
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
                                 {"Оператор станок с пу/гибка|Листосгибочная"},
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {},
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {"Оператор станок с пу/гибка|Листосгибочная",
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
                                    "Оператор станок с пу/гибка|Листосгибочная": 0,
                                    "Слесарь по сборке|Слесарная": 0
                                 }
                        
                                 },
             "next_operations": {
                                 "ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx": 
                                 {"Слесарь по сборке|Упаковочная"},
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {"Слесарь по сборке|Упаковочная"},
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
                                    "Слесарь по сборке|Сборочная": 0
                                 },
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {
                                    "Слесарь по сборке|Слесарная": 0,
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
                                    "Оператор станок с пу/гибка|Листосгибочная": 0
                                 },
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {
                                 },
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {"Оператор станок с пу/гибка|Листосгибочная": 0,
                                  "Слесарь по сборке|Ленточно-отрезная": 0}
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
            "Оператор станок с пу/гибка|Листосгибочная":
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
                                 {"Слесарь по сборке|Сборочная"},
                                 "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx":
                                 {},
                                 "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx":
                                 {"Слесарь по сборке|Сборочная",
                                  "Эл. Сварщик и п/авт машин|Сварка полуавтоматом в среде защитного газа (MIG"}
                                }
            },
            "Оператор станок с пу/гибка|Вальцовочная":
             {"machine": 1,
             "people": 1
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

class ShiftOperation:

    def __init__(self,
                 count: int,
                 operation_name: str,
                 detail_per_hour: dict[str, float],
                 prev_operations: dict[str, int],
                 next_operations: set[str],
                 ) -> None:
        self.count: int = 0
        self.operation_name: str = operation_name
        self.detail_per_hour: dict[str, float] = detail_per_hour
        #for parallel operations

        self.prev_operations: dict[str, dict[str, int]] = prev_operations
        self.next_operations: dict[str, set[str]] = next_operations

        #Day - false, Night - True
        self.fill_dates: list[tuple[datetime.date, bool]] = []

    @staticmethod
    def from_dict(cls, 
                  operation_name,
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

    def clear(self):
        for detail in self.prev_operations:
            for prev_operation in self.prev_operations[detail]:
                self.prev_operations[detail][prev_operation] = 0
#что мне теперь надо для вычислений
#1. Составить конфигурации всех деталей
#2. Заполнить detail_per_hour (идеально по конфигу, но пофиг, пока так сделаем) - done
#3. Написать цикл вычислений
#4. Собрать в одну таблицу

class ShiftCalc:
    def __init__(self,
                 shifts: dict[str, list[ShiftOperation]]) -> None:
        self.shifts: dict[str, list[ShiftOperation]] = shifts

    #строго говоря, тут всё надо распихать по струкутрам - operations, configs
    def calc(self,
             operations: dict[str, pd.DataFrame],
             input_count: dict[str, int],
             date_range: tuple[datetime.date, datetime.date]) -> pd.DataFrame:

        self.__fill_operations(operations=operations, input_count=input_count)
        self.__fill_start(details_count=input_count)

        details_to_compute: list[str] = list(operations.keys())

        is_fill: dict[str, bool] = {}

        for detail in details_to_compute:
            is_fill[detail] = False

        current_date: datetime.date =  copy.copy(date_range[0])
        
        while current_date <= date_range[1]:
            
            for detail in details_to_compute:
                
                if is_fill[detail]:
                    continue

                prev_empty: bool = True

                for i, operation in enumerate(self.shift[detail]):
                    count, prev_empty = operation.next(date=current_date, is_night=False, prev_empty=prev_empty, detail_name=detail)
                    next_names: set[str] = operation.next_operations[detail]

                    for op_name in next_names:
                        for j in range(i + 1, len(self.shift[detail])):
                            if self.shifts[j].operation_name == op_name:
                                self.shifts[j].prev_operations[detail][operation.operation_name] += count
                    
                if prev_empty:
                    is_fill[detail] = True

            current_date += datetime.timedelta(days=1)

        is_full: bool = True
        for _, val in is_fill:
            is_full = is_full and is_fill
        
        if not is_full:

            current_date: datetime.date =  copy.copy(date_range[0])
            is_night: bool = False
        
            while not is_full:
            
                for detail in details_to_compute:
                
                    if is_fill[detail]:
                        continue

                    prev_empty: bool = True

                    for i, operation in enumerate(self.shift[detail]):
                        count, prev_empty = operation.next(date=current_date, is_night=False, prev_empty=prev_empty, detail_name=detail)
                        next_names: set[str] = operation.next_operations[detail]

                        for op_name in next_names:
                            for j in range(i + 1, len(self.shift[detail])):
                                if self.shifts[j].operation_name == op_name:
                                    self.shifts[j].prev_operations[detail][operation.operation_name] += count
                    
                    if prev_empty:
                        is_fill[detail] = True

                if is_night:
                    current_date += datetime.timedelta(days=1)
                
                is_night = not is_night

                is_full: bool = True
                for _, val in is_fill:
                    is_full = is_full and is_fill

        answ: pd.DataFrame = self.__prepare_answ(details=details_to_compute) 
        
        self.clear()

        return answ


    def __fill_operations(self,
                          operations: dict[str, pd.DataFrame],
                          input_count: dict[str, int]) -> None:


        for detail in self.shifts:
            for shift_operation in self.shifts[detail]:
                shift_operation.detail_per_hour = input_count['detail'] /  \
                                                  operations[operations["Operation"] == shift_operation.operation_name.split("|")[1]]["Time"].to_numpy()[0]

    def __fill_start(self,
                     details_count: dict[str, int]) -> None:
        #fiil start with detail count
        for detail in details_count:
            start_ops_: list[str] = START_OPS[detail]
            
            for start_op in start_ops_:
                for op in self.shifts[detail]:
                    if op.operation_name == start_op:
                        op.prev_operations[detail]["Start"] = details_count[detail]
                        
                        break
    
    def __prepare_answ(self, details: list[str]) -> pd.DataFrame:
        
        operations_checked: set[str] = {}
        operations_params: dict[str, list] = {"Сотрудник": [],
                                              "Операция": [],
                                              "Количество": []}
        operations_dates: dict[str, list[tuple[datetime.date, bool]]] = {}
        min_date: datetime.date = datetime.date(1977, 1, 1)
        max_date: datetime.date = datetime.date(2777, 1, 1)

        for detail in details:
            for operation in self.shifts[detail]:
                if operation.operation_name not in operations_checked:
                    operations_checked.add(operation.operation_name)
                    operations_params["Сотрудник"].append(operation.operation_name.split("|")[0])
                    operations_params["Операция"].append(operation.operation_name.split("|")[0])
                    operations_params["Количество"].append(operation.count)

                    operations_dates[operation.operation_name] = operation.fill_dates

    def clear(clear):
        for detail in self.shifts:
            for shift in self.shifts[shift]:
                shift.clear()

#door = [Оператор станок с пу/лазер|Лазерная резка листа, Оператор станок с пу/гибка|Листосгибочная,
#        Эл. Сварщик и п/авт машин|Сварка полуавтоматом в среде защитного газа (MIG),
#        Оператор окрасочно-сушильной линии и агрегата|Окрашивание порошком, 
#        Слесарь по сборке|Сборочная, Слесарь по сборке|Упаковочная]

#podshipnik =  [ Слесарь по сборке|Ленточно-отрезная, Станочник широкого профиля|Токарная, 
#                Станочник широкого профиля|Вертикально-фрезерная, Оператор окрасочно-сушильной линии и агрегата|Окрашивание порошком,
#                Слесарь по сборке|Сборочная, Слесарь по сборке|Упаковочная
#]

# kormushka = [Слесарь по сборке|Слесарная, Оператор станок с пу/лазер|Лазерная резка листа, Слесарь по сборке|Ленточно-отрезная,
#              Оператор станок с пу/гибка|Листосгибочная, Оператор станок с пу/гибка|Вальцовочная,
#              Эл. Сварщик и п/авт машин|Сварка полуавтоматом в среде защитного газа (MIG),
#               Слесарь по сборке|Сборочная, Слесарь по сборке|Упаковочная]

laser = ShiftOperation.from_dict(operation_name="Оператор станок с пу/лазер|Лазерная резка листа",
                                 params=MAP_OPERATIONS["Оператор станок с пу/лазер|Лазерная резка листа"])
fold = ShiftOperation.from_dict(operation_name="Оператор станок с пу/гибка|Листосгибочная",
                                 params=MAP_OPERATIONS["Оператор станок с пу/гибка|Листосгибочная"])
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

details_to_ops: dict[str, list] = {
    "ЗМСДМГС6000000201Дверьтип6990х2040левая.xlsx": [laser, fold, welding, color, assembly, pack],
    "ЗМСПУБДТ00000ПодшипниковыйузелБДТ.xlsx": [cut, lathe, milling, color, assembly, pack],
    "ЗМСКДОП7502х400000Кормушкадоминокомбинированная.xlsx": [plumb, laser, cut, fold, rolling, welding, assembly, pack]
}

shift_calc = ShiftCalc(shifts=details_to_ops)