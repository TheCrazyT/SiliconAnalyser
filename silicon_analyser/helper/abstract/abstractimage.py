import abc
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal
import typing
import numpy as np
from silicon_analyser.grid import Grid
from silicon_analyser.rect import Rect

class AbstractImage(QLabel):
    onRectChanged: pyqtSignal
    
    @abc.abstractmethod
    def getImageHeight(self) -> int:
        raise NotImplementedError()

    @abc.abstractmethod
    def getImageWidth(self) -> int:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def clearAIRects(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def fetchData(self,x,y,ex,ey) -> np.ndarray[int,typing.Any]:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def drawImage(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def fetchFullData(self) -> np.ndarray[int,typing.Any]:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def appendRectGroup(self, text):
         raise NotImplementedError()

    @abc.abstractmethod
    def appendAIRectGroup(self, text):
         raise NotImplementedError()
    
    @abc.abstractmethod
    def appendGridRectGroup(self, grid, text):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def appendAIGridRectGroup(self, grid, text):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def activateGridRectGroup(self, grid, text):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def deactivateGridRectGroup(self, grid, text):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def activateAIGridRectGroup(self, grid, text):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def deactivateAIGridRectGroup(self, grid, text):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def activateRectGroup(self, text):
        raise NotImplementedError()

    @abc.abstractmethod
    def deactivateRectGroup(self, text):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def activateAIRectGroup(self, text):
        raise NotImplementedError()

    @abc.abstractmethod
    def deactivateAIRectGroup(self, text):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def appendAIRect(self,key,x,y,ex,ey):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def appendAIGrid(self, text):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def activateAIGrid(self, text):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def getRects(self) -> dict[str,Rect]:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def getGrids(self) -> dict[str,Grid]:
         raise NotImplementedError()
    
    @abc.abstractmethod
    def removeRectGroup(self, label):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def removeGrid(self, label):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def appendGrid(self, text):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def activateGrid(self, text):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def getAIIgnoreRects(self) -> list:
        raise NotImplementedError()