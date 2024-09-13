from PyQt5.QtCore import QThread
from MQTT_services.MQTT import MQTT
# from database import create_database_object
from controller import Controller
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
    def do_action(automation_id):
        automations = Controller.session.get("automations", None)
        if automations:
            for automation in automations:
                if automation["id"] == automation_id:
                    break
            actions = automation.get("actions", None)
        # actions = object.get_actions(action_id)
        list_of_actions = []
        for action in actions:
            order = int(action["sequence"])
            sec = action["duration"]
            actuator_id = action["actuator_id"]
            list_of_actions.insert(order - 1, (actuator_id, sec))
        # for i in actions.keys():
        #     for value in actions[i]:
        #         if i == 'duration':
        #             sec, order = value
        #             list_of_actions.insert(order - 1, (i, sec))
        #         else:
        #             id, status, order = value
        #             list_of_actions.insert(order - 1, (i, id, status))

        for tup in list_of_actions:
            # if tup[0] == 'siren' or tup[0] == 'switch':
            actuator_id = tup[0]
            duration    = int(tup[1])
            detatils = Controller.get_accessory_details(actuator_id)
            type     = detatils["type"]
            data = {'type': type, 'id': actuator_id, 'value': "On"}
            MQTT_publisher.handle_actuator_command(data)
            
            data = {'type': type, 'id': actuator_id, 'value': "Off"}
            time.sleep(duration)
            MQTT_publisher.handle_actuator_command(data)
    
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
        user_id = Controller.session.get("user_id")
        if MQTT_publisher.main_window and MQTT_publisher.mqtt_client:
            if GLOBAL_VERBOSE:
                print("MQTT Publisher is run successfully...")
            while True:
                try:
                    # db_manager = create_database_object()
                    alerts = Controller.get_alerts(user_id)
                    # if len(alerts) > 0:
                    for alert in alerts:
                        automation_id = alert
                        self.do_action_thread(automation_id)
                        Controller.reset_alert(automation_id)
                    # db_manager.disconnect()
                    time.sleep(1)

                except Exception as e:
                    print("[ERROR]: in push alerts:", e)
                    # obj = create_database_object()
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
    
    def do_action_thread(self, automation_id):
        try:
            MQTT_publisher.do_action(automation_id)
        except:
            print("[ERROR]: when do action is running...")

    @staticmethod
    def publish_message(type, id, status):
        MQTT_publisher.publish_message(type, id, status)




