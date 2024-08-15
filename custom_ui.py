# -*- coding: utf-8 -*-

# Early alarm system GUI
# Created by: Ahmed Khaled @ Micropolis Robotics
#

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow, QShortcut, QStackedWidget, QPushButton, QMenu, QAction, QVBoxLayout, QScrollArea, QGraphicsBlurEffect, QWidget, QLabel, QLineEdit, QGridLayout, QHBoxLayout
)
from PyQt5 import QtGui
from PyQt5.QtGui import QKeySequence, QPainter, QBrush, QColor

from Home_KIT_UI.home_kit_ui import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QPoint
from constants import *
from globals import exit_event, insertion_event, items_configuration, session, GLOBAL_VERBOSE, SHOW_ID_WITH_NAME
from utils import helpers, OptionsMenu, BlurredOverlay, AddButtonOptions, AddRoomDialog, AddAccessoryDialog
from database import Controller

class Window(QMainWindow, Ui_MainWindow):
    update_items_signal = pyqtSignal(str, int, str)

    def __init__(self, parent=None, handler = None):
        # Constents
        self.acuators = ["switch", "siren"]
        
        # This is a MQTT function to call when stop your APP to terminate threads of MQTT When close the app
        self.thread_terminaiton_handler = None
        self.handler = handler

        # GUI Manage Dialogs
        self.dialog = None
        self.blur_layer = None

        # Load fonts
        self.preloads()

        super().__init__(parent)
        self.update_items_signal.connect(self.update_status_by_id)
        self.setupUi(self)     

        # connect to database
        self.controller = Controller(session=session)
        # print(self.controller.general_insert(1, 2,"living room", [{
        #     "id": 11,
        #     "type": "siren",
        #     "status":"off",
        #     "name": "back siren",
        #     "cp": "LoRa"
        # }]))
        data = self.controller.start()
        self.rooms_data = data["rooms_data"]
        self.create_dashboard()
        # # self.actions = data['actions']
        # self.items_data = data['items_data']


        # Add Accessory 
        # helpers.add_accessory(self, self.gridLayout, "door_sensor", 10, "UNKOWN", "closed", 5, 3)
        # helpers.add_accessory(self, self.gridLayout, "switch", 11, "UNKOWN", "off", 5, 3)
        # helpers.add_accessory(self, self.gridLayout, "door_sensor", 11, "UNKOWN", "opened", 5, 3)
        # helpers.add_accessory(self, self.gridLayout, "motion_sensor", 11, "UNKOWN", "No Motion", 5, 3)
        # # self.add_accessory(self.gridLayout, "door_sensor", 10, "UNKOWN", "closed", 5, 3)
        # self.add_accessory(self.gridLayout, "door_sensor", 11, "UNKOWN", "opened", 5, 3)
        

        # Set icon, name of the applicaiton, and set the shortcuts
        # connect the function of add_button
        # Rearrange the items of the dashboard
        self.postloads()
    
      
    def create_dashboard(self):
        _translate = QtCore.QCoreApplication.translate

        for room in self.rooms_data:
            room_data = room.get("dashboard", None)
            room_id = room_data.get('dashboard_id')
            room_text = room_data.get("dashboard_name", "unkown room name")

            ## Label
            room_name = QtWidgets.QLabel(self.container)
            room_name.setEnabled(True)
            room_name.setLayoutDirection(QtCore.Qt.LeftToRight)
            room_name.setStyleSheet(Style.ROOM_NAME)
            # {'dashboard_id': 1, 'dashboard_name': 'home', 'user_id': 1, 'user_name': 'admin'}
            room_name.setObjectName("room_name_" + str(room_id))
            room_name.setText(_translate("MainWindow", room_text))
            self.verticalLayout_2.addWidget(room_name)

            ## Grid Container
            gridLayout = QtWidgets.QGridLayout()

            gridLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
            gridLayout.setSpacing(16)
            gridLayout.setObjectName("gridLayout_" + str(room_id))
            self.verticalLayout_2.addLayout(gridLayout)

            # Room Accessories
            accessories_data = room.get("accessories_data", None)
            # print(len(accessories_data))
            self.additems(room_id, accessories_data) # accessories_data[:1] if len(accessories_data) else None


    def additems(self, room_id, accessories_data):
        if accessories_data == None or accessories_data == []:
            return None

        for item in accessories_data:
            pos = item.get('position', None)
            if pos:
                num = int(pos) 
            else: 
                num = -1
            
            row = num // Layout.MAX_COLS
            col = num - (row * Layout.MAX_COLS)
            type = item['type']
            id = item['id']
            status = item["status"]
            try: 
                room_container = self.findChild(QGridLayout, "gridLayout_" + str(room_id))
                helpers.add_accessory(self, room_container, type, id, "UNKOWN" if not SHOW_ID_WITH_NAME else "UNKOWN" + str(id), status, row, col)
            except Exception as e:
                print(f"type: {type} id: {id} pos: {pos} error: {e}")


    def update_status_by_id(self, type, id, status):
        """
            Be sure to check the id and status if exist or valid data before use this function 
            Note: the check already did in on_message function
            
        """
        id_str = str(id)
        gb_bx = self.findChild(QtWidgets.QGroupBox, "accessory_box_"+ type + "_" + id_str)
        if gb_bx:
            accessory_status = gb_bx.findChild(QLabel, "accessory_status_" + type + "_" + id_str)
            # the status is the same of the current status
            if accessory_status.text() != status:
                helpers.accessory_update_status(gb_bx, type, id, status, CALLBACK=self.update_data_for_accessory)
        return None

    def accessory_toggle_handler(self):
        button = self.sender()

        type, id = helpers.get_type_and_id_of_accessory(button.parent())
        if type in self.acuators:
            accessory_all_data = helpers.find_accessory_data(self.rooms_data, type, id)
            room_data, accessory_data = accessory_all_data.get("room_data", None), accessory_all_data.get("accessory_data", None)
            status  = accessory_data['status']
            type    = accessory_data['type']

            if status == "on":
                new_staus = "off"
            elif status == "off":
                new_staus = "on"
            else:
                return None # stop wrong status

            # update GUI and the CALLBACK for update the current copy of data's database
            helpers.accessory_update_status(button.parent(), type, id, new_staus, CALLBACK=self.update_data_for_accessory)
            if self.handler:
                self.handler(type, id, new_staus)
            else:
                print("[Warning]: Can't publish your message...")
            # TODO
            # update database
        else:
            if GLOBAL_VERBOSE:
                print("[Warning]: This is not an acuator item")

    def update_data_for_accessory(self, type, id, new_status, VERBOSE = GLOBAL_VERBOSE):
        for room in self.rooms_data:
            accessories_data = room.get("accessories_data", None) 

            if accessories_data is not None:
                for accessory_data in accessories_data:
                    dtype = accessory_data.get('type')
                    did = accessory_data.get('id')

                    if dtype == type and did == id:
                        accessory_data['status'] = new_status
                        if VERBOSE:
                            print(f"Updated {type} with ID {id} to new status: {new_status}")
                        return True  # Return True if update is successful
        return False  # Return False if no update was made
    
    def add_overlay_menu(self):
        # button_position = self.add_button.mapToGlobal(QPoint(0, 0))
        # if GLOBAL_VERBOSE:
        #     print(f"Button position: {button_position}")  # Debug print
        
        if self.dialog:
            self.dialog.close()

        self.dialog = AddButtonOptions(self)
        print(self.x()+ 650, self.y())
        # self.dialog.setGeometry(650, 0, 254, 162) # - 228 + 58
        # x_pos = self.x() + 650
        # y_pos = self.y()
        # self.dialog.move(x_pos, y_pos)
        # self.dialog.resize(254, 162)
        if GLOBAL_VERBOSE:
            print("AddButtonOptions geometry set")  # Debug print

        if self.blur_layer:
            self.blur_layer.close()

        self.blur_layer = BlurredOverlay(self)
        # self.blur_layer.setGeometry(self.x(), self.y(), self.width(), self.height())
        self.blur_layer.show()
        if GLOBAL_VERBOSE:
            print("BlurredOverlay shown")  # Debug print
        self.dialog.show()
        # self.dialog.raise_()
        # self.dialog.activateWindow()
        if GLOBAL_VERBOSE:
            print("AddButtonOptions shown")  # Debug print  
    
    def clean_up_overlay(self):
        if self.blur_layer:
            self.blur_layer.close()
            self.blur_layer = None
        if GLOBAL_VERBOSE:
            print("Overlay cleaned up")  # Debug print    

    def accessory_option_handler(self):
        button = self.sender()
        pos = button.mapToGlobal(button.rect().bottomLeft())
        menu = OptionsMenu(self, accessory_source = button.parent())
        menu.show_menu(pos)

    def edit_widget(self, widget):
        print("Edit widget")

    def delete_widget(self, widget):
        widget.setParent(None)  # Remove widget from layout and delete it
        widget.deleteLater()
        self.populate_grid() # Rearrange items
        print("Widget deleted")
    
    def open_add_room_dialog(self):
        if self.dialog:
            self.dialog.close()
        
        self.dialog = AddRoomDialog(self)
        w = self.width() - (self.width() * 2 // 3)
        h = self.height() * 1 // 3
        x = self.x() + ( self.width() - w ) // 2
        keyboard_height = self.height() * 1 // 3
        y = self.y() + ( self.height() - keyboard_height - h ) // 2 
        self.dialog.setGeometry(x, y, w, h)
        
        if self.blur_layer:
            self.blur_layer.close()

        self.blur_layer = BlurredOverlay(self)
        self.blur_layer.setGeometry(self.x(), self.y(), self.width(), self.height())
        self.blur_layer.show()

        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()

    def open_add_accessory_dialog(self):
        if self.dialog:
            self.dialog.close()
        
        self.dialog = AddAccessoryDialog(self)
        w = self.width() - (self.width() * 2 // 3)
        h = self.height() * 2.3 // 3
        x = self.x() + ( self.width() - w ) // 2
        # keyboard_height = self.height() * 1 // 3
        y = self.y() + 30  #self.y() + ( self.height() - keyboard_height - h ) // 2 
        self.dialog.setGeometry(x, y, w, h)
        
        if self.blur_layer:
            self.blur_layer.close()

        self.blur_layer = BlurredOverlay(self)
        self.blur_layer.setGeometry(self.x(), self.y(), self.width(), self.height())
        self.blur_layer.show()

        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()

    def on_resize(self, event):
        self.populate_grid()
        event.accept()  
 
    def populate_grid(self):
        cols = self.calculate_columns()
        for layout in self.findChildren(QGridLayout):
            # layout.setSpacing(16)

            # 1- Get Items in the layout
            items = self.get_grid_elements(layout)

            # 2- Clear the layout from any item
            self.clear_grid_layout(layout)

            # 3- Rearrange items
            for i, element in enumerate(items):
                row = i // cols
                col = i % cols
                layout.addWidget(element, row, col)

    def calculate_columns(self):
        # Adjust the number of columns based on the window width
        width = self.size().width() 
        cols = width // (220) # 220 this number by trying and error 
        return cols
    
    def get_grid_elements(self, layout):
        # Get the number of rows in the grid layout
        rows = range(layout.rowCount())
        cols = range(layout.columnCount())
        elements = []
        c = 0
        for row in rows:
            # Iterate through each column in the current row
            for col in cols: 
                c += 1           
                item = layout.itemAtPosition(row, col)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        elements.append(widget)
                # else:
                #     print(row, col)
        return elements
    
    def clear_grid_layout(self, grid_layout):
        while grid_layout.count():
            item = grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()  # Safely deletes the widget
                widget.setParent(None)
            else:
                # If the item is a layout, recursively clear it
                sub_layout = item.layout()
                if sub_layout is not None:
                    self.clear_grid_layout(sub_layout)
            grid_layout.removeItem(item)   

    def preloads(self):
        font_paths = [
            ":/fonts/resources/fonts/Poppins/Poppins-Black.ttf",
            ":/fonts/resources/fonts/Poppins/Poppins-BlackItalic.ttf",
            ":/fonts/resources/fonts/Poppins/Poppins-Bold.ttf",
            ":/fonts/resources/fonts/Poppins/Poppins-BoldItalic.ttf",
            ":/fonts/resources/fonts/Poppins/Poppins-ExtraBold.ttf",
            ":/fonts/resources/fonts/Poppins/Poppins-ExtraBoldItalic.ttf",
            ":/fonts/resources/fonts/Poppins/Poppins-ExtraLight.ttf",
            ":/fonts/resources/fonts/Poppins/Poppins-ExtraLightItalic.ttf",
            ":/fonts/resources/fonts/Poppins/Poppins-Italic.ttf",
            ":/fonts/resources/fonts/Poppins/Poppins-Light.ttf",
            ":/fonts/resources/fonts/Poppins/Poppins-LightItalic.ttf",
            ":/fonts/resources/fonts/Poppins/Poppins-Medium.ttf",
            ":/fonts/resources/fonts/Poppins/Poppins-MediumItalic.ttf",
            ":/fonts/resources/fonts/Poppins/Poppins-Regular.ttf",
            ":/fonts/resources/fonts/Poppins/Poppins-SemiBold.ttf",
            ":/fonts/resources/fonts/Poppins/Poppins-SemiBoldItalic.ttf",
            ":/fonts/resources/fonts/Poppins/Poppins-Thin.ttf",
            ":/fonts/resources/fonts/Poppins/Poppins-ThinItalic.ttf"
        ]
        
        # Add fonts to the Qt font database
        for ttf_file in font_paths:
            # self.font_database.addApplicationFont(ttf_file)
            id = QtGui.QFontDatabase.addApplicationFont(ttf_file)
            if id < 0: print("Error")
            families = QtGui.QFontDatabase.applicationFontFamilies(id)
            # print(families[0])

    def postloads(self):
        # Set Icon
        self.setWindowIcon(QtGui.QIcon(':/logo/resources/logo/Home Kit Logo.png'))
        # set the title
        self.setWindowTitle("Home Kit")

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Create a keyboard shortcut Ctrl+M
        shortcut = QKeySequence(Qt.CTRL + Qt.Key_C)
        self.shortcut = QShortcut(shortcut, self)
        self.shortcut.activated.connect(self.terminate)

        self.add_button.clicked.connect(self.add_overlay_menu)
        
        # Rearrange accessories when resize and at the begining of the app to make the app responsive
        self.resizeEvent = self.on_resize

    def terminate(self):
        exit_event.set()
        if self.thread_terminaiton_handler:
            self.thread_terminaiton_handler()
        self.close()

    def set_thread_terminaiton_handler(self, handler = None):
        if handler:
            self.thread_terminaiton_handler = handler
