'''Define operation class'''
from src.calcs.resource import Resource
from src.calcs.employee import Employee

class Operation():
    '''
    Define linear oparation class

    name: name of operation
    standart_time: standtart time of execution (нормо-часы)
    resources: list of using resources (equipment)
    employees: list of employees
    '''
    def __init__(self, 
                 name: str,
                 standart_time: int,
                 resources: list[Resource],
                 employees: list[Employee]):
        self.name: str = name
        self.standart_time: int = standart_time
        self.resources: list[Resource] = resources
        self.employees: list[Employee] = employees

    def calc(self, count: int) -> int:
        '''Calculate standart time'''
        self.time: int =  int(count * self.standart_time)

        return self.time
    
class ConveyorOperation(Operation):
    '''
    Define piecewise-linear oparation class

    count_params: max count in one piece of operation
    '''
    def __init__(self,
                 name: str,
                 standart_time: int,
                 resources: list[Resource],
                 employees: list[Employee],
                 time_per_element: float,
                 max_count: int):
        '''
        Same as LinearOperation

        time_per_element - distance between details / velocity of conveyer
        max_count - max_count on conveyer belt
        '''
        super().__init__(name, standart_time, resources, employees)
        self.time_per_element: int = time_per_element
        self.max_count = max_count

    def calc(self, count: int) -> int:
        '''Calculate time for piecewise-linear operations'''
        self.time: int = (self.standart_time + (self.max_count - 1) * self.time_per_element) * count // self.max_count
        
        if count % self.max_count > 0:
            self.time += self.standart_time + (count % self.max_count  - 1) * self.time_per_element

        self.time = int(self.time)

        return self.time