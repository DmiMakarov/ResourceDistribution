import datetime
from calcs.detail import Detail
from calcs.tabel_time import TableTime
from calcs.shifts import shift_calc

table_time: TableTime = TableTime()
detail: Detail = Detail(name="ЗМСДМГС6000000201Дверьтип6990х2040левая", count=137)
detail1: Detail = Detail(name="ЗМСПУБДТ00000ПодшипниковыйузелБДТ", count=56)
detail2: Detail = Detail(name="ЗМСКДОП7502х400000Кормушкадоминокомбинированная", count=27)

answ  = table_time.calc([detail, detail1, detail2])

res = shift_calc.calc(operations=answ,
                input_count={detail.name + ".xlsx": detail.count,
                             detail1.name + ".xlsx": detail1.count,
                             detail2.name + ".xlsx": detail2.count},
                date_range=(datetime.date(year=2024,month=12,day=12),
                            datetime.date(year=2025,month=1,day=12)))
print(res)
#answ.to_excel("./data/answ.xlsx")