from PyQt5.QtCore import Qt, QRect, QSize, QTimer
from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtGui import QImage, QPixmap, QColor, QMouseEvent, QPainter, QPen, QBrush
import numpy as np
from silicon_analyser.helper.abstract.abstractmywindow import AbstractMyWindow
from silicon_analyser.savefiles import saveGrids,saveRects
from silicon_analyser.grid import Grid
from silicon_analyser.rect import Rect
from silicon_analyser.treeitem import TreeItem

class FullImage(QLabel):
    _rects: dict[Rect]
    _aiRects: dict[Rect]
    _rectActive: dict[bool]
    _grids: dict[Grid]
    _aiGrids: dict[Grid]
    _gridsActive: dict[bool]
    _aiGridsActive: dict[bool]
    _moveStartX: int
    _moveStartY: int
    _moveDeltaX: int
    _moveDeltaY: int
    _moveTimer: QTimer
    
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
    
    def getRects(self) -> list[Rect]:
        return self._rects
    
    def getAiRects(self) -> list[Rect]:
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
                    if button == Qt.LeftButton:
                        grid.setRect(int((tevx - (grid.x - posX))/(grid.width/grid.cols)),int((tevy - (grid.y - posY))/(grid.height/grid.rows)), self._myWindow.getTree().selectedLabel())
                    if button == Qt.RightButton:
                        grid.unsetRect(int((tevx - (grid.x - posX))/(grid.width/grid.cols)),int((tevy - (grid.y - posY))/(grid.height/grid.rows)), self._myWindow.getTree().selectedLabel())
                    if self._myWindow.autosave:
                        saveGrids(self._grids)
                    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton:
            self._moveStart = True
            self._moveStartX = event.x()
            self._moveStartY = event.y()
            self._moveDeltaX = 0
            self._moveDeltaY = 0
        tree = self._myWindow.getTree()
        if tree.selectedType() == TreeItem.TYPE_GRID_ITEM:
            self.markGridItem(event.x(),event.y(),event.button())
            return
        if event.button() == Qt.LeftButton:
            print("FullImage: mousePressEvent",self._drawRectStart)
            if tree.selectedType() is not None:
                if not self._drawRectStart:
                    self._drawRectStart = True
                    self._rectStartX = self._translateEventToPixel(event.x())
                    self._rectStartY = self._translateEventToPixel(event.y())
    
    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
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
            pen = QPen(Qt.red, 2)
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
        if event.button() == Qt.MiddleButton:
            self._moveStart = False
            self._moveTimer.stop()
            
        if event.button() == Qt.LeftButton:
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
                    self._grids[selectedKey] = grid
                    print(f"grid resized: {id(grid)}")
                    self._myWindow.reloadProperyWindowByGrid(grid)
                    if self._myWindow.autosave:
                        saveGrids(self._grids)
                self.drawImage()
        if event.button() == Qt.RightButton:
            print("right click")
            self.removeRectAt(event.x(),event.y())
            
    def removeRectGroup(self, label):
        del self._rects[label]
        del self._aiRects[label]
        del self._rectActive[label]
        del self._aiRectActive[label]
        
    def removeGrid(self, label):
        del self._grids[label]
        del self._aiGrids[label]
        del self._gridsActive[label]
        del self._aiGridsActive[label]

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
            saveRects(self._rects)
            saveGrids(self._grids)

    def appendRect(self,key,x,y,ex,ey):
        self._appendRect(key, self._rects, x, y, ex, ey)
        if self._myWindow.autosave:
            saveRects(self._rects)

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

    def fetchFullData(self):
        temp = QImage(self._pixmap.toImage())
        ptr = temp.constBits()
        ptr.setsize(temp.byteCount())
        arr = np.frombuffer(ptr, dtype=np.ubyte).reshape(temp.height(), temp.width(), 4)
        return arr
    
    def fetchData(self,x,y,ex,ey):
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
    
    def drawRectOnScaledImg(self, scaledImg: QPixmap):
        qp = QPainter(scaledImg)
        brush = QBrush(QColor(0,0,255,80))
        pen = QPen(Qt.blue, 2)
        qp.setBrush(brush)
        qp.setPen(pen)
        self._drawRectOnScaledImg(self._rects, self._rectActive, qp)
        brush = QBrush(QColor(0,255,0,80))
        pen = QPen(Qt.green, 2)
        qp.setBrush(brush)
        qp.setPen(pen)
        self._drawRectOnScaledImg(self._aiRects, self._aiRectActive, qp)
        qp.end()
        
    def drawGridOnScaledImg(self, scaledImg: QPixmap):
        qp = QPainter(scaledImg)
        brush = QBrush(QColor(0,0,255,80))
        pen = QPen(Qt.blue, 2)
        qp.setBrush(brush)
        qp.setPen(pen)
        self._drawGridOnScaledImg(self._grids, self._gridsActive, qp, TreeItem.TYPE_GRID_ITEM)

        brush = QBrush(QColor(0,255,0,80))
        pen = QPen(QColor(0,0,0,0), 2)
        qp.setBrush(brush)
        qp.setPen(pen)
        self._drawGridOnScaledImg(self._aiGrids, self._aiGridsActive, qp, TreeItem.TYPE_AI_GRID_ITEM, QColor(0,255,0,40), QColor(0,255,0,127), QColor(0,0,0,0))

        qp.end()
    
    def calcGridCellsVisibleRange(self, grid):
        posX, posY = self._myWindow.getPos()
        scale = self._myWindow.getScale()
        cellWidth = grid.width / grid.cols
        cellHeight = grid.height / grid.rows
        
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
        
    def getGrids(self) -> dict[Grid]:
        return self._grids
        
    def _drawGridOnScaledImg(self, grids, gridsActive, qp:QPainter, gridItemType:str, rectSetColor:QColor = QColor(0,255,255,40), rectSetActiveColor:QColor = QColor(0,255,255,127), rectUnsetColor:QColor = QColor(0,0,255,20)):
        posX, posY = self._myWindow.getPos()
        scale = self._myWindow.getScale()
        sposX, sposY = posX*scale, posY*scale
        for k in grids.keys():
            if gridsActive[k]:
                grid: Grid = grids[k]
                cellWidth = grid.width / grid.cols
                cellHeight = grid.height / grid.rows
                startCol, startRow, endCol, endRow = self.calcGridCellsVisibleRange(grid)
                #for col in range(0,grid.cols):
                #    for row in range(0,grid.rows):
                for col in range(startCol,endCol):
                    for row in range(startRow,endRow):
                        ox = grid.x + col * cellWidth
                        oy = grid.y + row * cellHeight
                        ex = ox + cellWidth
                        ey = oy + cellHeight
                        x = int(self._translatePixelToScaled(ox)-sposX)
                        y = int(self._translatePixelToScaled(oy)-sposY)
                        ex = int(self._translatePixelToScaled(ex)-sposX)
                        ey = int(self._translatePixelToScaled(ey)-sposY)
                        w = ex - x
                        h = ey - y
                        if x>=0 and y>=0 and x<=self.width() and y<=self.height():
                            if grid.isRectSet(col,row):
                                rectLabel = grid.rectLabel(col, row)
                                if self._myWindow.getTree().isItemSelected(rectLabel, grid.name, gridItemType):
                                    brush = QBrush(rectSetActiveColor)
                                else:
                                    brush = QBrush(rectSetColor)
                                qp.setBrush(brush)
                            else:
                                brush = QBrush(rectUnsetColor)
                                qp.setBrush(brush)
                            qp.drawRect(x,y,w,h)
                        
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
        self._aiGrids[text] = aiGrid
        return aiGrid
    
    def appendGrid(self, text):
        grid = Grid(text,0,0,20,20,20*10,20*10)
        self._grids[text] = grid
        self._myWindow.reloadProperyWindowByGrid(grid)
        if self._myWindow.autosave:
            saveGrids(self._grids)
        return self._grids[text]
    
    def activateAIGrid(self, text):
        self._aiGridsActive[text] = True
        self.drawImage()

    def activateGrid(self, text):
        self._gridsActive[text] = True
        self.drawImage()

    def deactivateGrid(self, text):
        self._gridsActive[text] = False
        self.drawImage()
    
    def appendAIGridRectGroup(self, grid: Grid, text):
        grid.addRectGroup(text)
    
    def appendGridRectGroup(self, grid: Grid, text):
        grid.addRectGroup(text)
    
    def activateAIGridRectGroup(self, grid: Grid, text):
        grid.rectActive(text)

    def deactivateAIGridRectGroup(self, grid: Grid, text):
        grid.rectDeactive(text)

    def activateGridRectGroup(self, grid: Grid, text):
        grid.rectActive(text)

    def deactivateGridRectGroup(self, grid: Grid, text):
        grid.rectDeactive(text)

    def appendRectGroup(self, text):
        self._rects[text] = []
    
    def activateRectGroup(self, text):
        self._rectActive[text] = True
        self.drawImage()

    def deactivateRectGroup(self, text):
        self._rectActive[text] = False
        self.drawImage()
        
    def appendAIRectGroup(self, text):
        self._aiRects[text] = []
    
    def activateAIRectGroup(self, text):
        self._aiRectActive[text] = True
        self.drawImage()

    def deactivateAIRectGroup(self, text):
        self._aiRectActive[text] = False
        self.drawImage()
