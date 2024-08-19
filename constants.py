# Constent
class Layout:
    MAX_COLS = 4  
    BUTTON_SIZE = 150

    COMBOBOX_ITEM_PADDING = 10
    COMBOBOX_MAX_NUM_OF_SHWON_ITEMS = 3

    TKINTER_KEYBOARD_Y_SHIFT = 30

# Styles
class Style:
    ROOM_NAME = """
                margin:10px;
                padding:10px;
                color: white;
                font-family: Poppins;
                font-size: 14px;
                font-weight: 400;
                line-height: 21px;
                text-align: left;
                font: normal;
                """
    ACCESSORY_GROUP_BOX_ACTIVE = """
                                    background-color: #FFFFFF;
                                    border-radius:15px;
                                    """
    
    ACCESSORY_GROUP_BOX_DEFAULT = """
                                    background-color: #333333;
                                    border-radius:15px;
                                    """
    # New styles
    ACCESSORY_NAME_COMMON = """
                            font-family: Poppins;
                            font-size: 14px;
                            font-weight: 600;
                            line-height: 21px;
                            text-align: left;
                            """
    ACCESSORY_NAME_ACTIVE = ACCESSORY_NAME_COMMON + """
        color: black;
    """

    ACCESSORY_NAME_DEFAULT = ACCESSORY_NAME_COMMON + """
        color: #FFFFFF;
    """

    ACCESSORY_STATUS = """
        color: #6d6d6d;
        font-family: Poppins;
        font-size: 12px;
        font-weight: 400;
        line-height: 18px;
        text-align: left;
    """

    ACCESSORY_ICON_ACTIVE = """
        background-color: #7f7f7f;
        border-radius: 34px;
    """

    ACCESSORY_ICON_DEFAULT = """
        background: rgba(255, 255, 255, 0.2);
        border-radius: 34px;
    """

    ADD_BUTTON_DIALOG_STYLE = """
            QWidget {
                background-color: #252525;
                font-family: Poppins;
                font-size: 14px;
                font-weight: 500;
            }
            QFrame {
                color: white;
                border: none;
            }
        """
    DIALOG_STYLE = """
            QWidget {
                background-color: #000000;
                border-radius: 10px;
                font-family: Poppins;
                font-size: 14px;
                font-weight: 400;
                color: rgba(255, 255, 255, 0.7); 
            }
            QPushButton {
                color: white;
                border: none;
                padding: 12px, 16px, 12px, 16px;
                border-radius: 5px; 
            }
        """
            # QPushButton:hover {
            #     background-color: #5c5c5c;
            # }

    MENU_STYLE = """
                QMenu {
                    border-radius: 12px;
                    background-color: #262626; /* Background color */
                    padding: 10px;
                }
                QMenu::item {
                    background-color: transparent; /* Item background color */
                    color: #ecf0f1; /* Text color */
                    padding: 5px 20px; /* Item padding */
                    border-radius: 16px;
                }
                QMenu::item:selected {
                    background-color: #5c5c5c; /* Hover background color */
                    color: #ecf0f1; /* Hover text color */
                }
                QMenu::item:last{
                    color:red;
                }
            """

    FLOAT_BUTTON_STYLE = """
                QPushButton {
                    background-color: #2E3440; /* Blue background color #3498db*/
                    color: white; /* White text color */
                    border: none; /* Remove border */
                    border-radius: 25px; /* Make the button circular */
                    font-weight: bold; /* Bold text */
                    font-size: 16px; /* Text size */
                    padding: 10px; /* Padding inside the button */
                }
                QPushButton:pressed {
                    background-color: #2980b9; /* Darker blue when pressed */
                }
            """
    
    ITEM_BUTTON_STYLE = """
                    padding: 10px;
                    margin-top: 10px;
                    border-radius: 10px;
                    background-color: white;
                    color: black;
                    font-size: 10px;
                """
    
    KEYBOARD_BUTTON_STYLE = """
        padding: 10px;
        border-radius: 10px;
        background-color: #4C566A;
        color: white;
        font-size: 18px;
    """

    KEYBOARD_BUTTON_STYLE_NUMBER = """
        padding: 10px;
        border-radius: 10px;
        background-color: #D08770;
        color: white;
        font-size: 18px;
    """

    KEYBOARD_BUTTON_STYLE_SHIFT = """
        padding: 10px;
        border-radius: 10px;
        background-color: #88C0D0;
        color: white;
        font-size: 18px;
    """

    KEYBOARD_BUTTON_STYLE_CAPS = """
        padding: 10px;
        border-radius: 10px;
        background-color: #81A1C1;
        color: white;
        font-size: 18px;
    """

    KEYBOARD_BUTTON_STYLE_SPACE = """
        padding: 10px;
        border-radius: 10px;
        background-color: #A3BE8C;
        color: white;
        font-size: 18px;
    """

    KEYBOARD_BUTTON_STYLE_BACKSPACE = """
        padding: 10px;
        border-radius: 10px;
        background-color: #BF616A;
        color: white;
        font-size: 18px;
    """

    KEYBOARD_STYLE = """
        background-color: #2E3440; 
        color: white;
        border-radius: 10px;

        
    """

    DIALOG_TITLE = """
            font-family: Poppins;
            font-size: 14px;
            font-weight: 500;
            
            text-align: center;
            color: white;
            margin-left:3px;
        """
    
    DIALOG_LABEL = """
            font-family: Poppins;
            font-size: 12px;
            font-weight: 500;
            text-align: left;
            color: rgba(255, 255, 255, 0.7);
            
        """
 
    # color: white;
    DIALOG_ENTRY = """
            border-radius: 10px;
            background-color: #191919;
            font-family: Poppins;
            font-size: 14px;
            font-weight: 500;
            height: 38px;
            border: none;
            padding: 0 8px;
        """

    DIALOG_COMBO = """
            QComboBox {
                border-radius: 10px;
                background-color: #343434;
                font-family: Poppins;
                font-size: 14px;
                font-weight: 500;
                height: 38px;
                border: none;
                padding: 0 8px;
                line-height: 21px;

            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: #343434;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                background: #343434;
                border-radius: 10px;
                            
            }
            QComboBox::drop-down:button {
                image: url(:/addtional_icons/resources/addtional_icons/Plus Light.png);
            }
            
            QComboBox QAbstractItemView {
                padding: 10px 31px;
                border: 1px solid #262626;
                background-color: #262626;
                color:white;
                border-radius: 10px;
                selection-background-color: #262626;
            }
        """

    DIALOG_BUTTON = """
            padding: 6px 14px 6px 14px;
            background-color: #4b4b4b;
            border-radius: 10px;
            font-family: Poppins;
            font-size: 14px;
            font-weight: 500;
            text-align: center;
            """