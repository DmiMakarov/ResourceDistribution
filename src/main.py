from calcs.tabel_time import TableTime
from calcs.detail import Detail

table_time: TableTime = TableTime()
detail: Detail = Detail(name='Тех_карта_ЗМС_ДМГС_6_00_000_02_01_Дверь_тип_6_990х2040_левая', count=1)
answ  = table_time.calc([detail])
/print('a')