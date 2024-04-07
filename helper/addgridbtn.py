from PyQt5.QtWidgets import QInputDialog, QPushButton
from helper.abstract.abstractmywindow import AbstractMyWindow
from PyQt5.QtGui import QMouseEvent
from treeitem import TreeItem

class AddGridBtn(QPushButton):
    def __init__(self, text: str):
        QPushButton.__init__(self, text)
        self.clicked.connect(self.buttonClicked)

    def buttonClicked(self, event: QMouseEvent):
        print("AddGridBtn: buttonClicked")
        self.myWindow.getTree().addTreeItem("grid_%d" % self.gridIdx,TreeItem.TYPE_GRID)
        self.gridIdx += 1
    
    def initialize(self, myWindow: AbstractMyWindow):
        self._myWindow = myWindow