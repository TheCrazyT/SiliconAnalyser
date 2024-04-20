from functools import lru_cache


class Grid:
    _rects: dict[str,list[list[int]]]
    _rectsActive: dict[str,bool]
    def __init__(self, name, x, y, cols, rows, width, height):
        self.name = name
        self.x = x
        self.y = y
        self.cols = cols
        self.rows = rows
        self.width = width
        self.height = height
        self.shearX = 0
        self.shearY = 0
        self._rects = {}
        self._rectsActive = {}
        self.recalcCell()
        print(f"init grid:{id(self)}")
    
    def recalcCell(self):
        self._cellWidth = self.width / self.cols
        self._cellHeight = self.height / self.rows
    
    def getCellWidth(self) -> float:
        return self._cellWidth

    def getCellHeight(self) -> float:
        return self._cellHeight
    
    def absX(self, col:int, row:int) -> int:
        w = self._cellWidth
        return int(self.x + col*w + self.shearX*row)

    def absY(self, row:int, col:int) -> int:
        h = self._cellHeight
        return int(self.y + row*h + self.shearY*col)
    
    def replaceValues(self,grid):
        self.x = grid.x
        self.y = grid.y
        self.cols = grid.cols
        self.rows = grid.rows
        self.width = grid.width
        self.height = grid.height
        self._rects = grid._rects
        self._cellHeight = grid._cellHeight
        self._cellWidth = grid._cellWidth
        self.shearX = grid.shearX
        self.shearY = grid.shearY
        for k in self._rects:
            for cx,cy in list(self._rects[k]):
                if cx < 0 or cy < 0:
                    self._rects[k].remove([cx,cy])
        self._rectsActive = grid._rectsActive
        
    def getLabels(self) -> list[str]:
        return list(self._rects.keys())
    
    def removeRectGroup(self, label):
        del self._rects[label]
        del self._rectsActive[label]
    
    def addRectGroup(self, text):
        self._rects[text] = []
        self.rectActive(text)
    
    def rectActive(self, text):
        self._rectsActive[text] = True
    
    def rectDeactive(self, text):
        self._rectsActive[text] = False
        
    def addTopRow(self):
        self.y -= int(self.height/self.rows)
        self.height += int(self.height/self.rows)
        self.rows += 1
        for label in self._rects:
            for i in range(0,len(self._rects[label])):
                col, row = self._rects[label][i]
                self._rects[label][i] = [col, row+1]

    def addBottomRow(self):
        self.height += int(self.height/self.rows)
        self.rows += 1
        
    def removeTopRow(self):
        for label in self._rects:
            delEntries = []
            for i in range(0,len(self._rects[label])):
                col, row = self._rects[label][i]
                if row - 1 < 0:
                    delEntries.append(i)
                else:
                    self._rects[label][i] = [col, row-1]
            delEntries = sorted(delEntries, reverse=True)
            for i in delEntries:
                del self._rects[label][i]
        self.y += int(self.height/self.rows)
        self.height -= int(self.height/self.rows)
        self.rows -= 1

    def removeBottomRow(self):
        self.height -= int(self.height/self.rows)
        self.rows -= 1
    
    def setRect(self, col, row, label):
        self.isRectSet.cache_clear()
        self.rectLabel.cache_clear()
        #print(f"setRect {col} {row} {label}")
        r = [col, row]
        if label not in self._rects:
            self._rects[label] = []
        for lbl in self._rects.keys():
            if r in self._rects[lbl]:
                self._rects[lbl].remove(r)
        self._rects[label].append(r)
        
    def unsetRect(self, col, row, label):
        self.isRectSet.cache_clear()
        self.rectLabel.cache_clear()
        print(f"unsetRect {col} {row}")
        r = [col, row]
        if r in self._rects[label]:
            self._rects[label].remove(r)
    
    @lru_cache(maxsize=None)
    def rectLabel(self, col, row) -> str|None:
        r = [col, row]
        keys = self._rects.keys()
        for k in keys:
            if self._rectsActive[k]:
                if r in self._rects[k]:
                    return k
    
    @lru_cache(maxsize=None)
    def isRectSet(self, col , row, key = None) -> bool:
        r = [col, row]
        if key is None:
            keys = self._rects.keys()
        else:
            keys = [key]
        for k in keys:
            if self._rectsActive[k] and r in self._rects[k]:
                return True
        return False

    def getRects(self, key: str) -> list[list[int]]:
        return self._rects[key]
    
def getAllCellRects(grid: Grid):
    cellRects = []
    for cx in range(0,grid.cols):
        for cy in range(0,grid.rows):
            cellRects.append((cx,cy))
    return cellRects