from paho.mqtt.client import Client as mqttClient
from json import dumps
from utils import encoder

class Client( mqttClient ):
    def __init__( self, host, port, route ):
        super().__init__()
        self.host = host
        self.port = port
        self.route = route
        self.message_callback = {}
                
    def build_topic( self, route ):
        return f"{self.route}{route}"
        
    def connect( self ):
        super().connect( self.host, self.port )
        self.loop_start()      
        
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0 :
            print( "connected ")
            for topic, fn in self.message_callback.items():
                full_topic = self.build_topic(topic)
                print(f'Subscribing to {full_topic}')
                self.subscribe(full_topic)
                self.message_callback_add(full_topic, fn)
        else :
            print('Erreur à la connexion')

        
    def add_message_callback(self, topic, fn ):
        self.message_callback.update({topic: fn})
        
    def publish( self, topic, message, **kwargs ):
        super().publish( self.build_topic( topic ), dumps(message, default=encoder), **kwargs )