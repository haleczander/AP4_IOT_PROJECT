from time import time

from enums import ProbeType, ValveState

class Message:
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
        
ProbeInfos = dict[int, ProbeInfo]
        
        
class ValveInstruction(Message):
    duration: int
    
    def __init__(self, hardware_id: int, state: ValveState, duration: int):
        super().__init__(hardware_id, state)
        self.duration = duration
        
    comment = lambda self : f"Valve {self.state.name} for {self.duration} seconds"
        
ValveInstructions = list[ValveInstruction]
        