import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
import json
import time
from datetime import timedelta
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict
import threading
from Client import Client
from env import *
from payloads import Message
from payloads.Message import HardwareInfo, HardwareInfos
from utils import parse_msg

# Variables globales
CURRENT_STATE = dict()
STATES = defaultdict(list)

# Dictionnaire pour les noms des types de capteurs
SENSOR_TYPES = {
    'MOISTURE': 'Humidité',
    'TEMPERATURE': 'Température',
    'LIGHT': 'Luminosité'
}

# Dictionnaire pour les unités des types de capteurs
SENSOR_UNITS = {
    'MOISTURE': '%',
    'TEMPERATURE': '°C',
    'LIGHT': 'lux'
}

# Dictionnaire pour les couleurs des graphiques selon le type de capteur
SENSOR_COLORS = {
    'MOISTURE': 'blue',
    'TEMPERATURE': 'red',
    'LIGHT': 'orange'
}

class SensorDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title(PROJECT_NAME)
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Structure pour stocker les widgets d'affichage des valeurs actuelles
        self.value_labels = {}
        self.type_labels = {}
        self.figures = {}
        self.axes = {}
        self.canvases = {}
        self.lines = {}
        
        # Période d'affichage des données (en minutes)
        self.display_period = 30
        
        # Configurer les styles
        self.configure_styles()
        
        # Créer l'interface
        self.create_widgets()
        
        # Démarrer le thread de mise à jour des graphiques
        self.update_thread = threading.Thread(target=self.update_graphs_thread)
        self.update_thread.daemon = True
        self.update_thread.start()

    def configure_styles(self):
        # Configuration des styles
        style = ttk.Style()
        
        # Style pour les frames
        style.configure("TFrame", background="#f0f0f0")
        
        # Style pour les labels
        style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 12))
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), padding=10)
        style.configure("Value.TLabel", font=("Helvetica", 24, "bold"))
        style.configure("Unit.TLabel", font=("Helvetica", 14))
        
        # Style pour les séparateurs
        style.configure("TSeparator", background="#cccccc")

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre du dashboard
        title_label = ttk.Label(main_frame, text=PROJECT_NAME, style="Header.TLabel")
        title_label.pack(fill=tk.X, pady=(0, 20))
        
        # Frame pour les valeurs actuelles
        values_frame = ttk.Frame(main_frame)
        values_frame.pack(fill=tk.X, pady=10)
        
        # Frame pour les graphiques
        graphs_frame = ttk.Frame(main_frame)
        graphs_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Créer les espaces pour chaque type de capteur dans le frame des valeurs
        for i, sensor_type in enumerate(['MOISTURE', 'TEMPERATURE', 'LIGHT']):
            # Frame pour ce type de capteur
            sensor_frame = ttk.Frame(values_frame)
            sensor_frame.grid(row=0, column=i, padx=20, sticky="nsew")
            
            # Label pour le type de capteur
            type_label = ttk.Label(
                sensor_frame,
                text=SENSOR_TYPES.get(sensor_type, sensor_type),
                style="Header.TLabel"
            )
            type_label.pack(pady=(0, 5))
            
            # Frame pour la valeur et l'unité
            value_unit_frame = ttk.Frame(sensor_frame)
            value_unit_frame.pack()
            
            # Label pour la valeur
            value_label = ttk.Label(
                value_unit_frame,
                text="--",
                style="Value.TLabel",
                foreground=SENSOR_COLORS.get(sensor_type, "black")
            )
            value_label.pack(side=tk.LEFT)
            
            # Label pour l'unité
            unit_label = ttk.Label(
                value_unit_frame,
                text=SENSOR_UNITS.get(sensor_type, ""),
                style="Unit.TLabel"
            )
            unit_label.pack(side=tk.LEFT, padx=(5, 0))
            
            # Stocker les références aux labels
            self.value_labels[sensor_type] = value_label
            self.type_labels[sensor_type] = type_label
        
        # Séparateur entre les valeurs et les graphiques
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=20)
        
        # Créer les graphiques pour chaque type de capteur
        for i, sensor_type in enumerate(['MOISTURE', 'TEMPERATURE', 'LIGHT']):
            # Frame pour ce graphique
            graph_frame = ttk.Frame(graphs_frame)
            graph_frame.grid(row=0, column=i, padx=10, sticky="nsew")
            
            # Créer la figure et les axes
            fig = Figure(figsize=(4, 3), dpi=100)
            ax = fig.add_subplot(111)
            
            # Configurer les axes
            ax.set_title(SENSOR_TYPES.get(sensor_type, sensor_type))
            ax.set_xlabel('Temps')
            ax.set_ylabel(SENSOR_UNITS.get(sensor_type, ""))
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Formater l'axe x pour afficher l'heure
            ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
            
            # Créer une ligne vide pour les données
            line, = ax.plot([], [], color=SENSOR_COLORS.get(sensor_type, "black"), lw=2)
            
            # Créer le widget Canvas pour afficher la figure
            canvas = FigureCanvasTkAgg(fig, master=graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Stocker les références aux objets graphiques
            self.figures[sensor_type] = fig
            self.axes[sensor_type] = ax
            self.canvases[sensor_type] = canvas
            self.lines[sensor_type] = line
        
        # Configurer le redimensionnement des colonnes
        values_frame.columnconfigure(0, weight=1)
        values_frame.columnconfigure(1, weight=1)
        values_frame.columnconfigure(2, weight=1)
        
        graphs_frame.columnconfigure(0, weight=1)
        graphs_frame.columnconfigure(1, weight=1)
        graphs_frame.columnconfigure(2, weight=1)

    def update_values(self):
        """Met à jour les valeurs affichées dans les labels."""
        for hardware_id, info in CURRENT_STATE.items():
            hardware_type = info.hardware_type
            if hardware_type in self.value_labels:
                self.value_labels[hardware_type].config(text=f"{info.value}")

    def update_graphs(self):
        """Met à jour les graphiques avec les données actuelles."""
        current_time = datetime.now()
        min_time = current_time - timedelta(minutes=self.display_period)
        
        for sensor_type in ['MOISTURE', 'TEMPERATURE', 'LIGHT']:
            data_times = []
            data_values = []
            
            # Trouver le capteur correspondant à ce type
            for hardware_id, messages in STATES.items():
                for msg in messages:
                    if msg.hardware_type == sensor_type:
                        # Convertir le timestamp en datetime
                        msg_time = datetime.fromtimestamp(msg.time)
                        
                        # Ne garder que les données dans la période d'affichage
                        if msg_time >= min_time:
                            data_times.append(msg_time)
                            data_values.append(msg.value)
            
            # Mettre à jour le graphique si nous avons des données
            if data_times and data_values:
                self.lines[sensor_type].set_data(data_times, data_values)
                
                # Ajuster les limites des axes
                self.axes[sensor_type].set_xlim(min_time, current_time)
                
                if data_values:
                    min_val = min(data_values)
                    max_val = max(data_values)
                    padding = (max_val - min_val) * 0.1 if max_val > min_val else 1
                    self.axes[sensor_type].set_ylim(min_val - padding, max_val + padding)
                
                # Redessiner le graphique
                self.figures[sensor_type].tight_layout()
                self.canvases[sensor_type].draw()

    def update_graphs_thread(self):
        """Thread pour mettre à jour les graphiques régulièrement."""
        while True:
            try:
                # Utiliser after pour exécuter les mises à jour dans le thread principal
                self.root.after(0, self.update_values)
                self.root.after(0, self.update_graphs)
                time.sleep(1)  # Mettre à jour toutes les secondes
            except Exception as e:
                print(f"Erreur lors de la mise à jour des graphiques: {e}")
                time.sleep(5)  # Attendre avant de réessayer en cas d'erreur


def on_hardware_message(client, userdata, message):
    """Callback pour les messages MQTT reçus."""
    try:
        payload: HardwareInfos = parse_msg(message)
        CURRENT_STATE.update(payload)
        
        # Mettre à jour l'historique des données
        for probe_id, probe_info in payload.items():
            STATES[probe_id].append(probe_info)
            
            # Limiter la taille de l'historique (optionnel)
            if len(STATES[probe_id]) > 1000:
                STATES[probe_id] = STATES[probe_id][-1000:]
        
        print(f"Message reçu: {payload}")
    except Exception as e:
        print(f"Erreur lors du traitement du message: {e}")


# Fonction principale
def main():
    # Fenêtre principale
    root = tk.Tk()
    
    # Créer le dashboard
    dashboard = SensorDashboard(root)
    
    # Configuration du client MQTT
    client = Client(HOST, PORT, ROUTE)
    client.add_message_callback(PROBES_ROUTE, on_hardware_message)
    client.connect()
    
    # Lancer l'interface Tkinter
    root.mainloop()


if __name__ == "__main__":
    main()
