import json
import threading

file_path = 'configuration.json'

# Open the JSON file in read mode
with open(file_path, 'r') as json_file:
    # Load the JSON data into a Python dictionary
    configuration_data      = json.load(json_file)
    database_configuration  = configuration_data["Database"]
    mqtt_configuration      = configuration_data["MQTT"]
    accessories_configuration       = configuration_data["Items"]

# app.config['SECRET_KEY'] = 'your_secret_key_here'
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Set session duration (e.g., 7 days)
sensor_types = list(accessories_configuration["Items Status"].keys())

# # is_first_load = True
# # page_loaded = False

class Session:
    def __init__(self):
        self.data = {}
    
    def get(self, key):
        return self.data.get(key)
    
    def set(self, key, value):
        self.data[key] = value

session = Session()
session.set('username', 'admin')
session.set('user_id', 1)
session.set('dashboard_id', 1)

# to exit from threading when the app closed
exit_event = threading.Event()

# to handle insertion between threads -> used for (onmessage), handle_acuator_event functions
insertion_event = threading.Event()


# You can use to help you in debug show you useful infomation
GLOBAL_VERBOSE = True

SHOW_ID_WITH_NAME = GLOBAL_VERBOSE