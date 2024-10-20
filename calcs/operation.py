'''Define operation class'''
from calcs.resource import Resource
from calcs.employee import Employee

class LinearOperation():
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
        return count * self.standart_time
    
class PiecewiseOperation(LinearOperation):
    '''
    Define piecewise-linear oparation class

    count_params: max count in one piece of operation
    '''
    def __init__(self,
                 name: str,
                 standart_time: int,
                 resources: list[Resource],
                 employees: list[Employee],
                 count_params: int):
        super().__init__(name, standart_time, resources, employees)
        self.count_params: int = count_params

    def calc(self, count: int) -> int:
        '''Calculate time for piecewise-linear operations'''
        return count * self.count_params * self.standart_time