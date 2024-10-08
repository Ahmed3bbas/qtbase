# -*- coding: utf-8 -*-

# Early alarm system GUI
# Created by: Ahmed Khaled @ Micropolis Robotics
#

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow, QShortcut, QLabel, QGridLayout, QDialog
)
from PyQt5 import QtGui
from PyQt5.QtGui import QKeySequence

from Home_KIT_UI.home_kit_ui import Ui_MainWindow
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, Qt, QPoint
from constants import Layout
from globals import exit_event, session, GLOBAL_VERBOSE, SHOW_ID_WITH_NAME, acuators
from utils import helpers, OptionsMenu, BlurredOverlay, AddButtonOptions, AddRoomDialog, AddAccessoryDialog, DeleteAccessoryDialog
from controller import Controller
from PyQt5.QtWidgets import QScroller

class Window(QMainWindow, Ui_MainWindow):
    update_items_signal = pyqtSignal(str, int, str)

    def __init__(self, parent=None, handler = None):
        # Constents
        self.acuators = acuators
        
        # This is a MQTT function to call when stop your APP to terminate threads of MQTT When close the app
        self.thread_terminaiton_handler = None
        self.mqtt_publish_handler = handler

        # GUI Manage Dialogs
        self.dialog = None
        self.blur_layer = None

        # Load fonts
        self.preloads()

        super().__init__(parent)
        self.update_items_signal.connect(self.update_status_by_id)
        self.setupUi(self)    
        QScroller.grabGesture(self.scrollArea.viewport(), QScroller.LeftMouseButtonGesture) 

        # connect to database
        self.controller = Controller(session=session)

        # Added for testing it will removed in production
        with Controller.with_db_connection() as db_manager:
            if db_manager.get_users():
                # Don't create user
                pass
            else:
                db_manager.add_user('john_doe', 'securepassword', 'Admin')
                print("user created successfuly")

        # connect with database at begining and get the data of the user
        self.controller.start()

        # After getting data create dashboard
        self.create_dashboard()
        
        # Set icon, name of the applicaiton, and set the shortcuts
        # connect the function of add_button
        # Rearrange the items of the dashboard
        self.postloads()
       
    def create_dashboard(self):
        room_data = Controller.session.get("rooms_data", None)
        for room_id in room_data:
            room = room_data[room_id]
            room_text = room.get("room_name", "unkown room name")
            accessories_data = room.get("accessories", None)

            helpers.add_room(self, room_id, room_text)

            # Room Accessories
            # room_accessories_data = [acc for acc in accessories_data if acc["room_id"] == room_id]# room.get("accessories_data", None)
            # print(len(accessories_data))
            self.additems(room_id, accessories_data) # accessories_data[:1] if len(accessories_data) else None

    def additems(self, room_id, accessories_data):
        if accessories_data == None or accessories_data == []:
            return None

        for item in accessories_data:
            # print(item)
            pos = item.get('accessory_position', None)
            if pos is not None or pos >= 0:
                num = int(pos) 
            else: 
                num = -1
            
            row = num // Layout.MAX_COLS
            col = num - (row * Layout.MAX_COLS)
            # print(row, col)
            type = item['accessory_type']
            id = item['accessory_id']
            status = item["current_status"]
            if status is None:
                status = Controller.get_defalut_status(type)
    
            name   = item.get("accessory_name", "UNKOWN")
            name   = name if name else "UNKOWN"
            try: 
                room_container = self.findChild(QGridLayout, "gridLayout_" + str(room_id))
                # print(item)
                helpers.add_accessory(self, room_container, type, id, name if not SHOW_ID_WITH_NAME else name + str(id), status, row, col)
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
                helpers.accessory_update_status(gb_bx, type, id, status) # , CALLBACK=self.update_accessory_data_in_session)
        return None

    def accessory_toggle_handler(self, clicked_object):
        # clicked_obj = self.sender()
        if isinstance(clicked_object, QtWidgets.QToolButton):
            clicked_object = clicked_object.parent()

        type, id = helpers.get_type_and_id_of_accessory(clicked_object) # clicked_obj.parent()
        rooms_data = Controller.session.get("rooms_data", None)
        # print(rooms_data)
        if type in self.acuators:
            for room_id in rooms_data:
                accessories_data = rooms_data[room_id]["accessories"]
                accessory_data = [acc for acc in accessories_data if acc["accessory_id"] == id] # helpers.find_accessory_data(self.accessories_data, type, id)
                if accessory_data:
                    accessory_data = accessory_data[0]
                    status  = accessory_data['current_status']
                    type    = accessory_data['accessory_type']
                    break
            # print(accessory_data)

            if status == "On":
                new_staus = "Off"
            elif status == "Off":
                new_staus = "On"
            else:
                return None # stop wrong status

            # update GUI and the CALLBACK for update the current copy of data's database
            helpers.accessory_update_status(clicked_object, type, id, new_staus)#, CALLBACK=self.update_accessory_data_in_session)
            
            if self.mqtt_publish_handler:
                self.mqtt_publish_handler(type, id, new_staus)
            else:
                print("[Warning]: Can't publish your message...")
        else:
            if GLOBAL_VERBOSE:
                print("[Warning]: This is not an acuator item")
    
    def add_overlay_menu(self):
        button_position = self.add_button.mapToGlobal(QPoint(0, 0))
        if GLOBAL_VERBOSE:
            print(f"Button position: {button_position}")  # Debug print
        
        if self.dialog:
            self.dialog.close()

        self.dialog = AddButtonOptions(self)
        self.dialog.setGeometry(button_position.x() - 228 , button_position.y() + 58, 254, 162)
        if GLOBAL_VERBOSE:
            print("AddButtonOptions geometry set")  # Debug print

        if self.blur_layer:
            self.blur_layer.close()

        self.blur_layer = BlurredOverlay(self)
        self.blur_layer.setGeometry(self.x(), self.y(), self.width(), self.height())
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
        # TODO
        print("Edit widget")

    def delete_widget(self, widget):
        dialog = DeleteAccessoryDialog()
        if dialog.exec_() == QDialog.Accepted:
            

            # update the database
            # +Update session
            type, id = helpers.get_type_and_id_of_accessory(widget)
            delete_data = Controller.delete_accessory(accessory_id = id)
            if delete_data.get("status", False):
                # Update the dashboard
                widget.deleteLater()
                widget.setParent(None)  # Remove widget from layout and delete it

                self.populate_grid() # Rearrange items
            else:
                print(delete_data)
            # clode Dialog
            dialog.close()
        
    def open_add_room_dialog(self):
        if self.dialog:
            self.dialog.close()
        
        self.dialog = AddRoomDialog(self)
        w = int(self.width() - (self.width() * 2 // 3))
        h = int(self.height() * 1 // 3)
        x = int(self.x() + ( self.width() - w ) // 2)
        keyboard_height = self.height() * 1 // 3
        y = int(self.y() + ( self.height() - keyboard_height - h ) // 2) 
        self.dialog.setGeometry(x, y, w, h)
        
        # if self.blur_layer:
        #     self.blur_layer.close()

        # self.blur_layer = BlurredOverlay(self)
        # self.blur_layer.setGeometry(self.x(), self.y(), self.width(), self.height())
        # self.blur_layer.show()

        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()

    def open_add_accessory_dialog(self):
        rooms_info = set()
        accessory_ids = set()
        rooms_data =  Controller.session.get("rooms_data", None)
        for room_id in rooms_data:
            room = rooms_data[room_id]
            room_name = room['room_name']
            rooms_info.add((room_id, room_name))
            accessories = room.get("accessories", None)
            
            for accessory in accessories:
                accessory_id = accessory.get('accessory_id')
                if accessory_id is not None:
                    accessory_ids.add(accessory_id)

        if self.dialog:
            self.dialog.close()
        
        self.dialog = AddAccessoryDialog(self, accessory_ids, rooms_info = rooms_info, accessories_types = Controller.session.get("accessories_types", None), communication_protocols = Controller.session.get("communication_protocols", None))
        w = int(self.width() - (self.width() * 2 // 3))
        h = int(self.height() * 2.3 // 3)
        x = int(self.x() + ( self.width() - w ) // 2)
        # keyboard_height = self.height() * 1 // 3
        y = int(self.y() + 30)  #self.y() + ( self.height() - keyboard_height - h ) // 2 
        self.dialog.setGeometry(x, y, w, h)
        
        # if self.blur_layer:
        #     self.blur_layer.close()

        # self.blur_layer = BlurredOverlay(self)
        # self.blur_layer.setGeometry(self.x(), self.y(), self.width(), self.height())
        # self.blur_layer.show()

        self.dialog.show()
        # self.dialog.raise_()
        # self.dialog.activateWindow()

    def on_resize(self, event):
        self.populate_grid()
        event.accept()  
 
    def populate_grid(self):
        cols = self.calculate_columns()
        # delay_in_msec = 10
        for layout in self.findChildren(QGridLayout):
            # layout.setSpacing(16)

            # 1- Get Items in the layout
            items = self.get_grid_elements(layout)
            # print(items)
            # print(layout, items)

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
        # c = 0
        for row in rows:
            # Iterate through each column in the current row
            for col in cols: 
                # c += 1           
                item = layout.itemAtPosition(row, col)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        elements.append(widget)
                # else:
                #     print(row, col)
        return elements
    
    # def clear_grid_layout(self, grid_layout):
    #     while grid_layout.count():
    #         item = grid_layout.takeAt(0)
    #         widget = item.widget()
    #         if widget is not None:
    #             widget.deleteLater()  # Safely deletes the widget
    #             widget.setParent(None)
    #         else:
    #             # If the item is a layout, recursively clear it
    #             sub_layout = item.layout()
    #             if sub_layout is not None:
    #                 self.clear_grid_layout(sub_layout)
    #         grid_layout.removeItem(item)   

    def clear_grid_layout(self, grid_layout):
        # Safely removes widgets without deleting them (so they can be reused)
        while grid_layout.count():
            item = grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                grid_layout.removeWidget(widget)
                widget.setParent(None)  # Detach widget from its parent to remove it from the layout
            else:
                # If the item is a layout, recursively clear it
                sub_layout = item.layout()
                if sub_layout is not None:
                    self.clear_grid_layout(sub_layout)

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
