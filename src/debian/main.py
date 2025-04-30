from threading import Thread
from ..States import States
from ..env import *
from ..Client import Client
from ..Data import Data, Payload
from time import now, sleep
from ..utils import *

class State(dict[States,any]):   
    def __setitem__(self, key: States, value):
        if not isinstance(key, States):
            raise KeyError(f"Clé invalide : {key} (doit être un état valide)")
        super().__setitem__(key, value)

DB = []
CURRENT_STATE = State()

def store_data( data: Data ):
    DB.append( data ) 
    
def toggle_water( state: bool):
    client.publish( WATER_ROUTE, state, qos=2 )
    
def start_water_timer( duration: int ):
    def water_timer():
        sleep( duration )
        if CURRENT_STATE.WATER:
            toggle_water( False )    
    thread = Thread( target= water_timer, name="WaterTimerThread" )
    thread.start()
    
def start_watering( duration : int= WATER_TIMER ):
    toggle_water( True )
    start_water_timer( duration )
    
    
def metier():
    water = CURRENT_STATE.get(States.WATER, False) 
    moisture = CURRENT_STATE.get(States.MOISTURE, 0)

    if water is False and moisture < MOISTURE_THRESHOLD:
        toggle_water( True )
        
    
    
def on_probe_message( client, userdata, mes ):
    dataset: Payload = parse_msg( mes )
    for data in dataset:
        store_data(data)
        CURRENT_STATE[ data.key ] = data.value
    
    

client = Client( HOST, PORT, ROUTE )
client.add_message_callback(PROBES_ROUTE, on_probe_message)
