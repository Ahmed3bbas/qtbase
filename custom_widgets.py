from PyQt5.QtWidgets import QLineEdit, QComboBox, QListView, QStyledItemDelegate, QWidget
from PyQt5.QtCore import pyqtSignal, QEvent
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtGui import  QPainter, QBrush, QColor
from constants import Style, Layout

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


class FocusableLineEdit(QLineEdit):
    focused = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.focused.emit(self)  # Emit the focused signal with the input field itself as an argument

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
        # self.view().setStyleSheet(Style.CUSTOM_COMBO_BOX)
        self.view().setFocusPolicy(Qt.NoFocus)
        # self.setStyleSheet(Style.DIALOG_COMBO)

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
            QTimer.singleShot(100, self.showPopup)  # Add a small delay
            # self.showPopup()
            return True
        return super().eventFilter(obj, event)

    # def paintEvent(self, event):
    #     # Draw the rounded background
    #     painter = QPainter(self)
    #     painter.setRenderHint(QPainter.Antialiasing)
    #     painter.setBrush(QBrush(QColor(34, 34, 34, 255)))  # Gray background
    #     painter.setPen(Qt.NoPen)
        
    #     # Draw rounded rect for the entire combo box
    #     rect = self.rect()
    #     painter.drawRoundedRect(rect, 12, 12)  # Radius of 12 for rounded corners
        
    #     # Call the base class to draw the rest of the combo box
    #     super().paintEvent(event)
    
    def showPopup(self):
        # Calculate the height of the popup based on item height and number of visible items
        item_height = self.view().sizeHintForRow(0)
        num_items = min(self.count(), self.maxVisibleItems)
        popup_height = item_height * num_items + 2  # Add 2 pixels for borders

        # Set the height of the popup
        self.view().parent().setFixedHeight(popup_height)
        
        # Adjust scroll bar policy
        self.view().setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff if num_items == self.count() else Qt.ScrollBarAsNeeded)

        super().showPopup()

     