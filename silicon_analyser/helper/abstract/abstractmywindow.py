import abc
from PyQt5.QtCore import QItemSelection, pyqtSignal, QSemaphore
from PyQt5.QtWidgets import QMainWindow, QAction
from PyQt5.QtGui import QStandardItem

from silicon_analyser.helper.abstract.abstractimage import AbstractImage
from silicon_analyser.helper.abstract.abstracttreehelper import AbstractTreeHelper
from silicon_analyser.savefiles import Saving

class AbstractMyWindow(QMainWindow):
    _actionSaveModel: QAction
    _actionLoadModel: QAction
    _actionRemoveGrid: QAction
    _actionRemoveLabel: QAction
    _actionSaveAsCsv: QAction
    _actionViewAsPixelimage: QAction
    _actionExportCellsToImages: QAction
    _actionDecisionTree: QAction
    _actionNeuralNetwork: QAction
    _actionGridAddXRowsBottom: QAction
    _actionGridAddXRowsTop: QAction
    _actionGridRemoveXRowsTop: QAction
    _actionGridRemoveXRowsBottom: QAction
    _actionGridAddXColumnsLeft: QAction
    _actionGridAddXColumnsRight: QAction
    _actionGridRemoveXColumnsLeft: QAction
    _actionGridRemoveXColumnsRight: QAction
    autosave: bool
    onRectChanged: pyqtSignal
    
    def __init__(self):
        QMainWindow.__init__(self)
    
    @abc.abstractmethod
    def getMainSemaphore(self) -> QSemaphore:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def getManualItem(self) -> QStandardItem:
        raise NotImplementedError()

    @abc.abstractmethod
    def getScale(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def getPos(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def getPosX(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def getPosY(self):
        raise NotImplementedError()
    
    def setPosX(self, x):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def setPosY(self, y):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def appendGrid(self, text):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def activateRectGroup(self, text):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def deactivateRectGroup(self, text):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def clearAIItem(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def fetchData(self,x,y,ex,ey):
        raise NotImplementedError()

    @abc.abstractmethod
    def fetchFullData(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def getAIIgnoreRects(self) -> list:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def drawImage(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def setStatusText(self, text: str):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def setErrorStatus(self, text: str):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def imageWidth(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def imageHeight(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def reloadProperyWindowByGrid(self, grid):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def reloadPropertyWindow(self, selection: QItemSelection):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def getImage(self) -> AbstractImage:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def getAIItem(self) -> QStandardItem:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def getTree(self) -> AbstractTreeHelper:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def setLastModel(self, name, model_train):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def getModel(self, name):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def hasModel(self, name) -> bool:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def drawImgAndMinimap(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def disableComputeButton(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def disableAutoComputeButton(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def disableAddLabelButton(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def disableAddGridButton(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def enableComputeButton(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def enableAutoComputeButton(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def enableAddLabelButton(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def enableAddGridButton(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def getSaving(self) -> Saving:
        raise NotImplementedError()

