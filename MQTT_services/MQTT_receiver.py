from PyQt5.QtCore import QThread, pyqtSignal
from controller import Controller
from custom_ui import Window
from globals import  exit_event, mqtt_configuration, GLOBAL_VERBOSE
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
            accessory_type = topic_parts[1]
            accessory_id = topic_parts[2]
            # if accessory_type not in sensor_data:
            #     sensor_data[accessory_type] = {}
            # sensor_data[accessory_type][accessory_id] = data['payload']
            if Controller.check_item_totally(accessory_type, accessory_id, data['payload']):
                if Window and MQTT_receiver.main_window:
                    if GLOBAL_VERBOSE:
                        print("[INFO] update the GUI form the reciever...")
                    MQTT_receiver.main_window.update_items_signal.emit(accessory_type, accessory_id, data['payload'])
                else:
                    print("There is no Window Class for GUI")
                # update the database 
                Controller.add_record(
                    {
                        "id": accessory_id,
                        "value": data['payload']
                    }) # database updated and session
            else:
                print("[WARNING]: message recived from MQTT is not valid", f"accessory_type: {accessory_type}, id: {accessory_id}, status: {data['payload']}")
            # insertion_event.set()

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


