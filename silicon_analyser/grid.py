class Grid:
    _rects: dict[list[list[int]]]
    _rectsActive: dict[bool]
    def __init__(self, name, x, y, cols, rows, width, height):
        self.name = name
        self.x = x
        self.y = y
        self.cols = cols
        self.rows = rows
        self.width = width
        self.height = height
        self._rects = {}
        self._rectsActive = {}
        print(f"init grid:{id(self)}")
    
    def replaceValues(self,grid):
        self.x = grid.x
        self.y = grid.y
        self.cols = grid.cols
        self.rows = grid.rows
        self.width = grid.width
        self.height = grid.height
        self._rects = grid._rects
        for k in self._rects:
            for cx,cy in list(self._rects[k]):
                if cx < 0 or cy < 0:
                    self._rects[k].remove([cx,cy])
        self._rectsActive = grid._rectsActive
        
    def getLabels(self) -> list[str]:
        return self._rects.keys()
    
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
        self.rows += 1
        for label in self._rects:
            for i in range(0,len(self._rects[label])):
                col, row = self._rects[label][i]
                self._rects[label][i] = [col, row+1]
    
    def setRect(self, col, row, label):
        #print(f"setRect {col} {row} {label}")
        r = [col, row]
        if label not in self._rects:
            self._rects[label] = []
        if r in self._rects[label]:
            self._rects[label].remove(r)
        self._rects[label].append(r)
        
    def unsetRect(self, col, row, label):
        print(f"unsetRect {col} {row}")
        r = [col, row]
        if r in self._rects[label]:
            self._rects[label].remove(r)
    
    def rectLabel(self, col, row) -> str:
        r = [col, row]
        keys = self._rects.keys()
        for k in keys:
            if self._rectsActive[k]:
                if r in self._rects[k]:
                    return k
    
    def isRectSet(self, col ,row, key = None) -> bool:
        r = [col, row]
        if key is None:
            keys = self._rects.keys()
        else:
            keys = [key]
        for k in keys:
            if self._rectsActive[k]:
                if r in self._rects[k]:
                    return True
        return False