from dataclasses import dataclass

from calcs.detail import Detail
from calcs.employee import Employee
from calcs.operation import Operation, ConveyorOperation

@dataclass
class DetailTransition():
    detail_from: Detail
    operation: Operation | ConveyorOperation
    detail_to: Detail

class DetailTree():
    def __init__(self):
        self.transitions: list[DetailTransition] = []

    def get_operations(detail: Detail, count: int) -> dict[Detail, 
                                                           tuple[Operation, Detail]]: