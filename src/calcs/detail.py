"""Define Detail class"""
from dataclasses import dataclass

@dataclass
class Detail():
    """
    Class to store detail information
    
    params:
    name - name of detail
    """
    name: str
    count: int