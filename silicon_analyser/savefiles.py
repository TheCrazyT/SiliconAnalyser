import logging
logger = logging.getLogger(__name__)

import json
from json import JSONDecoder, JSONEncoder
from PyQt5.QtCore import pyqtSignal, QObject, QSemaphore
from silicon_analyser.grid import Grid
from silicon_analyser.rect import Rect

SAVE_RECTS = "rects.json"
SAVE_GRIDS = "grids.json"
doSaveRects = False
doSaveGrids = False

class JSONGridDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, *args, **kwargs)
    def decode(self, *args, **kwargs):
        d = super().decode(*args, **kwargs)
        grids = {}
        for gridName in d:
            item = d[gridName]
            name = item["name"]
            if gridName != name:
                raise Exception("invalid gridname")
            x = item["x"]
            y = item["y"]
            cols = item["cols"]
            rows = item["rows"]
            width = item["width"]
            height = item["height"]
            g: Grid = Grid(name, x , y, cols, rows, width, height)
            g._rects = item["_rects"]
            g._rectsActive = item["_rectsActive"]
            if "shearX" in item:
                g.shearX = item["shearX"]
            else:
                g.shearX = 0
            if "shearY" in item:
                g.shearY = item["shearY"]
            else:
                g.shearY = 0
            grids[gridName] = g
        return grids
        
class MyJSONEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

class Saving(QObject):
    onSaving = pyqtSignal()
    
    def __init__(self, semaphore: QSemaphore):
        super().__init__()
        self.semaphore = semaphore

    def loadRects(self) -> dict[str, Rect]:
        with open(SAVE_RECTS,"r") as f:
            return json.load(f)

    def loadGrids(self) -> dict[str, Grid]:
        with open(SAVE_GRIDS,"r") as f:
            return json.load(f, cls=JSONGridDecoder)
        
    def triggerSaveRects(self):
        global doSaveRects
        logger.info("triggerSaveRects")
        doSaveRects = True

    def triggerSaveGrids(self):
        global doSaveGrids
        logger.info("triggerSaveGrids")
        doSaveGrids = True

    def saveRects(self,rects):
        global doSaveRects
        if doSaveRects:
            logger.info("acquire semaphore")
            self.semaphore.acquire()
            logger.info("semaphore acquired")
            try:
                logger.info("saveRects")
                with open(SAVE_RECTS,"w") as f:
                    json.dump(rects, f, cls = MyJSONEncoder)
                doSaveRects = False
            finally:
                logger.info("release semaphore")
                self.semaphore.release()
                logger.info("semaphore released")

    def saveGrids(self,grids):
        global doSaveGrids
        if doSaveGrids:
            self.onSaving.emit()
            logger.info("acquire semaphore")
            self.semaphore.acquire()
            logger.info("semaphore acquired")
            try:
                logger.info("saveGrids")
                with open(SAVE_GRIDS,"w") as f:
                    json.dump(grids, f, cls = MyJSONEncoder)
                doSaveGrids = False
            finally:
                logger.info("release semaphore")
                self.semaphore.release()
                logger.info("semaphore released")
