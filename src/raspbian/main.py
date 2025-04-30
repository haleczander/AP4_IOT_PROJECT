

from Client import Client
from enums import ValveState
from env import *
from payloads import ValveData, Info
from utils import async_thread, parse_msg, wait_and_execute

valve_states = {}

def send_valve_info( valve_id: int, info: any ):
    client.publish( INFO_ROUTE, Info( f"VALVE ({valve_id}): {info}" ) , qos=1 )

def set_valve_state( valve_id: int, state: ValveState ):
    valve_states[valve_id] = state
    send_valve_info( valve_id, state )
    #TODO: set the state of the valve in the hardware
    
def on_valve_message( client, userdata, mes ):
    message: ValveData = parse_msg( mes )
    valve_id = message.valve_id
    match message.state:
        case ValveState.OPEN:
            if valve_states.get(valve_id) == ValveState.OPEN:
                send_valve_info( valve_id, "Already open" )
                return
            set_valve_state(valve_id, ValveState.OPEN)
            close_callback = lambda: set_valve_state(valve_id, ValveState.CLOSE)
            async_thread( wait_and_execute, close_callback, message.duration )
        case ValveState.CLOSE:
            set_valve_state(valve_id, ValveState.CLOSE)
        case _:
            print(f"Unknown valve state: {message.state}")
    




client = Client( HOST, PORT, ROUTE )
client.add_message_callback(VALVE_ROUTE, on_valve_message)