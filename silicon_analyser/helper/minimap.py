from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap, QPainter, QPen, QMouseEvent
from silicon_analyser.helper.abstract.abstractmywindow import AbstractMyWindow

class MiniMap(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self, parent)
    
    def initialize(self, myWindow: AbstractMyWindow, pixmap: QPixmap):
        self._myWindow = myWindow
        self._pixmap = pixmap
        
    def mouseReleaseEvent(self,event: QMouseEvent):
        print("clicked")
        sc1x = 300/self._pixmap.width()
        sc1y = 300/self._pixmap.height()
        self._myWindow.setPosX(int(event.x()/sc1x))
        self._myWindow.setPosY(int(event.y()/sc1y))
        self._myWindow.drawImgAndMinimap()
        print(self._myWindow.getPosX(),self._myWindow.getPosY())

    def scaleMinimapX(self):
        return 300/self._pixmap.width()
    
    def scaleMinimapY(self):
        return 300/self._pixmap.height()

    def drawMinimap(self):
        minimapPm = self._pixmap.scaled(QSize(300, 300))
        posX, posY = self._myWindow.getPos()
        scale = self._myWindow.getScale()
        qp = QPainter(minimapPm)
        pen = QPen(Qt.red, 2)
        qp.setPen(pen)
        sc1x = self.scaleMinimapX()
        sc2x = sc1x/scale
        sc1y = self.scaleMinimapY()
        sc2y = sc1y/scale
        qp.drawRect(int(posX*sc1x),int(posY*sc1y),int(300*sc2x),int(300*sc2y))
        qp.end()
        self.setPixmap(minimapPm)