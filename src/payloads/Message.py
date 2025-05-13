from time import time
from typing import Dict, List

from enums import HardwareType, ActionState

class DotDict(dict):
    def __init__(self, dict={} ):
        super().__init__()
        for key, value in dict.items():
            if hasattr(value, 'keys'):
                value = DotDict(value)
            self[key] = value
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__

class Message( DotDict ):
    hardware_id: int
    value: any
    comment: str
    
    def __init__(self, hardware_id: int, value: any, comment: str = None):
        self.hardware_id = hardware_id
        self.value = value
        self.comment = comment
        
class HardwareMessage( Message ):
    hardware_type: HardwareType
    
    def __init__(self, hardware_type: HardwareType, hardware_id: int, value: any):
        super().__init__(hardware_id, value)
        self.hardware_type = hardware_type
    
class HardwareInfo(HardwareMessage):
    time: int
    
    def __init__(self, hardware_type: HardwareType, hardware_id: int, value: any):
        super().__init__(hardware_type, hardware_id, value)
        self.time = time()
        
HardwareInfos = Dict[int, HardwareInfo]
        
        
class Instruction(HardwareMessage):
    duration: int
    
    def __init__(self, hardware_type: HardwareType, hardware_id: int, state: ActionState, duration: int=None):
        super().__init__(hardware_type, hardware_id, state)
        self.duration = duration
        duration = f" for {duration} seconds" if duration else ""
        self.comment = f"HARDWARE#{hardware_id} set to {state.name}{duration}"
        
            
Instructions = List[Instruction]
        