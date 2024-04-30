from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem
import typing

class TreeItem(QStandardItem):
    TYPE = 0x1337
    OBJECT = 0x1338
    TEXT = 0x1339
    
    TYPE_GRID = "grid"
    TYPE_AI_GRID = "aiGrid"
    TYPE_GRID_ITEM = "gridItem"
    TYPE_AI_GRID_ITEM = "aiGridItem"
    TYPE_MANUAL = "manual"
    TYPE_AI = "ai"
    
    onChecked: typing.Callable|None
    
    def __init__(self, text, type, obj):
        QStandardItem.__init__(self,text)
        self._text = text
        self._type = type
        self._obj  = obj
        self.onChecked = None
    
    def data(self, role: int = ...): # type: ignore
        if(role == TreeItem.TYPE):
            return self._type
        if(role == TreeItem.OBJECT):
            return self._obj
        if(role == TreeItem.TEXT):
            return self._text
        return super().data(role)
    
    def getObject(self):
        return self._obj
    
    def setData(self, value: typing.Any, role: int = ...) -> None: # type: ignore
        if role == Qt.ItemDataRole.CheckStateRole:
            if self.onChecked is not None:
                if value == 0:
                    self.onChecked(self,False,self._text)
                else:
                    self.onChecked(self,True,self._text)
        return super().setData(value, role)
    
    def uncheck(self):
        self.setCheckState(Qt.CheckState.Unchecked)

    
    