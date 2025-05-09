from Client import Client
from enums import ProbeType, ValveState
from env import *
from payloads import Message, DotDict, ValveInstructions, ValveInstruction, ProbeInfo, ProbeInfos
from utils import async_thread, parse_msg, wait_and_execute
from time import sleep
import grovepi
import math

# Configuration des capteurs
MOISTURE_SENSOR_PORT = 0  # A0
SERVO_MOTOR_PORT = 5      # D5

grovepi.pinMode(MOISTURE_SENSOR_PORT, "INPUT")
grovepi.pinMode(SERVO_MOTOR_PORT, "OUTPUT")

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
    angle = 180 of state == ValveState.OPEN else 0
    grovepi.servoWrite(SERVO_MOTOR_PORT, angle)
    print(f"Valve {hardware_id} is now {state.name}({angle}°)")
    
def send_probes_info() :
    infos = DotDict({k: ProbeInfo(ProbeType.MOISTURE, k, v) for k,v in CURRENT_STATE.items()})
    client.publish( PROBES_ROUTE,infos )

    
    
def handle_valve_instruction( instruction: ValveInstruction ):
    valve_id = instruction.hardware_id
    current_state = CURRENT_STATE.get(valve_id, ValveState.UNKNOWN)

    if instruction.value == ValveState.OPEN:
        if current_state == ValveState.OPEN:
            send_info(Message(valve_id, current_state, "Valve already opened"))
            return
        update_hardware_value(valve_action, valve_id, ValveState.OPEN)
        close_callback = lambda: update_hardware_value(valve_action, valve_id, ValveState.CLOSE)
        async_thread(wait_and_execute, close_callback, instruction.duration)
    else:
        update_hardware_value(valve_action, valve_id, ValveState.CLOSE)
    else:
        send_info(Message(valve_id, current_state, "Unknown valve state received"))
    
    
def on_valve_instructions( client, userdata, mes ):
    instructions: ValveInstructions = parse_msg( mes )
    [handle_valve_instruction(i) for i in instructions ]
    
    


client = Client(HOST, PORT, ROUTE)
client.add_message_callback(VALVE_ROUTE, on_valve_instructions)
client.connect()
while True:
    try:
        # Lecture de l'humidité
        raw_value = grovepi.analogRead(MOISTURE_SENSOR_PORT)
        moisture = raw_value / 1023.0  # Converti en pourcentage (0–1)
        print(f"Humidité mesurée : {moisture:.2f}")

        # Mise à jour de l'état actuel
        CURRENT_STATE[1] = moisture  # hardware_id = 1
        send_probes_info()

        # Contrôle automatique de la valve en fonction de l'humidité
        if moisture < HUMIDITY_THRESHOLD_OPEN:
            update_hardware_value(valve_action, 1, ValveState.OPEN)
        elif moisture > HUMIDITY_THRESHOLD_CLOSE:
            update_hardware_value(valve_action, 1, ValveState.CLOSE)

        sleep(5)

    except Exception as e:
        print(f"Erreur capteur : {e}")
        sleep(5)
    CURRENT_STATE.update( {1: .12})
    send_probes_info()
    sleep(5)
