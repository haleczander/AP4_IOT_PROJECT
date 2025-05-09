from enums import ValveState, ProbeType
from payloads import ProbeInfos, ValveInstruction, Message, ValveInstructions, DotDict
from env import *
from Client import Client
from time import time
from utils import *
from time import sleep  

CURRENT_STATE = dict[int, Message]()
VALVE_PROBE_MAPPING: dict[int, int] = {1: 1}  

def get_valve_from_probe(probe_id: int) -> int:
    return VALVE_PROBE_MAPPING.get(probe_id, 0)

def send_valve_instructions(instructions: ValveInstructions):
    if instructions:  # Vérifie qu’il y a bien des instructions à envoyer
        print(f"📨 Envoi des instructions : {instructions}")
        client.publish(VALVE_ROUTE, instructions, qos=1)

def on_probe_message(client, userdata, mes):
    payload: ProbeInfos = parse_msg(mes)
    CURRENT_STATE.update(payload)
    valve_instructions = []

    for probe_id, probe_info in payload.items():
        print_message(probe_info)
        try:
            probe_type = ProbeType[probe_info.probe_type]
            if probe_type == ProbeType.MOISTURE:
                if probe_info.value < MOISTURE_THRESHOLD:
                    valve_id = get_valve_from_probe(probe_id)
                    if valve_id:  
                        valve_instructions.append(
                            ValveInstruction(valve_id, ValveState.OPEN, WATER_TIMER)
                        )
            else:
                print(f"[{time()}] 🚫 Probe type not handled: {probe_type}")
        except KeyError:
            print(f"[{time()}] 🚫 Probe type not known: {probe_info.probe_type}")

    # Envoi des instructions après le traitement de tous les capteurs
    send_valve_instructions(valve_instructions)

def on_info(client, userdata, mes):
    info: Message = DotDict(parse_msg(mes))
    print_message(info)

client = Client(HOST, PORT, ROUTE)
client.add_message_callback(PROBES_ROUTE, on_probe_message)
client.add_message_callback(INFO_ROUTE, on_info)
client.connect()

while True:
    sleep(5)
