from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QLabel, QSpinBox
from PyQt5.QtGui import QPixmap, QColor, QPainter, QPen, QBrush
from PyQt5.QtCore import Qt
import os.path as p

class PixelImageDlg(QDialog):
    _img: QLabel
    _rows: QSpinBox
    _cols: QSpinBox
    _pixSize: QSpinBox
    _orgRects: list[list[int]]|None
    _orgRectsRows: int = 0
    _orgRectsCols: int = 0
    _inOriginalEvent: bool = False

    
    def __init__(self):
        super().__init__()
        uic.loadUi(p.abspath(p.join(p.dirname(__file__), '.')) + '/pixel_image.ui', self)
        self._orgRects = None
        img: QLabel = self._img
        img.setPixmap(QPixmap())
        rows: QSpinBox = self._rows
        cols: QSpinBox = self._cols
        pixSize:QSpinBox = self._pixSize
        pixSize.setValue(3)
        rows.valueChanged.connect(self.rowColChanged)
        cols.valueChanged.connect(self.rowColChanged)
        pixSize.valueChanged.connect(self.rowColChanged)

    def rowColChanged(self, *args, **kwargs):
        rows: QSpinBox = self._rows
        cols: QSpinBox = self._cols
        self.drawRects(self.calcNewRects(rows.value(), cols.value()), False)
    
    def calcNewRects(self, rows:int, cols:int) -> list[list[int]]:
        result: list[list[int]] = []
        if self._orgRects is not None:
            for r in self._orgRects:
                i = r[0] + r[1]*self._orgRectsCols
                newCol = i % cols 
                newRow = int((i-newCol) // cols)
                result.append([newCol, newRow])
        return result
    
    def drawRects(self, rects: list[list[int]], isOriginal: bool = True):
        if(self._inOriginalEvent):
            return
        self._inOriginalEvent = True
        try:
            if(len(rects) == 0):
                return
            rectsRows = 0
            rectsCols = 0
            size:int = self._pixSize.value()
            for r in rects:
                rectsCols = max(rectsCols,r[0])
                rectsRows = max(rectsRows,r[1])
            if isOriginal:
                rows: QSpinBox = self._rows
                cols: QSpinBox = self._cols
                rows.setValue(rectsRows)
                cols.setValue(rectsCols)
            img: QLabel = self._img
            pixmap = QPixmap(rectsCols*size,rectsRows*size)
            qp = QPainter(pixmap)
            brush = QBrush(Qt.GlobalColor.white)
            pen = QPen(Qt.GlobalColor.white, 0)
            qp.setBrush(brush)
            qp.setPen(pen)
            qp.drawRect(0,0,rectsCols*size,rectsRows*size)
            brush = QBrush(Qt.GlobalColor.black)
            pen = QPen(Qt.GlobalColor.black, 0)
            qp.setBrush(brush)
            qp.setPen(pen)
            for r in rects:
                if r[1]*size<rectsRows*size and r[0]*size<rectsCols*size:
                    qp.drawRect(r[0]*size,r[1]*size,size,size)
            qp.end()
            if isOriginal:
                self._orgRects = rects
                self._orgRectsRows = rectsRows
                self._orgRectsCols = rectsCols
            img.setMinimumWidth(pixmap.width())
            img.setMinimumHeight(pixmap.height())
            img.setPixmap(pixmap)
        finally:
            self._inOriginalEvent = False
