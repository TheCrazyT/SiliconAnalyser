import abc
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QTreeView

from silicon_analyser.grid import Grid
from silicon_analyser.treeitem import TreeItem

class AbstractTreeHelper(QTreeView):
    evtTreeSelectionChanged: pyqtSignal
    
    @abc.abstractmethod
    def selectedType(self) -> str:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def selectedLabel(self) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def getSelectedItem(self) -> QStandardItem:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def getSelectedGrid(self):
       raise NotImplementedError()

    @abc.abstractmethod
    def getSelectedAIGrid(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def isItemSelected(self, rectLabel, gridName, gridItemType) -> bool:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def addTreeItem(self, text, type="auto", parent_obj=None, parent_item=None) -> tuple[Grid, TreeItem]:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def clearAIItem(self):
        raise NotImplementedError()