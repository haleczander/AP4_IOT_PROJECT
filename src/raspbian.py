from Client import Client
from enums import HardwareType, ActionState
from env import *
from payloads import Message, DotDict, Instructions, Instruction, HarwareInfo, HarwareInfos
from utils import async_thread, format_time, normalize_analog, parse_msg, wait_and_execute
from time import sleep
from grovepi import pinMode, analogWrite, dht, analogRead


# def pinMode( *args ): pass
# def analogWrite( *args ): pass
# def dht( *args ): 
#     from random import randint
#     return (randint(5,35), randint(0,100))
# def analogRead( *args ): 
#     from random import randint
#     return randint(0,1023)

# Configuration des capteurs

LIGHT_SENSOR_1_PORT = 1
pinMode(LIGHT_SENSOR_1_PORT, "INPUT")


LED_1_PORT = 2
pinMode(LED_1_PORT, "OUTPUT")

MOISTURE_TEMP_SENSOR_1_PORT = 4
pinMode(MOISTURE_TEMP_SENSOR_1_PORT, "INPUT")

SERVO_MOTOR_1_PORT = 5      # D5
pinMode(SERVO_MOTOR_1_PORT, "OUTPUT")


HARDWARE_ID_PORT_MAPPING = {
    MOISTURE_SENSOR_1_ID: MOISTURE_TEMP_SENSOR_1_PORT,
    TEMPERATURE_SENSOR_1_ID: MOISTURE_TEMP_SENSOR_1_PORT,
    VALVE_SERVO_1_ID: SERVO_MOTOR_1_PORT,
    LIGHT_SENSOR_1_ID: LIGHT_SENSOR_1_PORT,
    LED_1_ID: LED_1_PORT
}


CURRENT_STATE = DotDict()

def send_info(message: Message):
    client.publish(INFO_ROUTE, message, qos=1)

def update_hardware_value( action_fn: callable, hardware_id: int, value: any, *args ):
    action_fn( hardware_id, value, *args )
    CURRENT_STATE[hardware_id] = value
    send_info( HarwareInfo( HARDWARE_TYPES.get(hardware_id), hardware_id, value) )
    
def no_action( hardware_id: int, value: any, *args ):
    pass

def get_port( hardware_id: int ):
    return HARDWARE_ID_PORT_MAPPING.get(hardware_id, None)
    
def valve_action( hardware_id: int, state: ActionState, *args ):
    angle = 180 if state == ActionState.ON else 0
    analogWrite(hardware_id, angle)
    duration = f"for {args[0]} seconds" if args else ""
    print(f"Valve #{hardware_id} is now {state.name}({angle}°) {duration}")
    
def light_action( hardware_id: int, state: ActionState, *args ):
    intensity = 255 if state == ActionState.ON else 0
    analogWrite(hardware_id, intensity)
    print(f"LED #{hardware_id} is now {state.name}")

    
def send_probes_info() :
    infos = DotDict({k: HarwareInfo(HARDWARE_TYPES.get(k), k, v) for k,v in CURRENT_STATE.items() if HARDWARE_TYPES.get(k) is not HardwareType.VALVE and k is not None})
    if infos:
        client.publish( PROBES_ROUTE,infos )


def read_probes():
    t, h = dht( get_port(MOISTURE_SENSOR_1_ID), 1)
    CURRENT_STATE[MOISTURE_SENSOR_1_ID] = h
    CURRENT_STATE[TEMPERATURE_SENSOR_1_ID] = t
    
    light = normalize_analog( analogRead( get_port(LIGHT_SENSOR_1_ID) ) )
    CURRENT_STATE[LIGHT_SENSOR_1_ID] = light
    
    
def handle_valve_instruction( instruction: Instruction ):
    valve_id = instruction.hardware_id
    instruction_state = ActionState[instruction.value]
    current_state = CURRENT_STATE.get(valve_id, ActionState.UNKNOWN)
    if instruction_state == ActionState.ON:
        if ActionState.ON == current_state:
            send_info(Message(valve_id, current_state, "Valve already opened"))
            return
        update_hardware_value(valve_action, valve_id, ActionState.ON, instruction.duration)
        close_callback = lambda: update_hardware_value(valve_action, valve_id, ActionState.OFF)
        async_thread(wait_and_execute, close_callback, instruction.duration)
    else:
        update_hardware_value(valve_action, valve_id, ActionState.OFF)
    
def handle_light_instruction( instruction: Instruction ):
    light_id = instruction.hardware_id
    instruction_state = ActionState[instruction.value]
    current_state = CURRENT_STATE.get(light_id, ActionState.UNKNOWN)
    if instruction_state == ActionState.ON:
        if ActionState.ON == current_state:
            send_info(Message(light_id, current_state, "Light already ON"))
            return
        update_hardware_value(light_action, light_id, ActionState.ON)
    else:
        update_hardware_value(light_action, light_id, ActionState.OFF)  
    
def handle_instruction( instruction: Instruction ):
    try:
        hardware_type = HardwareType[instruction.hardware_type]
               
        if hardware_type == HardwareType.VALVE:
            handle_valve_instruction(instruction)
        elif hardware_type == HardwareType.LIGHT:
            handle_light_instruction(instruction)
        else:
            print( f"[{format_time()}] HardwareType not handled {hardware_type}" )
    except KeyError:
        print( f"[{format_time()}] HardwareType not known {instruction.hardware_type}" )

    
    
def on_instructions( client, userdata, mes ):
    instructions: Instructions = parse_msg( mes )
    [handle_instruction(i) for i in instructions ]
    

    


client = Client(HOST, PORT, ROUTE)
client.add_message_callback(VALVE_ROUTE, on_instructions)
client.connect()
while True:
    try:
        read_probes()
    except Exception as e:
        print(f"Erreur capteur : {e}")

    send_probes_info()
    sleep(5)
