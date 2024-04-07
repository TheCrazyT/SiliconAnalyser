from PyQt5.QtWidgets import QLabel

from grid import Grid
from rect import Rect

class AbstractImage(QLabel):
    
    def clearAIRects(self):
        raise NotImplementedError()
    
    def fetchData(self,x,y,ex,ey):
        raise NotImplementedError()
    
    def drawImage(self):
        raise NotImplementedError()
    
    def fetchFullData(self):
        raise NotImplementedError()
    
    def appendAIGridRectGroup(self, grid, text):
        raise NotImplementedError()
    
    def activateAIGridRectGroup(self, grid, text):
        raise NotImplementedError()
    
    def deactivateAIGridRectGroup(self, grid, text):
        raise NotImplementedError()
    
    def activateAIRectGroup(self, text):
        raise NotImplementedError()

    def deactivateAIRectGroup(self, text):
        raise NotImplementedError()
    
    def appendAIRect(self,key,x,y,ex,ey):
        raise NotImplementedError()
    
    def appendAIGrid(self, text):
        raise NotImplementedError()
    
    def activateAIGrid(self, text):
        raise NotImplementedError()
    
    def getRects(self) -> list[Rect]:
        raise NotImplementedError()
    
    def getGrids(self) -> dict[Grid]:
         raise NotImplementedError()