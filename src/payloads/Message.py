from time import time
from typing import Dict, List

from enums import ProbeType, ValveState

class DotDict(dict):
    def __init__(self, dict ):
        super().__init__()
        self.update(dict)
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
    
class ProbeInfo(Message):
    time: int
    probe_type: ProbeType
    
    def __init__(self, probe_type, hardware_id: int, value: any):
        super().__init__(hardware_id, value)
        self.probe_type = probe_type
        self.time = time()
        
ProbeInfos = Dict[int, ProbeInfo]
        
        
class ValveInstruction(Message):
    duration: int
    
    def __init__(self, hardware_id: int, state: ValveState, duration: int):
        super().__init__(hardware_id, state)
        self.duration = duration
        
        self.comment = f"Valve set to {state.name} for {self.duration} seconds"
        
    
    time = None
        
ValveInstructions = List[ValveInstruction]
        