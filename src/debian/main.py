from enums import ValveState, ProbeType
from payloads import ProbeInfos, ValveInstruction, Message, ValveInstructions
from ..env import *
from ..Client import Client
from time import time
from ..utils import *

CURRENT_STATE = dict[int, Message]()
VALVE_PROBE_MAPPING : dict[int, int] = {1: 2}
       
def get_valve_from_probe( probe_id: int ) -> int:
    return VALVE_PROBE_MAPPING.get( probe_id, 0 )
        
def send_valve_instructions( instructions: ValveInstructions ):
    client.publish( VALVE_ROUTE, instructions, qos=1 )
    [ print_info(i) for i in instructions ]
    
def on_probe_message( client, userdata, mes ):
    payload: ProbeInfos = parse_msg( mes )
    CURRENT_STATE.update( payload )
    valve_instructions = ValveInstructions()
    for (probe_id, probe_info) in payload.items():
        print_info( probe_info )
        match probe_info.probe_type:
            case ProbeType.MOISTURE:
                if probe_info.value < MOISTURE_THRESHOLD:
                    valve_instructions.append( ValveInstruction( get_valve_from_probe(probe_id), ValveState.OPEN, WATER_TIMER ) )
            case _:
                print( f"[{time()}] Probe type not handled {probe_info.probe_type.name}" )
                
            
def print_info( info: Message ):
    comment = f": {info.comment})" if info.comment else ""
    timestamp = f" at {info.time}" if info.time else ""
    print( f"[{time()}]INFO #{info.hardware_id} - {info.value}{comment}{timestamp}" )
    
    
def on_info( client, userdata, mes ):
    info: Message = parse_msg( mes )
    print_info( info )
    
    

client = Client( HOST, PORT, ROUTE )
client.add_message_callback(PROBES_ROUTE, on_probe_message)
client.add_message_callback(INFO_ROUTE, on_info)
