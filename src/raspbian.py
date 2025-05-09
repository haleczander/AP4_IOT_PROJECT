from Client import Client
from enums import ValveState, ProbeType
from env import *
from payloads import Message, ValveInstruction, ValveInstructions, ProbeInfo
from utils import async_thread, parse_msg, wait_and_execute
from time import sleep
import grovepi

# Configuration des capteurs
MOISTURE_SENSOR_PORT = 0  # A0
SERVO_MOTOR_PORT = 5      # D5

grovepi.pinMode(MOISTURE_SENSOR_PORT, "INPUT")
grovepi.pinMode(SERVO_MOTOR_PORT, "OUTPUT")

def valve_action(hardware_id: int, state: ValveState):
    if state == ValveState.OPEN:
        print(f"🚰 Valve {hardware_id} ouverte")
        grovepi.analogWrite(SERVO_MOTOR_PORT, 180)
    elif state == ValveState.CLOSE:
        print(f"🚫 Valve {hardware_id} fermée")
        grovepi.analogWrite(SERVO_MOTOR_PORT, 0)
    else:
        print(f"❓ État de valve inconnu pour {hardware_id}: {state}")

def handle_valve_instruction(instruction: ValveInstruction):
    valve_id = instruction.hardware_id
    if instruction.value in [ValveState.OPEN, ValveState.CLOSE]:
        valve_action(valve_id, instruction.value)
        if instruction.value == ValveState.OPEN and instruction.duration:
            close_callback = lambda: valve_action(valve_id, ValveState.CLOSE)
            async_thread(wait_and_execute, close_callback, instruction.duration)
    else:
        print(f"❓ Instruction inconnue reçue : {instruction}")

def on_valve_instructions(client, userdata, mes):
    instructions: ValveInstructions = parse_msg(mes)
    for instruction in instructions:
        handle_valve_instruction(instruction)

def send_probe_info(probe_id: int, value: float):
    info = {probe_id: ProbeInfo(ProbeType.MOISTURE, probe_id, value)}
    print(f"📡 Envoi de l'humidité : {value:.2f} pour sonde {probe_id}")
    client.publish(PROBES_ROUTE, info)

client = Client(HOST, PORT, ROUTE)
client.add_message_callback(VALVE_ROUTE, on_valve_instructions)
client.connect()

PROBE_ID = 1  # ID de la sonde pour identification côté serveur

while True:
    try:
        # Lecture de l'humidité
        raw_value = grovepi.analogRead(MOISTURE_SENSOR_PORT)
        moisture = raw_value / 1023.0  # Converti en pourcentage (0-1)

        # Envoi de l'info au serveur
        send_probe_info(PROBE_ID, moisture)

        sleep(5)
    except Exception as e:
        print(f"Erreur capteur : {e}")
        sleep(5)
