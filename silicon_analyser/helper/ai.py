import logging
logger = logging.getLogger(__name__)

import numpy as np
import random

from silicon_analyser.helper.abstract.abstractcomputationmethod import AbstractComputationMethod
from silicon_analyser.grid import Grid, getAllCellRects
from silicon_analyser.helper.abstract.abstractimage import AbstractImage
from silicon_analyser.helper.tree import Tree
from silicon_analyser.treeitem import TreeItem


def blockshaped(arr, nrows: int, ncols: int):
    """
    Return an array of shape (n, nrows, ncols) where
    n * nrows * ncols = arr.size

    If arr is a 2D array, the returned array should look like n subblocks with
    each subblock preserving the "physical" layout of arr.
    """
    h, w, v = arr.shape
    assert h % nrows == 0, f"{h} rows is not evenly divisible by {nrows}"
    assert w % ncols == 0, f"{w} cols is not evenly divisible by {ncols}"
    return (arr.reshape(h//nrows, nrows, -1, ncols, v)
               .swapaxes(1,2)
               .reshape(-1, nrows, ncols, v))
    
def getDefaultMaxWMaxH(grid: Grid) -> tuple[int,int]:
    maxW = int(grid.getCellWidth())
    maxH = int(grid.getCellHeight())
    MP = 5
    if maxW % MP != 0:
        maxW += MP - (maxW % MP)
    if maxH % MP != 0:
        maxH += MP - (maxH % MP)
    return maxW, maxH

# TODO: maybe deprecated, not shure yet
def initTrainAndValsForRects(rects, ignoreRects):
    maxW = 0
    maxH = 0
    cntTotal = 0
    for k in rects.keys():
        for x,y,ex,ey in rects[k]:
            maxW = max(maxW, ex-x)
            maxH = max(maxH, ey-y)
            cntTotal += 1

    for x,y,ex,ey in ignoreRects:
        maxW = max(maxW, ex-x)
        maxH = max(maxH, ey-y)
        cntTotal += 1
    cntTotal += 100
    MP=5
    if maxW % MP != 0:
        maxW += MP - (maxW % MP)
    if maxH % MP != 0:
        maxH += MP - (maxH % MP)
    countGroups = len(rects.keys())+1
    train = np.zeros(shape=(cntTotal,maxH,maxW,3),dtype=np.float32)
    vals = np.zeros(shape=(cntTotal,countGroups),dtype=np.float32)
    logger.info(f"train.shape:{train.shape}")
    logger.info(f"vals.shape:{vals.shape}")
    return maxW, maxH, countGroups, MP, train, vals

def initTrainAndValsForGrid(grid:Grid) -> tuple[int, int, list[str], int, int, np.ndarray, np.ndarray]:
    labels = grid.getLabels()
    countGroups = len(labels)
    cntTotal = 0
    for l in labels:
        for cx in range(0,grid.cols):
            for cy in range(0,grid.rows):
                if grid.isRectSet(cx,cy,l):
                    cntTotal += 1
    maxW = grid.width//grid.cols
    maxH = grid.height//grid.rows
    MP = 5
    if maxW % MP != 0:
        maxW += MP - (maxW % MP)
    if maxH % MP != 0:
        maxH += MP - (maxH % MP)
    train = np.zeros(shape=(cntTotal,maxH,maxW,3),dtype=np.float32)
    vals = np.zeros(shape=(cntTotal,countGroups),dtype=np.float32)
    logger.info(f"train.shape:{train.shape}")
    logger.info(f"vals.shape:{vals.shape}")
    return  maxW, maxH, labels, countGroups, MP, train, vals

# TODO: maybe deprecated, not shure yet
def appendFoundRects(img: AbstractImage, rectKeys, maxW, maxH, MP, computationMethod: AbstractComputationMethod):
            bx = 10000
            by = 10000
            data = img.fetchFullData()[:,:,0:3]
            dx = data.shape[0]
            dy = data.shape[1]
            dx -= dx % bx
            dy -= dy % by
            maxCnt = 20
            data = data[0:dx,0:dy]
            logger.info(f"data.shape: {data.shape}")
            computationMethod.build(input_shape=[1,*data.shape[0:2],3])
            subdataIdx = 0
            cnt = 0
            for subdata in blockshaped(data, bx, by):
                if cnt < maxCnt:
                    logger.info(f"subdata.shape:{subdata.shape}")
                    r = computationMethod.predict(np.array([subdata]))
                    logger.info(f"r.shape:{r.shape}")
                    for rx in range(0,r.shape[0]):
                        for ry in range(0,r.shape[1]):
                            if cnt >= maxCnt:
                                continue
                            x = rx + int(subdataIdx * subdata.shape[0]) % data.shape[0]
                            y = ry + (int(subdataIdx * subdata.shape[0]) // data.shape[0])*subdata.shape[1]
                            idx = np.argmax(r[rx,ry])
                            if(idx > 0):
                                x *= MP
                                y *= MP
                                key = rectKeys[idx-1]
                                ex = x+maxW
                                ey = y+maxH
                                img.appendAIRect(key,x,y,ex,ey)
                                cnt += 1
                subdataIdx += 1
                
def appendFoundCellRects(img: AbstractImage, grid: Grid, aiGrid: Grid, maxW: int, maxH: int, computationMethod: AbstractComputationMethod):
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
        a = np.zeros((maxH,maxW,3))
        data = img.fetchData(x,y,ex,ey)
        a[0:data.shape[0],0:data.shape[1]] = data
        dataList.append(a)
        dataIndexes.append((cx,cy))
    data = np.array(dataList,dtype=np.float32)
    logger.info(f"data.shape:{data.shape}")
    r = computationMethod.predict(data)
    logger.info(f"r.shape:{r.shape}")
    for ri in range(0,r.shape[0]):
        currentRec = r[ri]
        lblIdx = np.argmax(currentRec, axis=-1).flatten()[0]
        rx, ry = dataIndexes[ri]
        aiGrid.setRect(rx,ry,labels[lblIdx])
        
 # TODO: maybe deprecated, not shure yet
def prepareRectData(tree: Tree, img: AbstractImage, rects, countGroups, ignoreRects, maxW, maxH, train, vals):
    tree.clearAIItem()
    i = 0
    ii = 1
    logger.info(f"adding ignore values ({len(ignoreRects)})")
        
    for n in range(0,100):
        x = random.randint(0,img.width()-maxW)
        y = random.randint(0,img.height()-maxH)
        data = img.fetchData(x,y,x+maxW-1,y+maxH-1)
        train[i,0:data.shape[0],0:data.shape[1]] = data
        vals[i] = np.eye(countGroups,dtype=np.float32)[0]
        i += 1
        
    for x,y,ex,ey in ignoreRects:
        data = img.fetchData(x,y,x+maxW-1,y+maxH-1)
        train[i,0:data.shape[0],0:data.shape[1]] = data
        vals[i] = np.eye(countGroups,dtype=np.float32)[0]
        i += 1
        
    logger.info("adding values")
    for k in rects.keys():
        tree.addTreeItem(k,"ai")
        for x,y,ex,ey in rects[k]:
            data = img.fetchData(x,y,x+maxW-1,y+maxH-1)
            train[i,0:maxH,0:maxW] = data
            vals[i] = np.eye(countGroups,dtype=np.float32)[ii]
            i += 1
        ii += 1

def prepareGridData(tree: Tree, img: AbstractImage, grid: Grid, labels: list[str], aiGridRectsActive: dict[str,bool], countGroups, maxW, maxH, train, vals) -> Grid:
    tree.clearAIItem()
    i = 0
    ii = 0
    aiGrid, aiTreeItem = tree.addTreeItem(grid.name,TreeItem.TYPE_AI_GRID)
    for l in labels:
        shouldUncheck = not aiGridRectsActive[l]
        _,treeItem = tree.addTreeItem(l,TreeItem.TYPE_AI_GRID_ITEM,aiGrid,aiTreeItem)
        if(shouldUncheck):
            treeItem.uncheck()
        for cx in range(0,grid.cols):
            for cy in range(0,grid.rows):
                if grid.isRectSet(cx,cy,l):
                    x = grid.absX(cx,cy)
                    y = grid.absY(cy,cx)
                    ex = x + maxW - 1
                    ey = y + maxH - 1
                    data = img.fetchData(x,y,ex,ey)
                    train[i,0:data.shape[0],0:data.shape[1]] = data
                    vals[i] = np.eye(countGroups,dtype=np.float32)[ii]
                    i += 1
        ii += 1
    tree.expandAll()
    return aiGrid # type: ignore