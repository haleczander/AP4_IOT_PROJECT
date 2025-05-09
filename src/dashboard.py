import paho.mqtt.client as mqtt
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from datetime import datetime
from Client import Client
from env import *
from payloads import Message
from payloads.Message import HarwareInfos
from utils import parse_msg

CURRENT_STATE = dict[int, Message]()       



# Variables globales
humidity_values = []
time_values = []

# Fenêtre principale
root = tk.Tk()
root.title(PROJECT_NAME)
root.geometry("900x600")

# Titre
title_label = tk.Label(root, text=PROJECT_NAME, font=("Helvetica", 24, "bold"))
title_label.pack(pady=20)

# Texte pour l'humidité
humidity_label = tk.Label(root, text="Humidité : --%", font=("Helvetica", 18))
humidity_label.pack(pady=10)

# Texte pour l'état des valves
valve_label = tk.Label(root, text="État de la valve : Inconnu", font=("Helvetica", 18))
valve_label.pack(pady=10)

# Graphique pour l'humidité
fig = Figure(figsize=(8, 4), dpi=100)
ax = fig.add_subplot(111)
ax.set_title("Évolution de l'humidité")
ax.set_xlabel("Temps")
ax.set_ylabel("Humidité (%)")
line, = ax.plot([], [], color='blue', linewidth=2)

canvas = FigureCanvasTkAgg(fig, root)
canvas.get_tk_widget().pack()


def on_hardware_message(client, userdata, message):
    payload: HarwareInfos = parse_msg( message )
    CURRENT_STATE.update( payload )
    for (probe_id, probe_info) in CURRENT_STATE.items():
        try:
            probe_type = HardwareType[ probe_info.probe_type ]
            # comment = f": {probe_info.comment})" if probe_info.comment else ""
            # timestamp = f" at {format_time(probe_info.time)}" if probe_info.time else ""
            # probe_type = f"({probe_info.probe_type})" if probe_info.probe_type else ""
            # print( f"[{format_time()}]INFO #{probe_info.hardware_id}{probe_type} - {probe_info.value}{comment}{timestamp}" )
        except KeyError:pass

# Configuration du client MQTT
client = Client( HOST, PORT, ROUTE )
client.add_message_callback(PROBES_ROUTE, on_hardware_message)
client.connect()
# Lancer l'interface Tkinter
root.mainloop()