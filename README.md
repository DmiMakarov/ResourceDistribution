# ResourceDistribution

Main Goal of current project - define and implement mathematical model for enterprise

чтобы понять, сколько реально времени тратится надо считать с учётом блокировок. То есть если для детали С нужна деталь А и Б с временем выполнения 10 и 5, то время, требуемое для изготовления будет 10, потому что вот так вот. То есть нормо-часы - тема
А чтобы это потом оптимизировать, нам просто нужен список деталей всех, не важно для какой конечной детали, просто построим распределение 


Ещё идея - отделить интерфейс по загрузке деталей и запуску расчёта

Чтобы посчитать смены, надо сложить датафреймы для всех деталей

Улучшения модели:
1) Добавить время на смежные процессы, чтобы учлись перемещения между операциями
2) Интеграция с исходным сервисом