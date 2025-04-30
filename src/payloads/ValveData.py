from enums import MessageType, ValveState
from . import Data


class ValveData( Data ):
    id: int
    state: ValveState
    duration: int
    
    def __init__(self, id: int, state: ValveState, duration: int):
        super().__init__( MessageType.VALVE , state )
        self.id = id
        self.state = state
        self.duration = duration
    
    
    