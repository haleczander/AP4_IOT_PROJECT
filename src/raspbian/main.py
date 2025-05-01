

from Client import Client
from enums import ValveState
from env import *
from payloads import Message, ValveInstructions, ValveInstruction
from utils import async_thread, parse_msg, wait_and_execute

CURRENT_STATE = dict[int, any]()

def send_info( message: Message ):
    client.publish( INFO_ROUTE, message , qos=1 )

def update_hardware_value( hardware_id: int, value: any, action_fn: callable ):
    action_fn( hardware_id, value )
    CURRENT_STATE[hardware_id] = value
    send_info( Message(hardware_id, value) )
    
    
def valve_action( hardware_id: int, state: ValveState ):
    #TODO: Implement the actual hardware action here
    print(f"Valve {hardware_id} is now {state.name}")
    
    
def handle_valve_instruction( instruction: ValveInstruction ):
    valve_id = instruction.hardware_id
    current_state = CURRENT_STATE.get(valve_id, ValveState.UNKNOWN)
    match instruction.value:
        case ValveState.OPEN:
            if ValveState.OPEN == current_state:
                send_info( Message( valve_id, current_state, "Valve already opened" ) )
                return
            update_hardware_value(valve_id, ValveState.OPEN, valve_action)
            close_callback = lambda: update_hardware_value(valve_id, ValveState.CLOSE, valve_action)
            async_thread( wait_and_execute, close_callback, instruction.duration )
        case ValveState.CLOSE:
            update_hardware_value(valve_id, ValveState.CLOSE, valve_action)
        case _:
            send_info( Message( valve_id, current_state, "Unknown valve state received" ) )
    
    
def on_valve_instructions( client, userdata, mes ):
    instructions: ValveInstructions = parse_msg( mes )
    [handle_valve_instruction(i) for i in instructions ]
    
    

    




client = Client( HOST, PORT, ROUTE )
client.add_message_callback(VALVE_ROUTE, on_valve_instructions)