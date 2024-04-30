import logging
logger = logging.getLogger(__name__)

from PyQt5.QtWidgets import QInputDialog, QPushButton
from PyQt5.QtGui import QMouseEvent
from silicon_analyser.helper.abstract.abstractmywindow import AbstractMyWindow
from silicon_analyser.treeitem import TreeItem

class AddGridBtn(QPushButton):
    def __init__(self, text: str):
        QPushButton.__init__(self, text)
        self.clicked.connect(self.buttonClicked)
        self._gridIdx = 0

    def buttonClicked(self, event: QMouseEvent):
        print("AddGridBtn: buttonClicked")
        tree = self._myWindow.getTree()
        tree.addTreeItem("grid_%d" % self._gridIdx,TreeItem.TYPE_GRID)
        tree.expandAll()
        self._gridIdx += 1
    
    def initialize(self, myWindow: AbstractMyWindow):
        self._myWindow = myWindow