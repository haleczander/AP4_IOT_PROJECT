from threading import Thread

import State
from enums import ValveState
from payloads import Info, Payload, ValveData
from ..enums.MessageType import MessageType
from ..env import *
from ..Client import Client
from time import now
from ..utils import *

CURRENT_STATE = State()

    


    
    
def metier():
    water = CURRENT_STATE.get(MessageType.WATER, False) 
    moisture = CURRENT_STATE.get(MessageType.MOISTURE, 0)

    if water is False and moisture < MOISTURE_THRESHOLD:
        payload = ValveData( 0, ValveState.OPEN )
        client.publish( VALVE_ROUTE, payload, qos=1 )
        
    
    
def on_probe_message( client, userdata, mes ):
    payload: Payload = parse_msg( mes )
    CURRENT_STATE.update( payload )
    metier()
    
def on_info( client, userdata, mes ):
    info: Info = parse_msg( mes )
    print( f"[{now()}] {info.message} ({info.time})" )
    
    

client = Client( HOST, PORT, ROUTE )
client.add_message_callback(PROBES_ROUTE, on_probe_message)
client.add_message_callback(INFO_ROUTE, on_info)
