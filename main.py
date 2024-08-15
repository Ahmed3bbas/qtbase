from custom_ui import  Window
from PyQt5.QtWidgets import QApplication
import sys
from PyQt5 import QtGui
# from database import Controller
from MQTT_services.MQTT_client import MQTT_client
# from globals import session

if __name__ == "__main__":
    # obj = Controller(session)

    app = QApplication(sys.argv)
    win = Window(handler= MQTT_client.handle_user_commands)
    # win = Window(controller = obj, handler=MQTT_client.handle_user_commands)


    client = MQTT_client(win)
    win.set_thread_terminaiton_handler(client.stop) # set the terminsation funciton of the thread to close the threads before close the main application 
    client.run()

    win.show()
    sys.exit(app.exec())
    
