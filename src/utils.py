from enum import Enum
from threading import Thread
from time import sleep
from json import JSONDecodeError, loads

from payloads import DotDict

def parse_msg( msg ):
    decoded_payload = msg.payload.decode("UTF-8")
    try:
        decoded = loads(decoded_payload)
        return decoder( decoded )

    except JSONDecodeError:
        print(f"Erreur de décodage JSON: {decoded_payload}")
        return None  # ou gérer l'erreur comme nécessaire

    

def wait_and_execute( func, delay: int= 0, *args, **kwargs ):
    sleep( delay )
    func( *args, **kwargs )
    
def wait_and_execute_loop( func, delay: int= 0, *args, **kwargs ):
    while True:
        sleep( delay )
        func( *args, **kwargs )
        
def async_thread( exec_func, func, delay: int= 0, *args, **kwargs ):
    thread = Thread( target=exec_func, args=(func, delay, *args), kwargs=kwargs )
    thread.daemon = True
    thread.start()
    return thread

def encoder( element: any ):
    if isinstance(element, Enum):
        return element.name
    
    if isinstance(element, dict):
        return {key: encoder(value) for key, value in element.items()}
    
    if isinstance(element, list):
        return [encoder(item) for item in element]
    
    return element

def decoder( element: any ):
    if isinstance(element, dict):
        message = DotDict(element)
        return message
    elif isinstance(element, list):
        return [DotDict(item) for item in element]
    return element


