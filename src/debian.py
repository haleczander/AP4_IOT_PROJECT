from enums import ActionState, HardwareType
from payloads import HarwareInfos, Instruction, Message, Instructions, DotDict
from env import *
from Client import Client
from utils import *

CURRENT_STATE = dict[int, Message]()       

        
def send_valve_instructions( instructions: Instructions ):
    client.publish( VALVE_ROUTE, instructions, qos=1 )
    
def on_probe_message( client, userdata, mes ):
    payload: HarwareInfos = parse_msg( mes )
    CURRENT_STATE.update( payload )
    valve_instructions = []#ValveInstructions()
    for (probe_id, probe_info) in payload.items():
        print_message( probe_info )
        valve_id = PROBE_ACTION_MAPPING.get(int(probe_id), None)
        try:
            hardware_type = HardwareType[ probe_info.hardware_type ]
            if hardware_type == HardwareType.MOISTURE:
                if probe_info.value < MOISTURE_THRESHOLD:
                    valve_instructions.append( Instruction( hardware_type, valve_id, ActionState.ON, WATER_TIMER ) )
            elif hardware_type == HardwareType.LIGHT:
                action = ActionState.OFF if probe_info.value > BRIGHTNESS_THRESHOLD else ActionState.ON
                valve_instructions.append( Instruction( hardware_type, valve_id, action ) )
            else:
                print( f"[{format_time()}] Probe type not handled {hardware_type}" )
        except KeyError:
            print( f"[{format_time()}] Probe type not known {probe_info.hardware_type}" )
    if valve_instructions:
        send_valve_instructions( valve_instructions )
                
            

    
    
def on_info( client, userdata, mes ):
    info: Message = DotDict( parse_msg( mes ) )
    print_message( info )
    
    

client = Client( HOST, PORT, ROUTE )
client.add_message_callback(PROBES_ROUTE, on_probe_message)
client.add_message_callback(INFO_ROUTE, on_info)
client.connect()

while True:
    sleep(5)
