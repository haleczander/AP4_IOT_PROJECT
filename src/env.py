
from enums import HardwareType

HOST="mosquitto.junia.com"
#HOST="broker.hivemq.com"

PORT=1883
PROJECT_NAME="Notre super potager connecté"
PROJECT_ROUTE="notre_super_potager_connecte"
ROUTE=f"/Junia/{PROJECT_ROUTE}"

PROBES_ROUTE="/probes"
VALVE_ROUTE="/valve"
INFO_ROUTE="/info"


MOISTURE_THRESHOLD = 80
BRIGHTNESS_THRESHOLD = 60
TEMPERATURE_THRESHOLD = 35


WATER_TIMER = 10
SEND_INTERVAL = 600

MOISTURE_SENSOR_1_ID = 0
TEMPERATURE_SENSOR_1_ID = 1
VALVE_SERVO_1_ID = 5

LIGHT_SENSOR_1_ID = 2
LED_1_ID = 3
BUZZER_1_ID = 4




HARDWARE_TYPES = {
    MOISTURE_SENSOR_1_ID: HardwareType.MOISTURE, 
    TEMPERATURE_SENSOR_1_ID: HardwareType.TEMPERATURE,
    VALVE_SERVO_1_ID: HardwareType.VALVE,
    LIGHT_SENSOR_1_ID: HardwareType.LIGHT,
    LED_1_ID: HardwareType.LED,
    BUZZER_1_ID: HardwareType.BUZZER
}

PROBE_ACTION_MAPPING = {
    MOISTURE_SENSOR_1_ID: VALVE_SERVO_1_ID,
    LIGHT_SENSOR_1_ID: LED_1_ID,
    TEMPERATURE_SENSOR_1_ID: BUZZER_1_ID,
}
