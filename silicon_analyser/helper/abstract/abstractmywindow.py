from PyQt5.QtCore import QItemSelection
from PyQt5.QtWidgets import QMainWindow, QPushButton, QAction
from PyQt5.QtGui import QStandardItem

from silicon_analyser.helper.abstract.abstractimage import AbstractImage
from silicon_analyser.helper.abstract.abstracttreehelper import AbstractTreeHelper

class AbstractMyWindow(QMainWindow):
    _actionGridAddRowTop: QAction
    _actionSaveModel: QAction
    _actionLoadModel: QAction
    _actionRemoveGrid: QAction
    _actionRemoveLabel: QAction
    _actionSaveAsCsv: QAction
    _actionViewAsPixelimage: QAction
    _actionExportCellsToImages: QAction
    autosave: bool
    def __init__(self):
        QMainWindow.__init__(self)
        
    def getManualItem(self) -> QStandardItem:
        raise NotImplementedError()
    
    def getScale(self):
        raise NotImplementedError()
    
    def getPos(self):
        raise NotImplementedError()

    def getPosX(self):
        raise NotImplementedError()
    
    def getPosY(self):
        raise NotImplementedError()
    
    def setPosX(self, x):
        raise NotImplementedError()
    
    def setPosY(self, y):
        raise NotImplementedError()
    
    def appendGrid(self, text):
        raise NotImplementedError()
    
    def activateRectGroup(self, text):
        raise NotImplementedError()
    
    def deactivateRectGroup(self, text):
        raise NotImplementedError()
    
    def clearAIItem(self):
        raise NotImplementedError()
    
    def fetchData(self,x,y,ex,ey):
        raise NotImplementedError()

    def fetchFullData(self):
        raise NotImplementedError()
    
    def getAIIgnoreRects(self) -> list:
        raise NotImplementedError()
    
    def drawImage(self):
        raise NotImplementedError()
    
    def setStatusText(self, text):
        raise NotImplementedError()
    
    def imageWidth(self):
        raise NotImplementedError()

    def imageHeight(self):
        raise NotImplementedError()
    
    def reloadProperyWindowByGrid(self, grid):
        raise NotImplementedError()
    
    def reloadPropertyWindow(self, selection: QItemSelection):
        raise NotImplementedError()
    
    def getImage(self) -> AbstractImage:
        raise NotImplementedError()
    
    def getAIItem(self) -> QStandardItem:
        raise NotImplementedError()
        
    def getTree(self) -> AbstractTreeHelper:
        raise NotImplementedError()
    
    def setLastModel(self, name, model_train):
        raise NotImplementedError()
    
    def getModel(self, name):
        raise NotImplementedError()
    
    def hasModel(self, name) -> bool:
        raise NotImplementedError()
    
    def drawImgAndMinimap(self):
        raise NotImplementedError()
