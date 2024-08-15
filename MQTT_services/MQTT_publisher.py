from PyQt5.QtCore import QThread
from MQTT_services.MQTT import MQTT
from database import create_database_object
from globals import exit_event, GLOBAL_VERBOSE
from custom_ui import Window
import time



class MQTT_publisher(MQTT):
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def handle_actuator_command(data):
        try:
            actuator_type = data['type']
            actuator_id = data['id']
            actuator_value = data['value']
            if GLOBAL_VERBOSE:
                print(data)
            MQTT_publisher.publish_message(actuator_type, actuator_id, actuator_value)
            # MQTT_publisher.mqtt_client.publish(f'micropolis/{actuator_type}/{actuator_id}', actuator_value)

            # update in GUI
            if Window and MQTT_publisher.main_window:
                if GLOBAL_VERBOSE:
                    print("[INFO] update the GUI form the Publisher...")
                # Window.update_status_by_id(MQTT_publisher.main_window, actuator_type, actuator_id, actuator_value)
                MQTT_publisher.main_window.update_items_signal.emit(MQTT_publisher.main_window, actuator_type, int(actuator_id), actuator_value)
            else:
                print("[ERROR]: there is no Window class or you are not initialized window object")
        except:
            print("[ERROR]: in send mqtt command")

    @staticmethod
    def do_action(action_id, object):
        actions = object.get_actions(action_id)
        list_of_actions = []
        for i in actions.keys():
            for value in actions[i]:
                if i == 'time':
                    sec, order = value
                    list_of_actions.insert(order - 1, (i, sec))
                else:
                    id, status, order = value
                    list_of_actions.insert(order - 1, (i, id, status))

        for tup in list_of_actions:
            if tup[0] == 'siren' or tup[0] == 'switch':
                data = {'type': tup[0], 'id': tup[1], 'value': tup[2]}
                MQTT_publisher.handle_actuator_command(data)
            else:
                time.sleep(int(tup[1]))
    
    @staticmethod
    def publish_message(type, id, status):
        # print(type, id, status)
        if MQTT_publisher.mqtt_client:
            MQTT_publisher.mqtt_client.publish(f'micropolis/{type}/{id}', status)
        else:
            print("[ERROR] Client is not defined")


class MQTTPublisherThread(QThread):
    def __init__(self):
        super().__init__()
        self._stop_event = True
    
    def run(self):
        if MQTT_publisher.main_window and MQTT_publisher.mqtt_client:
            if GLOBAL_VERBOSE:
                print("MQTT Publisher is run successfully...")
            while True:
                try:
                    obj = create_database_object()
                    rows = obj.get_push_alert()
                    if rows:
                        for row in rows:
                            event_id, action_id = row
                            self.do_action_thread(action_id)
                            obj.delete_push_alert(action_id)
                    obj.disconnect()
                    time.sleep(1)

                except Exception as e:
                    print("[ERROR]: in push alerts:", e)
                    obj = create_database_object()
                finally:
                    if exit_event.is_set():
                        if GLOBAL_VERBOSE:
                            print("MQTT publisher is disconnected and thread exiting.")
                        break
        else:
            print("You have to set mainwindow like this: (MQTT_client(`window obj`) or mqtt client not initialized")
            return None
    def stop(self):
        self._stop_event = True
    
    def do_action_thread(self, action_id):
        try:
            MQTT_publisher.do_action(action_id, create_database_object())
        except:
            print("[ERROR]: when do action is running...")

    @staticmethod
    def publish_message(type, id, status):
        MQTT_publisher.publish_message(type, id, status)
















##########################################################################################################
# import time
# from MQTT_services.MQTT import MQTT
# from database import create_database_object
# import threading
# import time
# from globals import exit_event
# from custom_ui import Window

# class MQTT_publisher(MQTT):
#     def __init__(self) -> None:
#         pass
    
#     @staticmethod
#     def handle_actuator_command(data):
#         try:
#             actuator_type = data['type']
#             actuator_id = data['id']
#             actuator_value = data['value']
#             print(data)
#             MQTT_publisher.mqtt_client.publish(f'micropolis/{actuator_type}/{actuator_id}', actuator_value)

#             # update in GUI
#             if Window and MQTT_publisher.main_window:
#                 print("[INFO] update the GUI form the Publisher...")
#                 Window.update_status_by_id(MQTT_publisher.main_window, actuator_type, actuator_id, actuator_value)
#             else:
#                 print("[ERROR]: there is no Window class or you are not intilaized window object")
#         except:
#             print("error in send mqtt command")

#     @staticmethod
#     def do_action(action_id, object):
#         actions = object.get_actions(action_id)
#         list_of_actions = []
#         for i in actions.keys():
#             for value in actions[i]:
#                 if i == 'time':
#                     sec, order = value
#                     list_of_actions.insert(order - 1, (i, sec))
#                 else:
#                     id, status, order = value
#                     list_of_actions.insert(order - 1, (i, id, status))

#         for tup in list_of_actions:
#             if tup[0] == 'siren' or tup[0] == 'switch':
#                 data = {'type': tup[0], 'id': tup[1], 'value': tup[2]}
#                 MQTT_publisher.handle_actuator_command(data)
#             else:
#                 time.sleep(int(tup[1]))

#     @staticmethod
#     def do_action_thread(action_id):
#         # Perform the necessary action
#         try:
#             MQTT_publisher.do_action(action_id, create_database_object())
#             # mqtt_client.publish('alarm_door')

#         except:
#             print("Error when do action is running...")

    
#     # Function to check for new rows periodically
#     @staticmethod
#     def check_push_alerts():
#         while True:
#             try:
#                 obj = create_database_object()
#                 rows = obj.get_push_alert()
#                 if rows:
#                     for row in rows:
#                         event_id, action_id = row
#                         t = threading.Thread(target=MQTT_publisher.do_action_thread, args=(action_id,))
#                         t.start()
#                         obj.delete_push_alert(action_id)
#                 obj.disconnect()
#                 time.sleep(1)

#             except Exception as e:
#                 print("Error in push alerts:", e)
#                 obj = create_database_object()
#             finally:
#                 if exit_event.is_set():
#                     print("MQTT publisher is disconnected and thread exiting.")
#                     break



