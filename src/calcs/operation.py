"""Define operation class"""


class Operation:
    """
    Define linear operation class
    name: name of operation

    standard_time: standard time of execution (нормо-часы)
    """

    def __init__(self,
                 name: str,
                 standard_time: float,
                 tpz: float) -> None:

        self.name: str = name
        self.standard_time: int = standard_time
        self.tpz = tpz

    def calc(self, count: int) -> float:
        """Calculate standard time"""
        self.time: float =  count * self.standard_time + self.tpz

        return self.time


class ConveyorOperation(Operation):
    """
    Define piecewise-linear operation class
    count_params: max count in one piece of operation
    """
    def __init__(self,
                 name: str,
                 standard_time: float,
                 tpz: float,
                 time_per_element: float,
                 max_count: int) -> None:
        """
        Same as LinearOperation
        time_per_element - distance between details / velocity of conveyer
        max_count - max_count on conveyer belt
        """
        super().__init__(name, standard_time, tpz)
        self.time_per_element: int = time_per_element
        self.max_count = max_count

    def calc(self, count: int) -> float:
        """Calculate time for piecewise-linear operations"""
        self.time = (self.standard_time + (self.max_count - 1) * self.time_per_element) * count // self.max_count

        if count // self.max_count > 0:
            self.time += self.standard_time + (count % self.max_count  - 1) * self.time_per_element

        self.time += self.tpz

        return self.time
