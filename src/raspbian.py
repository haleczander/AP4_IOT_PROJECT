from Client import Client
from enums import ProbeType, ValveState
from env import *
from payloads import Message, DotDict, ValveInstructions, ValveInstruction, ProbeInfo, ProbeInfos
from utils import async_thread, parse_msg, wait_and_execute
from time import sleep
from grovepi import pinMode, analogRead, servoWrite

# Configuration des capteurs
MOISTURE_SENSOR_PORT = 0  # A0
SERVO_MOTOR_PORT = 5      # D5

pinMode(MOISTURE_SENSOR_PORT, "INPUT")
pinMode(SERVO_MOTOR_PORT, "OUTPUT")

CURRENT_STATE = DotDict()

def send_info(message: Message):
    client.publish(INFO_ROUTE, message, qos=1)

def update_hardware_value( action_fn: callable, hardware_id: int, *args: any,  ):
    action_fn( hardware_id, *args )
    CURRENT_STATE[hardware_id] = args
    send_info( Message(hardware_id, args) )
    
def no_action( hardware_id: int, *args ):
    pass
    
def valve_action( hardware_id: int, state: ValveState ):
    angle = 180 if state == ValveState.OPEN else 0
    servoWrite(SERVO_MOTOR_PORT, angle)
    print(f"Valve {hardware_id} is now {state.name}({angle}°)")
    
def send_probes_info() :
    infos = DotDict({k: ProbeInfo(ProbeType.MOISTURE, k, v) for k,v in CURRENT_STATE.items()})
    client.publish( PROBES_ROUTE,infos )

    
    
def handle_valve_instruction( instruction: ValveInstruction ):
    valve_id = instruction.hardware_id
    instruction_state = ValveState[instruction.value]
    current_state = CURRENT_STATE.get(valve_id, ValveState.UNKNOWN)
    if instruction_state == ValveState.OPEN:
        if ValveState.OPEN == current_state:
            send_info(Message(valve_id, current_state, "Valve already opened"))
            return
        update_hardware_value(valve_action, valve_id, ValveState.OPEN, instruction.duration)
        close_callback = lambda: update_hardware_value(valve_action, valve_id, ValveState.CLOSE)
        async_thread(wait_and_execute, close_callback, instruction.duration)
    else:
        update_hardware_value(valve_action, valve_id, ValveState.CLOSE)
    
    
def on_valve_instructions( client, userdata, mes ):
    instructions: ValveInstructions = parse_msg( mes )
    [handle_valve_instruction(i) for i in instructions ]
    
    


client = Client(HOST, PORT, ROUTE)
client.add_message_callback(VALVE_ROUTE, on_valve_instructions)
client.connect()
while True:
    try:
        # Lecture de l'humidité
        raw_value = analogRead(MOISTURE_SENSOR_PORT)
        moisture = raw_value / 1023.0  # Converti en pourcentage (0–1)
        print(f"Humidité mesurée : {moisture:.2f}")

        # Mise à jour de l'état actuel
        CURRENT_STATE[MOISTURE_SENSOR_PORT] = moisture
        send_probes_info()
    except Exception as e:
        print(f"Erreur capteur : {e}")

    CURRENT_STATE.update( {MOISTURE_SENSOR_PORT: .12})
    send_probes_info()
    sleep(5)
