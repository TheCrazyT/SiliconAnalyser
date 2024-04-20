from functools import lru_cache
from PyQt5.QtCore import Qt, QRect, QSize, QTimer
from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtGui import QImage, QPixmap, QColor, QMouseEvent, QPainter, QPen, QBrush
import typing
import numpy as np
from silicon_analyser.helper.abstract.abstractmywindow import AbstractMyWindow
from silicon_analyser.savefiles import triggerSaveGrids, triggerSaveRects, saveGrids, saveRects
from silicon_analyser.grid import Grid
from silicon_analyser.rect import Rect
from silicon_analyser.treeitem import TreeItem

class FullImage(QLabel):
    _rects: dict[str, list[Rect]]
    _aiRects: dict[str, list[Rect]]
    _rectActive: dict[str, bool]
    _grids: dict[str, Grid]
    _aiGrids: dict[str, Grid]
    _gridsActive: dict[str, bool]
    _aiGridsActive: dict[str, bool]
    _moveStartX: int
    _moveStartY: int
    _moveDeltaX: int
    _moveDeltaY: int
    _moveTimer: QTimer
    _saveTimer: QTimer
    
    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self._drawRectStart = False
        self._rectStartX = 0
        self._rectStartY = 0
        self._rectEndX = 0
        self._rectEndY = 0
        self._grids = {}
        self._aiGrids = {}
        self._gridsActive = {}
        self._aiGridsActive = {}
        self._rects = {}
        self._aiRects = {}
        self._rectActive = {}
        self._aiRectActive = {}
        self._aiIgnoreRects = []
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self._moveTimer = QTimer()
        self._moveTimer.timeout.connect(self.moveUpdate)
        self._moveTimer.setInterval(int(1000 * 0.2))
        self._moveStart = False
        self._saveTimer = QTimer()
        self._saveTimer.timeout.connect(self.doSave)
        self._saveTimer.setInterval(int(1000 * 10)) #save every 10 seconds
        self._saveTimer.start()
    
    def doSave(self):
        saveRects(self._rects)
        saveGrids(self._grids)
        
    def moveUpdate(self):
        posX, posY = self._myWindow.getPos()
        posX += self._moveDeltaX
        posY += self._moveDeltaY
        self._myWindow.setPosX(posX)
        self._myWindow.setPosY(posY)
        self._myWindow.drawImgAndMinimap()
    
    def initialize(self, myWindow: AbstractMyWindow, pixmap: QPixmap):
        self._myWindow = myWindow
        self._pixmap: QPixmap = pixmap
        self._currentImg = pixmap
    
    def getRects(self) -> dict[str,list[Rect]]:
        return self._rects
    
    def getAiRects(self) -> dict[str,list[Rect]]:
        return self._aiRects
    
    def getAIIgnoreRects(self) -> list:
        return self._aiIgnoreRects
    
    def markGridItem(self,evx,evy,button):
        scale = self._myWindow.getScale()
        posX, posY = self._myWindow.getPos()
        sposX, sposY = posX*scale, posY*scale
        for k in self._grids.keys():
            if self._gridsActive[k]:
                grid: Grid = self._grids[k]
                x,y,ex,ey = grid.x, grid.y, grid.x + grid.width, grid.y + grid.height
                x = int(self._translatePixelToScaled(x)-sposX)
                y = int(self._translatePixelToScaled(y)-sposY)
                ex = int(self._translatePixelToScaled(ex)-sposX)
                ey = int(self._translatePixelToScaled(ey)-sposY)
                if ex<x:
                    x,ex = ex,x
                if ey<y:
                    y,ey = ey,y
                if x < evx and y < evy and ex > evx and ey > evy:
                    tevx = self._translateEventToPixel(evx)
                    tevy = self._translateEventToPixel(evy)
                    rx = grid.x - posX
                    ry = grid.y - posY
                    if button == Qt.MouseButton.LeftButton:
                        grid.setRect(int((tevx - rx)/(grid.getCellWidth())),int((tevy - ry)/(grid.getCellHeight())), self._myWindow.getTree().selectedLabel())
                    if button == Qt.MouseButton.RightButton:
                        grid.unsetRect(int((tevx - rx)/(grid.getCellWidth())),int((tevy - ry)/(grid.getCellHeight())), self._myWindow.getTree().selectedLabel())
                    if self._myWindow.autosave:
                        triggerSaveGrids()
                    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._moveStart = True
            self._moveStartX = event.x()
            self._moveStartY = event.y()
            self._moveDeltaX = 0
            self._moveDeltaY = 0
        tree = self._myWindow.getTree()
        if tree.selectedType() == TreeItem.TYPE_GRID_ITEM:
            self.markGridItem(event.x(),event.y(),event.button())
            return
        if event.button() == Qt.MouseButton.LeftButton:
            print("FullImage: mousePressEvent",self._drawRectStart)
            if tree.selectedType() is not None:
                if not self._drawRectStart:
                    self._drawRectStart = True
                    self._rectStartX = self._translateEventToPixel(event.x())
                    self._rectStartY = self._translateEventToPixel(event.y())
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._moveStart:
            self._moveDeltaX = event.x() - self._moveStartX
            self._moveDeltaY = event.y() - self._moveStartY
            self._moveTimer.start()

        if self._drawRectStart:
            self._rectEndX = self._translateEventToPixel(event.x())
            self._rectEndY = self._translateEventToPixel(event.y())
            if(self._rectEndX < self._rectStartX):
                self._rectEndX, self._rectStartX = self._rectStartX, self._rectEndX
            if(self._rectEndY < self._rectStartY):
                self._rectEndY, self._rectStartY = self._rectStartY, self._rectEndY
            pixmap = self._currentImg.copy()
            qp = QPainter(pixmap)
            brush = QBrush(QColor(255,0,0,127))
            pen = QPen(Qt.GlobalColor.red, 2)
            qp.setBrush(brush)
            qp.setPen(pen)
            qp.drawRect(
                self._translatePixelToScaled(self._rectStartX),
                self._translatePixelToScaled(self._rectStartY),
                self._translatePixelToScaled(self._rectEndX)-self._translatePixelToScaled(self._rectStartX),
                self._translatePixelToScaled(self._rectEndY)-self._translatePixelToScaled(self._rectStartY))
            qp.end()
            self.setPixmap(pixmap)
     
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._moveStart = False
            self._moveTimer.stop()
            
        if event.button() == Qt.MouseButton.LeftButton:
            self._drawRectStart = False
            print("mouseReleaseEvent",self._rectStartX,self._rectStartY,self._rectEndX,self._rectEndY)
            selectedKey: str = self._myWindow.getTree().selectedLabel()
            if selectedKey is not None:
                x = self._rectStartX
                y = self._rectStartY
                ex = self._rectEndX
                ey = self._rectEndY
                if selectedKey in self._rects:
                    self.appendRect(selectedKey,x,y,ex,ey)
                if selectedKey in self._grids:
                    grid: Grid = self._grids[selectedKey]
                    posX, posY = self._myWindow.getPos()
                    grid.x = posX+x
                    grid.y = posY+y
                    grid.width = ex-x
                    grid.height = ey-y
                    grid.recalcCell()
                    self._grids[selectedKey] = grid
                    print(f"grid resized: {id(grid)}")
                    self._myWindow.reloadProperyWindowByGrid(grid)
                    if self._myWindow.autosave:
                        triggerSaveGrids()
                self.drawImage()
        if event.button() == Qt.MouseButton.RightButton:
            print("right click")
            self.removeRectAt(event.x(),event.y())
    
    def removeRectGroup(self, label):
        self._rects.pop(label, None)
        self._aiRects.pop(label, None)
        self._rectActive.pop(label, None)
        self._aiRectActive.pop(label, None)
        
    def removeGrid(self, label):
        self._grids.pop(label, None)
        self._aiGrids.pop(label, None)
        self._gridsActive.pop(label, None)
        self._aiGridsActive.pop(label, None)

    def removeRectAt(self, evx, evy):
        scale = self._myWindow.getScale()
        posX, posY = self._myWindow.getPos()
        sposX, sposY = posX*scale, posY*scale
        for k in self._rects.keys():
            toRemove = []
            if self._rectActive[k]:
                for i in range(0,len(self._rects[k])):
                    rect: Rect = self._rects[k][i]
                    x,y,ex,ey = rect.x, rect.y, rect.ex, rect.ey
                    x = int(self._translatePixelToScaled(x)-sposX)
                    y = int(self._translatePixelToScaled(y)-sposY)
                    ex = int(self._translatePixelToScaled(ex)-sposX)
                    ey = int(self._translatePixelToScaled(ey)-sposY)
                        
                    if ex < x:
                        x,ex = ex,x
                    if ey < y:
                        y,ey = ey,y
                    if x < evx and y < evy and ex > evx and ey > evy:
                        toRemove.append(i)
            for i in  sorted(toRemove, reverse=True):
                print(f"remove {i}")
                del self._rects[k][i]
        
        for k in self._aiRects.keys():
            toRemove = []
            if self._aiRectActive[k]:
                for i in range(0,len(self._aiRects[k])):
                    rect: Rect = self._aiRects[k][i]
                    x,y,ex,ey = rect.x, rect.y, rect.ex, rect.ey
                    x = int(self._translatePixelToScaled(x)-sposX)
                    y = int(self._translatePixelToScaled(y)-sposY)
                    ex = int(self._translatePixelToScaled(ex)-sposX)
                    ey = int(self._translatePixelToScaled(ey)-sposY)
                        
                    if ex<x:
                        x,ex = ex,x
                    if ey<y:
                        y,ey = ey,y
                    if x<evx and y<evy and ex>evx and ey>evy:
                        toRemove.append(i)
            for i in sorted(toRemove, reverse=True):
                print(f"remove {i}")
                self._aiIgnoreRects.append(self._aiRects[k][i])
                del self._aiRects[k][i]
                
        self.drawImage()
        if  self._myWindow.autosave:
            triggerSaveRects()
            triggerSaveGrids()

    def appendRect(self,key,x,y,ex,ey):
        self._appendRect(key, self._rects, x, y, ex, ey)
        if self._myWindow.autosave:
            triggerSaveRects()

    def _appendRect(self, key, rects, x, y, ex, ey, ignorePos = False):
        if ignorePos:
            rects[key].append(Rect(
                x,
                y,
                ex,
                ey
            ))
        else:
            posX, posY = self._myWindow.getPos()
            rects[key].append(Rect(
                posX+x,
                posY+y,
                posX+ex,
                posY+ey
            ))
                
    def appendAIRect(self,key,x,y,ex,ey):
        self._appendRect(key, self._aiRects, x, y, ex, ey, True)

    def fetchFullData(self) -> np.ndarray[int,typing.Any]:
        temp = QImage(self._pixmap.toImage())
        ptr = temp.constBits()
        ptr.setsize(temp.byteCount())
        return np.ndarray((temp.height(), temp.width(), 4), buffer=ptr, strides=[temp.bytesPerLine(), 4, 1], dtype=np.uint8) # type: ignore
    
    def fetchData(self,x:float,y:float,ex:float,ey:float) -> np.ndarray[int,typing.Any]:
        x = int(x)
        ex = int(ex)
        y = int(y)
        ey = int(ey)
        arr = self.fetchFullData()
        r = arr[y:ey+1,x:ex+1,0:3]
        return r
        
    def loadRects(self, rects):
        self._rects = rects
        
    def loadGrids(self, grids):
        for g1_name in self._grids:
            for g2_name in grids:
                if(g1_name == g2_name):
                    self._grids[g1_name].replaceValues(grids[g2_name])
        
    def _translateEventToPixel(self, v):
        return int(v/self._myWindow.getScale())
    
    def _translatePixelToScaled(self, v):
        return int(v*self._myWindow.getScale())
    
    def clearAIRects(self):
        self._aiGridsActive = {}
        self._aiGrids = {}
        self._aiRects = {}
        self._aiRectActive = {}
    
    # TODO: maybe deprecated, not shure yet
    def drawRectOnScaledImg(self, scaledImg: QPixmap):
        qp = QPainter(scaledImg)
        brush = QBrush(QColor(0,0,255,80))
        pen = QPen(Qt.GlobalColor.blue, 2)
        qp.setBrush(brush)
        qp.setPen(pen)
        self._drawRectOnScaledImg(self._rects, self._rectActive, qp)
        brush = QBrush(QColor(0,255,0,80))
        pen = QPen(Qt.GlobalColor.green, 2)
        qp.setBrush(brush)
        qp.setPen(pen)
        self._drawRectOnScaledImg(self._aiRects, self._aiRectActive, qp)
        qp.end()
        
    def drawGridOnScaledImg(self, scaledImg: QPixmap):
        qp = QPainter(scaledImg)
        brush = QBrush(QColor(0,0,255,80))
        pen = QPen(Qt.GlobalColor.blue, 2)
        qp.setBrush(brush)
        qp.setPen(pen)
        self._drawGridOnScaledImg(self._grids, self._gridsActive, qp, TreeItem.TYPE_GRID_ITEM)

        brush = QBrush(QColor(0,255,0,80))
        pen = QPen(QColor(0,0,0,0), 2)
        qp.setBrush(brush)
        qp.setPen(pen)
        self._drawGridOnScaledImg(self._aiGrids, self._aiGridsActive, qp, TreeItem.TYPE_AI_GRID_ITEM, QColor(0,255,0,40), QColor(0,255,0,127), QColor(0,0,0,0))

        qp.end()
    
    def calcGridCellsVisibleRange(self, grid: Grid):
        posX, posY = self._myWindow.getPos()
        scale = self._myWindow.getScale()
        cellWidth = grid.getCellWidth()
        cellHeight = grid.getCellHeight()
        
        startCol = -(grid.x - posX)//cellWidth
        startCol = int(max(0, startCol))
        
        startRow = -(grid.y - posY)//cellHeight
        startRow = int(max(0, startRow))
        
        endCol = int((grid.x + grid.width - posX)//cellWidth)
        endRow = int((grid.y + grid.height - posY)//cellHeight)
        
        maxColsCnt = (self.width() / cellWidth)/scale
        maxRowsCnt = (self.height() / cellHeight)/scale
        
        endCol = max(int(startCol + maxColsCnt),endCol)
        endRow = max(int(startRow + maxRowsCnt),endRow)
        endCol = int(min(endCol, grid.cols))
        endRow = int(min(endRow, grid.rows))
        
        return (startCol, startRow, endCol, endRow)
        
    def getGrids(self) -> dict[str,Grid]:
        return self._grids
        
    def _drawGridOnScaledImg(self, grids: dict[str,Grid], gridsActive: dict[str,bool], qp:QPainter, gridItemType:str, rectSetColor:QColor = QColor(0,255,255,40), rectSetActiveColor:QColor = QColor(0,255,255,127), rectUnsetColor:QColor = QColor(0,0,255,20)):
        activeBrush = QBrush(rectSetActiveColor)
        nonActiveBrush = QBrush(rectSetColor)
        unsetBrush = QBrush(rectUnsetColor)
        posX, posY = self._myWindow.getPos()
        scale = self._myWindow.getScale()
        sposX, sposY = posX*scale, posY*scale
        for k in grids.keys():
            if gridsActive[k]:
                grid: Grid = grids[k]
                cellWidth = grid.getCellWidth()
                cellHeight = grid.getCellHeight()
                startCol, startRow, endCol, endRow = self.calcGridCellsVisibleRange(grid)
                for row in range(startRow,endRow):
                    if not self._drawGridOnScaledImgRow(qp, gridItemType, activeBrush, nonActiveBrush, unsetBrush, sposX, sposY, grid, cellWidth, cellHeight, startCol, endCol, row):
                        break

    def _drawGridOnScaledImgRow(self, qp:QPainter, gridItemType:str, activeBrush:QBrush, nonActiveBrush:QBrush, unsetBrush:QBrush, sposX:float, sposY:float, grid:Grid, cellWidth:float, cellHeight:float, startCol:int, endCol:int, row:int):
        oy = grid.absY(row, 0)
        y = int(self._translatePixelToScaled(oy)-sposY)
        if y >= self.height():
            return False
        for col in range(startCol,endCol):
            oy = grid.absY(row, col)
            y = int(self._translatePixelToScaled(oy)-sposY)
            ox = grid.absX(col, row)
            ex = ox + cellWidth
            ey = oy + cellHeight
            x = int(self._translatePixelToScaled(ox)-sposX)
            if x > self.width():
                break
            ex = int(self._translatePixelToScaled(ex)-sposX)
            ey = int(self._translatePixelToScaled(ey)-sposY)
            w = ex - x
            h = ey - y
            if x>=0 and y>=0 and x<=self.width() and y<=self.height():
                if grid.isRectSet(col,row):
                    rectLabel = grid.rectLabel(col, row)
                    if self._myWindow.getTree().isItemSelected(rectLabel, grid.name, gridItemType):
                        brush = activeBrush
                    else:
                        brush = nonActiveBrush
                    qp.setBrush(brush)
                else:
                    brush = unsetBrush
                    qp.setBrush(brush)
                qp.drawRect(x,y,w,h)
        return True

    # TODO: maybe deprecated, not shure yet                        
    def _drawRectOnScaledImg(self, rects, rectActive, qp:QPainter):
        posX, posY = self._myWindow.getPos()
        scale = self._myWindow.getScale()
        sposX, sposY = posX*scale, posY*scale
        for k in rects.keys():
            if rectActive[k]:
                for r in rects[k]:
                    x,y,ex,ey = r.x, r.y, r.ex, r.ey
                    x = int(self._translatePixelToScaled(x)-sposX)
                    y = int(self._translatePixelToScaled(y)-sposY)
                    ex = int(self._translatePixelToScaled(ex)-sposX)
                    ey = int(self._translatePixelToScaled(ey)-sposY)
                    w = ex - x
                    h = ey - y
                    if x>=0 and y>=0 and x<=self.width() and y<=self.height():
                        qp.drawRect(x,y,w,h)

    def drawImage(self):
        posX, posY = self._myWindow.getPos()
        scale = self._myWindow.getScale()
        rect = QRect(int(posX), int(posY), int(self.width()/scale), int(self.height()/scale))
        cropped = self._pixmap.copy(rect)
        scaled = cropped.scaled(QSize(int(self.width()), int(self.height())))
        self._currentImg = scaled
        self.drawRectOnScaledImg(scaled)
        self.drawGridOnScaledImg(scaled)
        self.setPixmap(scaled)
    
    def appendAIGrid(self, text):
        grid = self._grids[text]
        aiGrid = Grid(grid.name,grid.x,grid.y,grid.cols,grid.rows,grid.width,grid.height)
        aiGrid.shearX = grid.shearX
        aiGrid.shearY = grid.shearY
        self._aiGrids[text] = aiGrid
        return aiGrid
    
    def appendGrid(self, text):
        grid = Grid(text,0,0,20,20,20*10,20*10)
        self._grids[text] = grid
        self._myWindow.reloadProperyWindowByGrid(grid)
        if self._myWindow.autosave:
            triggerSaveGrids()
        return self._grids[text]
    
    def activateAIGrid(self, text):
        self._aiGridsActive[text] = True
        self.drawImage()

    def activateGrid(self, text: str):
        self._gridsActive[text] = True
        self.drawImage()

    def deactivateGrid(self, text: str):
        self._gridsActive[text] = False
        self.drawImage()
    
    def appendAIGridRectGroup(self, grid: Grid, text: str):
        grid.addRectGroup(text)
    
    def appendGridRectGroup(self, grid: Grid, text: str):
        grid.addRectGroup(text)
    
    def activateAIGridRectGroup(self, grid: Grid, text: str):
        grid.rectActive(text)

    def deactivateAIGridRectGroup(self, grid: Grid, text: str):
        grid.rectDeactive(text)

    def activateGridRectGroup(self, grid: Grid, text: str):
        grid.rectActive(text)

    def deactivateGridRectGroup(self, grid: Grid, text: str):
        grid.rectDeactive(text)

    def appendRectGroup(self, text: str):
        self._rects[text] = []
    
    def activateRectGroup(self, text: str):
        self._rectActive[text] = True
        self.drawImage()

    def deactivateRectGroup(self, text: str):
        self._rectActive[text] = False
        self.drawImage()
        
    def appendAIRectGroup(self, text: str):
        self._aiRects[text] = []
    
    def activateAIRectGroup(self, text: str):
        self._aiRectActive[text] = True
        self.drawImage()

    def deactivateAIRectGroup(self, text: str):
        self._aiRectActive[text] = False
        self.drawImage()
        
    def getImageHeight(self) -> int:
        return self._pixmap.height()

    def getImageWidth(self) -> int:
        return self._pixmap.width()