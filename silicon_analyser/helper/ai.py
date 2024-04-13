import numpy as np
import keras
from silicon_analyser.grid import Grid, getAllCellRects
from silicon_analyser.helper.abstract.abstractimage import AbstractImage

def getDefaultMaxWMaxH(grid: Grid):
    maxW = grid.width//grid.cols
    maxH = grid.height//grid.rows
    MP = 5
    if maxW % MP != 0:
        maxW += MP - (maxW % MP)
    if maxH % MP != 0:
        maxH += MP - (maxH % MP)
    return maxW, maxH

def appendFoundCellRects(img: AbstractImage, grid: Grid, aiGrid: Grid, maxW, maxH, model: keras.Sequential):
    if maxW is None or maxH is None:
        maxW, maxH = getDefaultMaxWMaxH(grid)
    labels = grid.getLabels()
    allCellRects = getAllCellRects(grid)
    dataList = []
    dataIndexes = []
    for cx,cy in allCellRects:
        x = int(grid.x + cx*maxW)
        y = int(grid.y + cy*maxH)
        ex = x + maxW - 1
        ey = y + maxH - 1
        dataList.append(img.fetchData(x,y,ex,ey))
        dataIndexes.append((cx,cy))
    data = np.array(dataList,dtype=np.float32)
    print("data.shape",data.shape)
    r = model.predict(data)
    print("r.shape",r.shape)
    for ri in range(0,r.shape[0]):
        currentRec = r[ri]
        lblIdx = np.argmax(currentRec)
        rx, ry = dataIndexes[ri]
        aiGrid.setRect(rx,ry,labels[lblIdx])