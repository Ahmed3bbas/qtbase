from PyQt5.QtCore import QThread, pyqtSignal
from database import Controller
from custom_ui import Window
from globals import  exit_event, mqtt_configuration, insertion_event, GLOBAL_VERBOSE # sensor_data,
from MQTT_services.MQTT import MQTT


class MQTT_receiver(MQTT):
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def on_connect(client, userdata, flags, rc):
        if GLOBAL_VERBOSE:
            print("Connected to MQTT Broker")

    @staticmethod
    def on_message(client, userdata, message):
        try:
            # global sensor_data
            data = dict(
                topic=message.topic,
                payload=message.payload.decode()
            )
            if GLOBAL_VERBOSE:
                print(data)
            topic_parts = data['topic'].split('/')
            sensor_type = topic_parts[1]
            sensor_id = topic_parts[2]
            # if sensor_type not in sensor_data:
            #     sensor_data[sensor_type] = {}
            # sensor_data[sensor_type][sensor_id] = data['payload']
            if Controller.check_item_totally(sensor_type, int(sensor_id), data['payload']):
                if Window and MQTT_receiver.main_window:
                    if GLOBAL_VERBOSE:
                        print("[INFO] update the GUI form the reciever...")
                    MQTT_receiver.main_window.update_items_signal.emit(sensor_type, int(sensor_id), data['payload'])
                else:
                    print("There is no Window Class for GUI")
                # TODO update the database
                # Controller.insert_reading(sensor_type, sensor_id, data['payload'])
            else:
                print("[WARNING]: message recived from MQTT is not valid", f"sensor_type: {sensor_type}, id: {int(sensor_id)}, status: {data['payload']}")
            insertion_event.set()

        except Exception as e:
            print("[ERROR]: in mqtt socket sender")




class MQTTReceiverThread(QThread):
    update_signal = pyqtSignal(str, str, str)

    def __init__(self):
        super().__init__()
        self.mqtt_client = MQTT.mqtt_client
        self._stop_event = False

    def run(self):
        if MQTT_receiver.main_window:
            self.mqtt_client.on_connect = MQTT_receiver.on_connect
            self.mqtt_client.on_message = MQTT_receiver.on_message
            self.mqtt_client.connect(mqtt_configuration['broker'], mqtt_configuration['port'], mqtt_configuration['keep_alive'])
            self.mqtt_client.subscribe("#")
            while not exit_event.is_set():
                self.mqtt_client.loop(timeout=1.0)
            self.mqtt_client.disconnect()
            if GLOBAL_VERBOSE:        
                print("MQTT receiver is disconnected and thread exiting.")
        else:
            print("You have to set mainwindow like this: (MQTT_client(`window obj`)")
    
    def stop(self):
        self._stop_event = True















##########################################################################################################


# from database import Controller
# from custom_ui import Window
# from globals import sensor_data, exit_event, mqtt_configuration, insertion_event  # it is very important don't remove it
# from MQTT_services.MQTT import MQTT

# class MQTT_receiver(MQTT):
#     def __init__(self) -> None:
#         pass
    
#     @staticmethod
#     def on_connect(client, userdata, flags, rc):
#         print("Connected to MQTT Broker")

#     @staticmethod
#     def on_message(client, userdata, message):
#         # if insertion_event.is_set():
#         #     # DO NOT do anything when the user publish data from the GUI for example when click on the lamb(switch) or siren
#         #     pass
#         # else:
#             try:
#                 global sensor_data
#                 data = dict(
#                     topic=message.topic,
#                     payload=message.payload.decode()
#                 )
#                 print(data)
#                 topic_parts = data['topic'].split('/')
#                 sensor_type = topic_parts[1]
#                 sensor_id = topic_parts[2]
#                 if sensor_type not in sensor_data:
#                     sensor_data[sensor_type] = {}
#                 sensor_data[sensor_type][sensor_id] = data['payload']
#                 # socketio.emit(f'{sensor_type}_data', json.dumps(sensor_data[sensor_type]))
#                 if Window and MQTT_receiver.main_window:
#                     print("[INFO] update the GUI form the reciever...")
#                     Window.update_status_by_id(MQTT_receiver.main_window, sensor_type, sensor_id, data['payload'])
#                 else:
#                     print("There is no Window Class for GUI")
#                 Controller.insert_reading(sensor_type, sensor_id, data['payload'])
#                 insertion_event.set()

#             except Exception as e:
#                 print("error in mqtt socket sender")

#     @staticmethod
#     def mqtt_client_thread():
#         MQTT_receiver.mqtt_client.on_connect = MQTT_receiver.on_connect
#         MQTT_receiver.mqtt_client.on_message = MQTT_receiver.on_message
#         MQTT_receiver.mqtt_client.connect(mqtt_configuration['broker'], mqtt_configuration['port'], mqtt_configuration['keep_alive'])
#         MQTT_receiver.mqtt_client.subscribe("#")
#         while not exit_event.is_set():
#             MQTT_receiver.mqtt_client.loop(timeout=1.0)  # Adjust the timeout as needed

#         MQTT_receiver.mqtt_client.disconnect()
#         print("MQTT receiver is disconnected and thread exiting.")

    
