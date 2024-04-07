from PyQt5.QtWidgets import QInputDialog, QPushButton
from helper.abstract.abstractmywindow import AbstractMyWindow
from PyQt5.QtGui import QMouseEvent

class AddLabelBtn(QPushButton):
    def __init__(self, text: str):
        QPushButton.__init__(self, text)
        self.clicked.connect(self.buttonClicked)

    def buttonClicked(self, event: QMouseEvent):
        print("AddLabelBtn: buttonClicked")
        text, ok = QInputDialog.getText(self, 'Label Input Dialog', 'Enter your label:')
        if ok:
            self._myWindow.getTree().addTreeItem(text)
            
    def initialize(self, myWindow: AbstractMyWindow):
        self._myWindow = myWindow