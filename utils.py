from PyQt5.QtWidgets import QFrame, QGridLayout, QGroupBox, QLabel, QToolButton, QWidget, QShortcut, QApplication, QGraphicsScene, QGraphicsPixmapItem, QGraphicsView
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QPushButton, QGraphicsBlurEffect, QLineEdit, QComboBox, QListView
from PyQt5.QtCore import QSize, QRect, Qt, QCoreApplication,  pyqtSignal, Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QBrush, QColor, QKeySequence
from constants import Style, Layout
from globals import items_configuration, GLOBAL_VERBOSE #self.scrollAreaWidgetContents_1

class helpers:
    @staticmethod
    def add_accessory(main_continer, room_layout: QGridLayout, accessory_type: str, id: int, name: str = None, status: str = None, row: int = 0, column: int = 0):
        # Validate parameters
        # if not isinstance(main_continer, QWidget):
        #     raise TypeError("main_continer must be an instance of QWidget")
        if not isinstance(room_layout, QGridLayout):
            raise TypeError("room_layout must be an instance of QGridLayout")
        if not isinstance(accessory_type, str):
            raise TypeError("accessory_type must be a string")
        if not isinstance(id, int):
            raise TypeError("id must be an integer")
        if name is not None and not isinstance(name, str):
            raise TypeError("name must be a string")
        if status is not None and not isinstance(status, str):
            raise TypeError("status must be a string")
        if not isinstance(row, int) or row < 0:
            raise TypeError("row must be a positve integer")
        if not isinstance(column, int) or column < 0:
            raise TypeError("column must be a positve integer")

        if accessory_type and accessory_type in list(items_configuration["Items Status"].keys()):
            _translate = QCoreApplication.translate
            is_active = helpers.is_active(accessory_type, status)
            if is_active is None:
                print(f"[ERROR]: I can't recognize if the accessory is active or not, please check: accessory_type: {accessory_type}, status: {status} the id of this item is: {id}")
                print(accessory_type, id, status )
                return None
            id_str = str(id)
            type_str = str(accessory_type)
            accessory_group_box = QGroupBox(main_continer.container)
            accessory_group_box.setMinimumSize(QSize(180, 180))
            accessory_group_box.setMaximumSize(QSize(180, 180))
            accessory_group_box.setContentsMargins(0, 0, 0, 0)
            

            if is_active:
                accessory_group_box.setStyleSheet(Style.ACCESSORY_GROUP_BOX_ACTIVE)
            else:
                accessory_group_box.setStyleSheet(Style.ACCESSORY_GROUP_BOX_DEFAULT)
            accessory_group_box.setTitle("")
            accessory_group_box.setObjectName("accessory_box_" + type_str + "_" + id_str)

            # Accessory Name
            accessory_name = QLabel(accessory_group_box)
            accessory_name.setGeometry(QRect(14, 126, 152, 21))
            accessory_name.setMinimumSize(QSize(152, 21))
            font = QFont()
            font.setFamily("Poppins")
            accessory_name.setFont(font)
            if is_active:
                accessory_name.setStyleSheet(Style.ACCESSORY_NAME_ACTIVE)                                   
            else:
                accessory_name.setStyleSheet(Style.ACCESSORY_NAME_DEFAULT)
            accessory_name.setObjectName("accessory_name_"+ type_str + "_" + id_str)

            # Accessory Status
            accessory_status = QLabel(accessory_group_box)
            accessory_status.setGeometry(QRect(14, 150, 152, 18))
            accessory_status.setMinimumSize(QSize(152, 18))
            accessory_status.setStyleSheet(Style.ACCESSORY_STATUS)
            accessory_status.setObjectName("accessory_status_" + type_str + "_" + id_str)

            # Accessory Icon
            accessory_icon = QToolButton(accessory_group_box)
            accessory_icon.setGeometry(QRect(11, 11, 68, 68))
            if is_active:
                accessory_icon.setStyleSheet(Style.ACCESSORY_ICON_ACTIVE)
            else:
                accessory_icon.setStyleSheet(Style.ACCESSORY_ICON_DEFAULT)

            icon2 = QIcon()
            icon_path = helpers.get_icon_path(accessory_type, status, is_active)
            icon2.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.On)
            accessory_icon.setIcon(icon2)
            accessory_icon.setIconSize(QSize(48, 48))
            accessory_icon.setToolButtonStyle(Qt.ToolButtonIconOnly)
            accessory_icon.setObjectName("accessory_icon_" + type_str + "_" + id_str)
            accessory_icon.clicked.connect(main_continer.accessory_toggle_handler)

            # Accessory Options Button
            accessory_options = QToolButton(accessory_group_box)
            accessory_options.setGeometry(QRect(140, 10, 32, 32))

            # Accessory Option Icon
            icon3 = QIcon()
            if is_active:
                icon3.addPixmap(QPixmap(":/addtional_icons/resources/addtional_icons/Dots Dark.png"), QIcon.Normal, QIcon.On)
            else:
                icon3.addPixmap(QPixmap(":/addtional_icons/resources/addtional_icons/Dots.png"), QIcon.Normal, QIcon.On)
            accessory_options.setIcon(icon3)
            accessory_options.setIconSize(QSize(32, 32))
            accessory_options.setObjectName("accessory_options_" + type_str + "_" + id_str)
            accessory_options.clicked.connect(main_continer.accessory_option_handler)

            # Set text for the icons
            accessory_icon.setText(_translate("MainWindow", "..."))
            accessory_options.setText(_translate("MainWindow", "..."))

            # Fill Accessory data
            accessory_name.setText(_translate("MainWindow", name))
            accessory_status.setText(_translate("MainWindow", status))

            room_layout.addWidget(accessory_group_box, row, column, 1, 1)
    
    # @staticmethod
    # def find_accessory_items(gb_obj):
    #     pass
    
    @staticmethod
    def accessory_update_status(gb_obj, type, id, status, CALLBACK = None):
        
        _translate = QCoreApplication.translate

        # obj_name = gb_obj.objectName().split("_")
        # obj_pre, type, id = obj_name[0], obj_name[1], obj_name[2]
        
        is_active = helpers.is_active(type, status)
        id_str = str(id)
        accessory_name = gb_obj.findChild(QLabel, "accessory_name_"+ type + "_" + id_str)
        accessory_icon = gb_obj.findChild(QToolButton, "accessory_icon_" + type + "_" + id_str)
        accessory_options =  gb_obj.findChild(QToolButton, "accessory_options_" + type + "_" + id_str)
        accessory_status = gb_obj.findChild(QLabel, "accessory_status_" + type + "_" + id_str)
        # Accessory Option Icon
        icon2 = QIcon()
        icon3 = QIcon()

        icon_path = helpers.get_icon_path(type, status, is_active)
        icon2.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.On)
        if is_active:
            gb_obj.setStyleSheet(Style.ACCESSORY_GROUP_BOX_ACTIVE)
            accessory_name.setStyleSheet(Style.ACCESSORY_NAME_ACTIVE)                                    
            accessory_icon.setStyleSheet(Style.ACCESSORY_ICON_ACTIVE)
            icon3.addPixmap(QPixmap(":/addtional_icons/resources/addtional_icons/Dots Dark.png"), QIcon.Normal, QIcon.On)
        else:
            gb_obj.setStyleSheet(Style.ACCESSORY_GROUP_BOX_DEFAULT)
            accessory_name.setStyleSheet(Style.ACCESSORY_NAME_DEFAULT)
            accessory_icon.setStyleSheet(Style.ACCESSORY_ICON_DEFAULT)

            icon3.addPixmap(QPixmap(":/addtional_icons/resources/addtional_icons/Dots.png"), QIcon.Normal, QIcon.On)
        # Set icons
        accessory_options.setIcon(icon3)
        accessory_icon.setIcon(icon2)
        accessory_status.setText(_translate("MainWindow", status))


        # CALLBACK to Update current copy of data's database
        if CALLBACK:
            CALLBACK(type, id, status)


    @staticmethod
    def get_type_and_id_of_accessory(obj):
        # Ensure obj has a valid objectName
        if not hasattr(obj, 'objectName'):
            raise AttributeError("The object does not have an 'objectName' attribute.")
        
        obj_name = obj.objectName().split("_")
        
        # Check if obj_name has at least 4 parts (prefix0, prefix1, type, id)
        if len(obj_name) < 4:
            raise ValueError(f"Object name '{obj.objectName()}' is not in the expected format.")
        
        obj_prefix0 = obj_name[0]   # "accessory"
        obj_prefix1 = obj_name[1]   # "box"
        type = "_".join(obj_name[2:-1])  # Join parts from type_str
        id_str = obj_name[-1]  # The last part should be the id

        # Convert id to an integer and handle errors
        try:
            id = int(id_str)
        except ValueError:
            id = None
            print(f"Warning: Unable to convert '{id_str}' to an integer. Setting id to None.")
        
        return type, id

    @staticmethod
    def find_accessory_data(data, type, id):
        for room in data:
            room_data           = room.get("dashboard", None)
            accessories_data    = room.get("accessories_data", None)

            for item in accessories_data:
                # dpos = item.get('position', None)
                dtype = item['type']
                did = item['id']
                # dstatus = item["status"]
                if dtype == type and did == id:
                    return {"room_data": room_data, "accessory_data": item}
        return None
    
    @staticmethod
    def get_icon_path(type, status=None, isActive = False):
        if isActive:
            common_path = ":/accessories_active/resources/accessories/active/"
        else:
            common_path = ":/accessories_default/resources/accessories/default/"
        
        if type not in items_configuration["Items Status"]:
            return None

        status_list = items_configuration["Items Status"][type]
        icon_paths = items_configuration["Icon Paths"].get(type, {})

        if status in status_list:
            item = icon_paths.get(status, None)
            if item:
                return common_path + item

        return None
    
    @staticmethod
    def is_active(type, status):
        if type not in items_configuration["Items Status"]:
            return None

        status_list = items_configuration["Items Status"][type]

        if status in status_list:
            index = status_list.index(status)
            if index == 0:
                return True
            elif index == 1:
                return False

        return None

from PyQt5.QtCore import QPoint, QRectF
from PyQt5.QtGui import QRegion, QPainterPath
class OptionsMenu(QWidget):
    def __init__(self, parent=None, accessory_source = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.accessory_source = accessory_source
        
        self.main_widget = QWidget(self)
        self.main_widget.setStyleSheet("""
                                       QWidget{
                                            Width:90px;
                                            font-size: 14px;
                                            font-weight: 400;
                                            text-align: left;
                                            border: none;
                                            background-color: #262626;
                                       }
                                       """)
    
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(0)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.main_widget)
        
        # Edit Button
        self.edit_button = QPushButton("Edit")
        self.edit_button.setStyleSheet("""
            QPushButton {
                background-color: #262626; 
                color: #ecf0f1; 
                border: none; 
                padding: 6px 10px; 
                border-radius: 6px;  
                margin-bottom:5px;
            }
            QPushButton:hover {
                background-color: #5c5c5c;
            }
        """)
        self.edit_button.setCursor(Qt.PointingHandCursor)
        self.edit_button.clicked.connect(self.on_edit)
        layout.addWidget(self.edit_button)

        # Create dividers
        divider1 = QFrame()
        divider1.setFrameShape(QFrame.HLine)
        divider_style = """
        QFrame {
            background-color: gray;
            border-top: 1px solid;
        }
        """
        divider1.setStyleSheet(divider_style)
        layout.addWidget(divider1)
        
        # Delete Button
        self.delete_button = QPushButton("Delete")
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #262626; 
                color: red; 
                border: none; 
                padding: 6px 10px;  
                border-radius: 6px;
                margin-top:5px;
            }
            QPushButton:hover {
                background-color: #5c5c5c;
            }
        """)
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.clicked.connect(self.on_delete)
        layout.addWidget(self.delete_button)

        # Apply the mask to ensure the rounded corners are clean
        self.apply_mask()

    def apply_mask(self):
        # Create a rounded rectangle path with slightly reduced size to account for margins
        path = QPainterPath()
        # print(self.width(), self.height())
        # these numbers that added or subtarcted from the height or the width to remove the border and the shadow that OS generate by defualt
        rect = QRectF(0, 0, self.width() + 20 , self.height() * 4  - 20)  # Full widget size
        path.addRoundedRect(rect, 12, 12)  # Radius of 12.0 for rounded corners

        # Create a region from the path and set it as the mask
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def paintEvent(self, event):
        # Draw the rounded background
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(38, 38, 38, 255)))  # gray background
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 12, 12)  # Radius of 12 for rounded corners

    def show_menu(self, pos):
        new_pos = QPoint(pos.x() - self.width() + 15, pos.y())
        self.move(new_pos)
        self.show()

    def on_edit(self):
        
        if self.accessory_source:
            self.parent().edit_widget(self.accessory_source)
        else:
            print("[Error]: Could you pass the accessory source")

        self.hide()

    def on_delete(self):
        if self.accessory_source:
            self.parent().delete_widget(self.accessory_source)
        else:
            print("[Error]: Could you pass the accessory source")
        self.hide()


class OverlayWidget(QWidget):
    def __init__(self, parent=None):
        super(OverlayWidget, self).__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)  # Transparent background
        self.setStyleSheet("background: transparent;")  # Ensure background is transparent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(75, 75, 75, 200))) 
        painter.setPen(Qt.NoPen)  # Ensure no border is drawn
        painter.drawRect(self.rect())


class BlurredOverlay(QWidget):
    def __init__(self, parent=None):
        super(BlurredOverlay, self).__init__(parent)
        self.p = parent
        self.setAttribute(Qt.WA_TranslucentBackground)  # Set widget background to be transparent
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool )  # No border and always on top
        self.setGeometry(parent.geometry())  # Set position and size of the transparent widget
        
        # # Create a QGraphicsScene to apply the blur effect
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(self.rect())
        self.view.setStyleSheet("background: transparent; border: none;")  # Ensure the background is transparent
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Create a QPixmap of the parent widget’s content
        pixmap = QPixmap(self.size())
        painter = QPainter(pixmap)
        self.p.render(painter)
        painter.end()

        # Scale the pixmap to fit the view
        pixmap = pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

        # Create a QGraphicsPixmapItem with the captured pixmap
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)

        # # Apply the blur effect to the QGraphicsPixmapItem
        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(15 * 3)  # Adjust the blur radius as needed
        pixmap_item.setGraphicsEffect(blur_effect)

        # Adjust the view to fit the scene
        self.view.fitInView(self.scene.sceneRect(), Qt.IgnoreAspectRatio)

        # # Add OverlayWidget to handle the semi-transparent overlay
        self.overlay_widget = OverlayWidget(self)
        self.overlay_widget.setGeometry(self.rect())
        self.overlay_widget.show()
    


    def mousePressEvent(self, event):
        if GLOBAL_VERBOSE:
            print("Overlay clicked")
        if self.p.dialog:
            self.p.dialog.close()
        self.close()  # Close the widget on click


class AddButtonOptions(QFrame):
    will_you_open_another_dialog = False

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Options Menu')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(Style.ADD_BUTTON_DIALOG_STYLE)
        AddButtonOptions.will_you_open_another_dialog = False

        # Create dividers
        divider1 = QFrame()
        divider1.setFrameShape(QFrame.HLine)
        
        divider2 = QFrame()
        divider2.setFrameShape(QFrame.HLine)

        divider3 = QFrame()
        divider3.setFrameShape(QFrame.HLine)

        divider_style = """
        QFrame {
            background-color: gray;
            border-top: 1px solid;
        }
        """
        divider1.setStyleSheet(divider_style)
        divider2.setStyleSheet(divider_style)
        divider3.setStyleSheet(divider_style)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)

        # Helper function to create a button with icons
        def create_button_with_icons(text, left_icon_path, right_icon_path, slot):
            button_layout = QHBoxLayout()
            button_layout.setContentsMargins(16, 12, 16, 12)

            # Left Icon
            left_icon_label = QLabel()
            left_icon_label.setPixmap(QPixmap(left_icon_path).scaled(30, 30, Qt.KeepAspectRatio))
            button_layout.addWidget(left_icon_label)

            # Button Text
            button = QLabel(text)
            # button.setFlat(True)  # Makes the button background transparent
            button_layout.addWidget(button)

            # Ensure button and icons stretch accordingly
            button_layout.addStretch()
            # Right Icon
            if right_icon_path:
                right_icon_label = QLabel()
                right_icon_label.setPixmap(QPixmap(right_icon_path).scaled(30, 30, Qt.KeepAspectRatio))
                button_layout.addWidget(right_icon_label)


            # Create a frame to make the entire layout clickable
            button_frame = QFrame()
            button_frame.setLayout(button_layout)
            button_frame.mousePressEvent = lambda event: slot()

            return button_frame

        # Paths to icons
        left_icon_path = ":/addtional_icons/resources/addtional_icons/Plus Light.png"  # Replace with actual path
        right_icon_paths = {
            'add_room': ":/addtional_icons/resources/addtional_icons/Room.png",
            'add_accessory': ":/accessories_default/resources/accessories/default/Lamp Light.png",
            'add_automation': ":/addtional_icons/resources/addtional_icons/Alarm Light.png",
            'close': "path/to/close_icon.png"
        }

        # Create buttons with icons
        add_room_button = create_button_with_icons('Add Room', left_icon_path, right_icon_paths['add_room'], self.add_room)
        add_accessory_button = create_button_with_icons('Add Accessory', left_icon_path, right_icon_paths['add_accessory'], self.add_accessory)
        add_automation_button = create_button_with_icons('Add Automation', left_icon_path, right_icon_paths['add_automation'], self.add_automation)
        # close_button = create_button_with_icons('Close', left_icon_path, None, self.close) # right_icon_paths['close']

        # Add buttons and dividers to layout
        layout.addWidget(add_room_button)
        layout.addWidget(divider1)
        layout.addWidget(add_accessory_button)
        layout.addWidget(divider2)
        layout.addWidget(add_automation_button)
        # layout.addWidget(divider3)
        # layout.addWidget(close_button)

        self.setLayout(layout)

    def paintEvent(self, event):
        # This ensures that the window is painted with rounded corners
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(37, 37, 37, 255)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)  # Radius for x and y

    def add_room(self):
        AddButtonOptions.will_you_open_another_dialog = True
        if GLOBAL_VERBOSE:
            print("Add room selected")
        self.parent().open_add_room_dialog()
        # self.close()
        
    def add_accessory(self):
        AddButtonOptions.will_you_open_another_dialog = True
        if GLOBAL_VERBOSE:
            print("Add Accessory selected")
        self.parent().open_add_accessory_dialog()
        
    def add_automation(self):
        print("Add Automation selected")
    
    def closeEvent(self, event):
        super().closeEvent(event)
        if GLOBAL_VERBOSE:
            print("AddButtonOptions closed")
        # Call cleanup method if needed
        if self.parent():
            parent_window = self.parent()
            if hasattr(parent_window, 'clean_up_overlay') and not AddButtonOptions.will_you_open_another_dialog:
                parent_window.clean_up_overlay()



class FocusableLineEdit(QLineEdit):
    focused = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.focused.emit(self)  # Emit the focused signal with the input field itself as an argument


class VirtualKeyboard(QWidget):
    def __init__(self):
        super().__init__()
        self.target_input = None
        self.shift_pressed = False
        self.caps_lock_on = False
        self.is_lower = False
        self.init_ui()
        QApplication.instance().focusChanged.connect(self.on_focus_changed)

    def init_ui(self):
        layout = QGridLayout()

        self.buttons = [
            ('Q', 1, 0), ('W', 1, 1), ('E', 1, 2), ('R', 1, 3), ('T', 1, 4), ('Y', 1, 5), ('U', 1, 6), ('I', 1, 7), ('O', 1, 8), ('P', 1, 9),            ('1', 1, 11, 'number'), ('2', 1, 12, 'number'), ('3', 1, 13, 'number'),
            ('A', 2, 0), ('S', 2, 1), ('D', 2, 2), ('F', 2, 3), ('G', 2, 4), ('H', 2, 5), ('J', 2, 6), ('K', 2, 7), ('L', 2, 8),                         ('4', 2, 11, 'number'), ('5', 2, 12, 'number'), ('6', 2, 13, 'number'),
            ('Shift', 3, 0, 'shift'), ('Z', 3, 1), ('X', 3, 2), ('C', 3, 3), ('V', 3, 4), ('B', 3, 5), ('N', 3, 6), ('M', 3, 7), ('Caps', 3, 8, 'caps'), ('7', 3, 11, 'number'), ('8', 3, 12, 'number'), ('9', 3, 13, 'number'),
            ('Space', 4, 0, 'space', 1, 6), ('Backspace', 4, 6, 'backspace', 1, 4),                                                                                              ('0', 4, 12, 'number')
        ]

        for button in self.buttons:
            text, row, col = button[0], button[1], button[2]
            role = button[3] if len(button) > 3 else 'letter'
            rowspan, colspan = 1, 1
            if len(button) > 4:
                rowspan, colspan = button[4], button[5]
            btn = QPushButton(text)
            btn.setObjectName(text)
            btn.clicked.connect(self.on_button_click)
            if role == 'number':
                btn.setStyleSheet(Style.KEYBOARD_BUTTON_STYLE_NUMBER)
            elif role == 'shift':
                btn.setStyleSheet(Style.KEYBOARD_BUTTON_STYLE_SHIFT)
            elif role == 'caps':
                btn.setStyleSheet(Style.KEYBOARD_BUTTON_STYLE_CAPS)
            elif role == 'space':
                btn.setStyleSheet(Style.KEYBOARD_BUTTON_STYLE_SPACE)
            elif role == 'backspace':
                btn.setStyleSheet(Style.KEYBOARD_BUTTON_STYLE_BACKSPACE)
            else:
                btn.setStyleSheet(Style.KEYBOARD_BUTTON_STYLE)
            layout.addWidget(btn, row, col, rowspan, colspan)

        self.setLayout(layout)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setStyleSheet(Style.KEYBOARD_STYLE)

    def set_target_input(self, input_field):
        self.target_input = input_field
        DialogTemplate.show_keyboard()

    def on_button_click(self):
        if not self.target_input:
            return
        
        button = self.sender()
        text = button.text()

        if text == 'Shift':
            self.shift_pressed = not self.shift_pressed
            self.update_buttons()
        elif text == 'Caps':
            self.caps_lock_on = not self.caps_lock_on
            self.update_buttons()
        elif text == 'Space':
            self.target_input.insert(' ')
        elif text == 'Backspace':
            current_text = self.target_input.text()
            self.target_input.setText(current_text[:-1])
        else:
            if self.shift_pressed:
                self.target_input.insert(text)
                self.shift_pressed = False
                self.update_buttons()
            elif self.caps_lock_on:
                self.target_input.insert(text)
            else:
                self.target_input.insert(text)

    def update_buttons(self):
        for button in self.buttons:
            btn = self.findChild(QPushButton, button[0])
            if btn:
                if button[0] not in ['Shift', 'Caps', 'Space', 'Backspace']:
                    if self.is_lower:
                        btn.setText(button[0].upper())
                    else:
                        btn.setText(button[0].lower())
        
        self.is_lower = not self.is_lower

    def on_focus_changed(self, old, new):
        if isinstance(new, FocusableLineEdit):
            self.set_target_input(new)
        elif isinstance(new, QPushButton):
            pass
        elif self.isVisible():
            self.hide()


class DialogTemplate(QWidget):
    keyboard = None

    def __init__(self, parent=None, title='Dialog'):
        super().__init__(parent)

        self.p = parent
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(Style.DIALOG_STYLE)

        # Title Layout
        self.title_layout = QHBoxLayout()
        self.title_icon = QLabel()
        pixmap = QPixmap(":/addtional_icons/resources/addtional_icons/Plus Light.png").scaled(28, 28, Qt.KeepAspectRatio)
        self.title_icon.setPixmap(pixmap)
        self.title_icon.setFixedSize(24, 24)
        # self.title_icon.setStyleSheet("margin-bottom: 2px")
        
        self.title_label = QLabel(title)
        # self.title_label.setFixedHeight(37)
        self.title_label.setStyleSheet(Style.DIALOG_TITLE)

        self.title_layout.addWidget(self.title_icon)
        self.title_layout.addWidget(self.title_label)
        self.title_layout.setAlignment(Qt.AlignCenter)
        self.title_layout.setContentsMargins(7, 7, 7, 7)

        # init keyboard
        DialogTemplate.keyboard = VirtualKeyboard()  # Instantiate the virtual keyboard
        keyboard_height = self.p.height() // 3
        DialogTemplate.keyboard.setGeometry(self.p.x(), self.p.y() + self.p.height() - keyboard_height, self.p.width(), keyboard_height)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setContentsMargins(0, 0, 0, 0)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)

        self.layout.addLayout(self.title_layout)
        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)

        shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        shortcut.activated.connect(self.close)

    def paintEvent(self, event):
        # This ensures that the window is painted with rounded corners
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(0, 0, 0, 255)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)  # Radius for x and y

    def create_buttons(self):
        button_layout = QHBoxLayout()  # Create a layout to hold the label and entry side by side

        self.save_button = QPushButton('Save')
        cancel_button = QPushButton('Cancel')
        button_layout.addWidget(cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_layout.addStretch()                 # make button at the end of the dialog
        self.scroll_layout.addLayout(button_layout)

        cancel_button.clicked.connect(self.close)

        self.save_button.setStyleSheet(Style.DIALOG_BUTTON + "background: rgba(1, 78, 255, 1); color: white;")

        cancel_button.setStyleSheet(Style.DIALOG_BUTTON)
        # self.setStyleSheet(Style.KEYBOARD_STYLE)
    
    def apply_styles(self, label, entry):
        label.setStyleSheet(Style.DIALOG_LABEL)
        entry.setStyleSheet(Style.DIALOG_ENTRY)
        
    @staticmethod
    def show_keyboard():
        if DialogTemplate.keyboard:
            DialogTemplate.keyboard.show()
            DialogTemplate.keyboard.update()

    def closeEvent(self, event):
        super().closeEvent(event)
        if self.parent():
            parent_window = self.parent()
            if hasattr(parent_window, 'clean_up_overlay'):
                self.keyboard.close()
                parent_window.clean_up_overlay()

    def connect_focus_events(self, input_fields):
        for field in input_fields:
            field.focused.connect(self.keyboard.set_target_input)



class AddRoomDialog(DialogTemplate):
    def __init__(self, parent=None):
        super().__init__(parent, title='Add Room')

        name_label = QLabel('Room')
        self.name_entry = FocusableLineEdit()  # Use the custom FocusableLineEdit class
        self.name_entry.setPlaceholderText("Enter room name")

        form_container = QFrame()
        form_layout = QVBoxLayout(form_container)  # Create a layout to hold the label and entry side by side
        form_layout.setSpacing(0)  # Set the spacing between widgets to 3px
        form_container.setLayout(form_layout)
        # form_container.setMaximumHeight(58)  # Set the maximum height of the form
        form_container.setContentsMargins(0, 12, 0, 12)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_entry)

        self.apply_styles(name_label, self.name_entry)
        self.scroll_layout.addWidget(form_container)

        self.postloads()

    def postloads(self):
        self.create_buttons()
        self.name_entry.setFocus()
        
        if self.submit:
            self.save_button.clicked.connect(self.submit)

        self.connect_focus_events(self.findChildren(FocusableLineEdit))  # Connect focus events for input fields

    def submit(self):
        print(f"Room name 1 : {self.name_entry.text()}")
        self.close()

from PyQt5.QtWidgets import QLabel, QComboBox, QVBoxLayout, QFrame, QLineEdit, QStyleOptionComboBox, QStyle
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt, QEvent
from PyQt5.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem
from PyQt5.QtGui import QPainter

class CustomDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        # Add padding to the option's rect
        option.rect.setTop(option.rect.top() + 1)
        option.rect.setBottom(option.rect.bottom() - 1)
        super().paint(painter, option, index)

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(size.height() + 2)  # Increase the height to add space
        return size


class AddAccessoryDialog(DialogTemplate):
    def __init__(self, parent=None):
        super().__init__(parent, title='Add Accessory')

        accessory_type_label = QLabel('Accessory Type')
        self.accessory_type_combo = self.create_custom_combo_box(["Type 1", "Type 2", "Type 3"], "Select")

        room_label = QLabel('Room')
        self.room_combo = self.create_custom_combo_box(["Room 1", "Room 2", "Room 3"], "Select Room")

        name_label = QLabel('Name')
        self.name_entry = FocusableLineEdit()
        self.name_entry.setPlaceholderText("Name this accessory")

        id_label = QLabel('ID')
        self.id_entry = FocusableLineEdit()
        self.id_entry.setPlaceholderText("Enter accessory ID")

        cp_label = QLabel('Communication Protocol')
        self.cp_combo = self.create_custom_combo_box(["Protocol 1", "Protocol 2", "Protocol 3", "Protocol 1", "Protocol 2", "Protocol 3"], "Select Protocol")

        form_container = QFrame()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(5)
        form_container.setLayout(form_layout)
        form_container.setContentsMargins(0, 0, 0, 0)
        form_layout.setContentsMargins(0, 0, 0, 0)

        form_layout.addWidget(accessory_type_label)
        form_layout.addWidget(self.accessory_type_combo)
        form_layout.addWidget(room_label)
        form_layout.addWidget(self.room_combo)
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_entry)
        form_layout.addWidget(id_label)
        form_layout.addWidget(self.id_entry)
        form_layout.addWidget(cp_label)
        form_layout.addWidget(self.cp_combo)

        self.apply_styles(name_label, self.name_entry)
        self.apply_styles(id_label, self.id_entry)

        # Applying custom styles to labels and combo boxes using Style
        accessory_type_label.setStyleSheet(Style.DIALOG_LABEL)
        room_label.setStyleSheet(Style.DIALOG_LABEL)
        cp_label.setStyleSheet(Style.DIALOG_LABEL)

        self.scroll_layout.addWidget(form_container)

        self.postloads()

    def create_custom_combo_box(self, items, placeholder):
        combo = CustomComboBox()
        combo.addItems(items)
        combo.setCurrentIndex(-1) # it shoud be here (before placehlder to show the placeholder correctly)
        combo.setPlaceholderText(placeholder)
        combo.setStyleSheet(Style.DIALOG_COMBO)

        return combo


    def postloads(self):
        self.create_buttons()
        # self.name_entry.setFocus()

        if self.submit:
            self.save_button.clicked.connect(self.submit)

        self.connect_focus_events(self.findChildren(FocusableLineEdit))

    def submit(self):
        print(f"Accessory Type: {self.accessory_type_combo.currentText()}")
        print(f"Room: {self.room_combo.currentText()}")
        print(f"Name: {self.name_entry.text()}")
        print(f"ID: {self.id_entry.text()}")
        print(f"Communication Protocol: {self.cp_combo.currentText()}")
        self.close()

class PaddedItemDelegate(QStyledItemDelegate):
    def __init__(self, padding=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.padding = padding

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        return QSize(size.width(), size.height() + 2 * self.padding)


class CustomComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.placeholder = ""
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setAlignment(Qt.AlignCenter)
        self.lineEdit().installEventFilter(self)

        # Set a custom QListView for the dropdown
        self.setView(QListView())
        self.view().setSpacing(0)  # Remove spacing between items
        
        # Apply stylesheet for border-radius and centering
        self.view().setStyleSheet("""
            QListView {
                border: 1px solid gray;
                border-radius: 5px;
                padding: 0px;
                padding-left: 15px;
                margin: 0px;
            }
            QListView::item:hover {
                background: none;  /* Removes the hover background */
                border: none;      /* Removes any border on hover */
            }
            QListView::item:selected {
                background: none;  /* Removes the selection background */
                border: none;      /* Removes any border on selection */
            }
        """)
        self.setStyleSheet(Style.DIALOG_COMBO)

        # Set the custom delegate with padding
        padding = Layout.COMBOBOX_ITEM_PADDING  # Define padding size
        self.view().setItemDelegate(PaddedItemDelegate(padding))

        # Set a maximum number of visible items
        self.maxVisibleItems = Layout.COMBOBOX_MAX_NUM_OF_SHWON_ITEMS

    def setPlaceholderText(self, placeholder):
        self.placeholder = placeholder
        self.update_placeholder()

    def update_placeholder(self):
        if self.currentIndex() == -1:  # No selection
            self.lineEdit().setText(self.placeholder)
        else:
            self.lineEdit().setText(self.currentText())

    def currentText(self):
        if self.currentIndex() == -1:  # No selection
            return ""
        return super().currentText()

    def eventFilter(self, obj, event):
        if obj == self.lineEdit() and event.type() in [QEvent.MouseButtonPress]:
            self.showPopup()
        return super().eventFilter(obj, event)

    def showPopup(self):
        # Calculate the height of the popup
        item_height = self.view().sizeHintForRow(0)
        num_items = min(self.count(), self.maxVisibleItems)  # Limit number of visible items
        popup_height = item_height * num_items  # Height for the popup based on visible items

        # Set the fixed height for the popup
        self.view().parent().setFixedHeight(popup_height)
        
        # Adjust scroll bar policy
        self.view().setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff if num_items == self.count() else Qt.ScrollBarAsNeeded)

        super().showPopup()


# class AddAccessoryDialog(DialogTemplate):
#     def __init__(self, parent=None):
#         super().__init__(parent, title='Add Accessory')

#         accessory_type_label = QLabel('Accessory Type')
#         self.accessory_type_combo = QComboBox()
#         self.accessory_type_combo.setPlaceholderText("Select")

#         room_label = QLabel('Room')
#         self.room_combo = QComboBox()
#         self.room_combo.setPlaceholderText("Select Room")

#         name_label = QLabel('Name')
#         self.name_entry = FocusableLineEdit()
#         self.name_entry.setPlaceholderText("Name this accessory")

#         id_label = QLabel('ID')
#         self.id_entry = FocusableLineEdit()
#         self.id_entry.setPlaceholderText("Enter accessory ID")

#         cp_label = QLabel('Communication Protocol')
#         self.cp_combo = QComboBox()

#         form_container = QFrame()
#         form_layout = QVBoxLayout(form_container)
#         form_layout.setSpacing(0)
#         form_container.setLayout(form_layout)
#         form_container.setContentsMargins(0, 0, 0, 0)
#         form_layout.setContentsMargins(0, 0, 0, 0)

#         form_layout.addWidget(accessory_type_label)
#         form_layout.addWidget(self.accessory_type_combo)
#         form_layout.addWidget(room_label)
#         form_layout.addWidget(self.room_combo)
#         form_layout.addWidget(name_label)
#         form_layout.addWidget(self.name_entry)
#         form_layout.addWidget(id_label)
#         form_layout.addWidget(self.id_entry)
#         form_layout.addWidget(cp_label)
#         form_layout.addWidget(self.cp_combo)

#         self.apply_styles(name_label, self.name_entry)
#         self.apply_styles(id_label, self.id_entry)

#         # Applying custom styles to labels and combo boxes
#         accessory_type_label.setStyleSheet(Style.DIALOG_LABEL)
#         self.accessory_type_combo.setStyleSheet(Style.DIALOG_COMBO)
#         room_label.setStyleSheet(Style.DIALOG_LABEL)
#         self.room_combo.setStyleSheet(Style.DIALOG_COMBO)
#         cp_label.setStyleSheet(Style.DIALOG_LABEL)
#         self.cp_combo.setStyleSheet(Style.DIALOG_COMBO)

#         self.scroll_layout.addWidget(form_container)

#         self.postloads()

#     def postloads(self):
#         self.create_buttons()
#         # self.name_entry.setFocus()

#         if self.submit:
#             self.save_button.clicked.connect(self.submit)

#         self.connect_focus_events(self.findChildren(FocusableLineEdit))

#     def submit(self):
#         print(f"Accessory Type: {self.accessory_type_combo.currentText()}")
#         print(f"Room: {self.room_combo.currentText()}")
#         print(f"Name: {self.name_entry.text()}")
#         print(f"ID: {self.id_entry.text()}")
#         print(f"Communication Protocol: {self.cp_combo.currentText()}")
#         self.close()


########################################################### Example ################################
# class DialogEample(DialogTemplate):
#     def __init__(self, parent=None):
#         super().__init__(parent, title='Add Room')

#         name_label = QLabel('Name of the room 1:')
#         self.name_entry = FocusableLineEdit()  # Use the custom FocusableLineEdit class

#         form_layout = QHBoxLayout()  # Create a layout to hold the label and entry side by side
#         form_layout.addWidget(name_label)
#         form_layout.addWidget(self.name_entry)

#         self.scroll_layout.addLayout(form_layout)
#         self.apply_styles(name_label, self.name_entry)


#         name_label1 = QLabel('Name of the room 2:')
#         self.name_entry1 = FocusableLineEdit()  # Use the custom FocusableLineEdit class

#         form_layout = QHBoxLayout()  # Create a layout to hold the label and entry side by side
#         form_layout.addWidget(name_label1)
#         form_layout.addWidget(self.name_entry1)

#         self.scroll_layout.addLayout(form_layout)
        
#         self.apply_styles(name_label1, self.name_entry1)


#         name_label2 = QLabel('Name of the room 3:')
#         self.name_entry2 = FocusableLineEdit()  # Use the custom FocusableLineEdit class

#         form_layout = QHBoxLayout()  # Create a layout to hold the label and entry side by side
#         form_layout.addWidget(name_label2)
#         form_layout.addWidget(self.name_entry2)

#         self.scroll_layout.addLayout(form_layout)
        
#         self.apply_styles(name_label2, self.name_entry2)

        
#         name_label3 = QLabel('Name of the room 4:')
#         self.name_entry3 = FocusableLineEdit()  # Use the custom FocusableLineEdit class

#         form_layout = QHBoxLayout()  # Create a layout to hold the label and entry side by side
#         form_layout.addWidget(name_label3)
#         form_layout.addWidget(self.name_entry3)

#         self.scroll_layout.addLayout(form_layout)
        
#         self.apply_styles(name_label3, self.name_entry3)


#         name_label4 = QLabel('Name of the room 5:')
#         self.name_entry4 = FocusableLineEdit()  # Use the custom FocusableLineEdit class

#         form_layout = QHBoxLayout()  # Create a layout to hold the label and entry side by side
#         form_layout.addWidget(name_label4)
#         form_layout.addWidget(self.name_entry4)

#         self.scroll_layout.addLayout(form_layout)
        
#         self.apply_styles(name_label4, self.name_entry4)


#         self.create_buttons()
#         self.name_entry.setFocus()
        
#         if self.submit:
#             self.submit_button.clicked.connect(self.submit)

#         self.connect_focus_events(self.findChildren(FocusableLineEdit))  # Connect focus events for input fields

#     def submit(self):
#         print(f"Room name 1 : {self.name_entry.text()}")
#         print(f"Room name2 : {self.name_entry1.text()}")
#         self.close()
