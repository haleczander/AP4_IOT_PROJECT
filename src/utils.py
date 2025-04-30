from threading import Thread
from time import sleep

def parse_msg( msg ):
    return msg.payload.decode("UTF-8")

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


