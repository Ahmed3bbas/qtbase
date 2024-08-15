import paho.mqtt.client as mqtt
from MQTT_services.MQTT import MQTT
from MQTT_services.MQTT_receiver import MQTTReceiverThread
from MQTT_services.MQTT_publisher import MQTTPublisherThread
# from database import Controller

class MQTT_client:
    def __init__(self, main_window) -> None:
        MQTT.main_window = main_window
        MQTT.mqtt_client = mqtt.Client()
        

    @staticmethod
    def run_reciever():
        mqtt_thread = MQTTReceiverThread()
        mqtt_thread.start()
        return mqtt_thread
    

    @staticmethod
    def run_publisher():
        mqtt_thread = MQTTPublisherThread()
        mqtt_thread.start()
        return mqtt_thread
    
        
    def run(self):
        try:
            self.mqtt_receiver_thread = MQTT_client.run_reciever()
            self.mqtt_publisher_thread = MQTT_client.run_publisher()
        except:
            print("[ERROR]: when creating threads")
    
    def stop(self):
        self.mqtt_receiver_thread.stop()
        self.mqtt_publisher_thread.stop()

        # Wait for threads to finish
        self.mqtt_receiver_thread.wait()
        self.mqtt_publisher_thread.wait()

    @staticmethod
    def handle_user_commands(type, id, status):
        MQTTPublisherThread.publish_message(type, id, status)
























##########################################################################################################
# import paho.mqtt.client as mqtt
# from MQTT_services.MQTT import MQTT
# from MQTT_services.MQTT_publisher import MQTT_publisher
# from MQTT_services.MQTT_receiver import MQTT_receiver
# import threading
# from database import Controller

# class MQTT_client:
#     def __init__(self, main_window) -> None:
#         MQTT.main_window = main_window
#         MQTT.mqtt_client = mqtt.Client()

#     @staticmethod
#     def run_reciever():
#         if MQTT_receiver.main_window:
#             mqtt_thread = threading.Thread(target=MQTT_receiver.mqtt_client_thread)
#             # mqtt_thread.daemon = True  # Set the thread as a daemon so it exits when the main program exits
#             mqtt_thread.start()
#             print("MQTT Receiver is run sucessfully...")
#             return mqtt_thread
#         else:
#             print("You have to set mainwindow like this: (MQTT_client(`window obj`)")

#     @staticmethod
#     def run_publisher():
#         if MQTT_publisher.main_window and MQTT_publisher.mqtt_client:
#             t = threading.Thread(target=MQTT_publisher.check_push_alerts)
#             t.start()
#             print("MQTT Publisher is run sucessfully...")
#             return t
#         else:
#             print("You have to set mainwindow like this: (MQTT_client(`window obj`) or mqtt client not intialized")
#             return None
        
#     def run(self):
#         try:
#             mqtt_receiver_thread    = MQTT_client.run_reciever()
#             mqtt_publisher_thread   = MQTT_client.run_publisher()
#         except:
#             print("[ERROR]: when creating threads")
    
#     @staticmethod
#     def handle_user_commands(type, id, status):
#         print(type, id, status)
#         if MQTT_publisher.mqtt_client:
#             # MQTT_publisher.handle_actuator_command({'type': type, 'id': id, 'value': status})
#             MQTT_publisher.mqtt_client.publish(f'micropolis/{type}/{id}', status)
#             #Controller.insert_reading(type, id, status)
#         else:
#             print("[ERROR] Client is not defined")
        


