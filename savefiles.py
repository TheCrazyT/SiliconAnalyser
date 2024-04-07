import json
from json import JSONDecoder, JSONEncoder
from grid import Grid

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
            grids[gridName] = g
        return grids
        
class MyJSONEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

def loadRects():
    with open(SAVE_RECTS,"r") as f:
        return json.load(f)

def loadGrids():
    with open(SAVE_GRIDS,"r") as f:
        return json.load(f, cls=JSONGridDecoder)
    
def triggerSaveRects():
    global doSaveRects
    print("triggerSaveRects")
    doSaveRects = True

def triggerSaveGrids():
    global doSaveGrids
    print("triggerSaveGrids")
    doSaveGrids = True

def saveRects(rects):
    global doSaveRects
    print("saveRects")
    if doSaveRects:
        with open(SAVE_RECTS,"w") as f:
            json.dump(rects, f, cls = MyJSONEncoder)
        doSaveRects = False

def saveGrids(grids):
    global doSaveGrids
    print("saveGrids")
    if doSaveGrids:
        with open(SAVE_GRIDS,"w") as f:
            json.dump(grids, f, cls = MyJSONEncoder)
        doSaveGrids = False