from enums import MessageType
from time import now

class Data:
    time: int
    key: MessageType
    value: any
    
    def __init__(self, key: MessageType, value: any):
        self.key = key
        self.value = value
        self.time = now()
        
