from calcs.detail import Detail
from calcs.tabel_time import TableTime

table_time: TableTime = TableTime()
detail: Detail = Detail(name="ЗМС ПУ БДТ 00 000 Подшипниковый узел БДТ", count=212)
answ  = table_time.calc([detail])
answ.to_excel("./data/answ.xlsx")