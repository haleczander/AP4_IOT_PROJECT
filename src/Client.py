from paho.mqtt.client import Client as mqttClient

class Client( mqttClient ):
    def __init__( self, host, port, route ):
        super().__init__()
        self.host = host
        self.port = port
        self.route = route
        
    def build_topic( self, route ):
        return f"{self.route}{route}"
        
    def connect( self ):
        super().connect( self.host, self.port )
        
    def add_message_callback(self, endpoint, fn ):
        self.message_callback_add(f"{self.route}{endpoint}", fn)
        
    def publish( self, topic, message, **kwargs ):
        super().publish( self.build_topic( topic ), message, **kwargs )