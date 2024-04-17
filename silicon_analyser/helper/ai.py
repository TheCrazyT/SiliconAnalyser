import typing
import os
import numpy as np
os.environ["KERAS_BACKEND"] = "torch"
import keras
from silicon_analyser.grid import Grid, getAllCellRects
from silicon_analyser.helper.abstract.abstractimage import AbstractImage

def getDefaultMaxWMaxH(grid: Grid) -> tuple[int,int]:
    maxW = int(grid.getCellWidth())
    maxH = int(grid.getCellHeight())
    MP = 5
    if maxW % MP != 0:
        maxW += MP - (maxW % MP)
    if maxH % MP != 0:
        maxH += MP - (maxH % MP)
    return maxW, maxH

def appendFoundCellRects(img: AbstractImage, grid: Grid, aiGrid: Grid, maxW: int, maxH: int, model: keras.Sequential):
    if maxW is None or maxH is None:
        maxW, maxH = getDefaultMaxWMaxH(grid)
    labels = grid.getLabels()
    allCellRects = getAllCellRects(grid)
    dataList = []
    dataIndexes = []
    for cx,cy in allCellRects:
        x = grid.absX(cx,cy)
        y = grid.absY(cy,cx)
        ex = int(x + maxW - 1)
        ey = int(y + maxH - 1)
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