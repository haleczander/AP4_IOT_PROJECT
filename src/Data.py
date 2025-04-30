from time import now
from .States import States


class Data:
    key: States
    value: any
    time: int
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.time = now()
        
Payload = list[Data]
