from sklearn.model_selection import train_test_split
import os
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QMouseEvent
import random
import numpy as np
import sys
from silicon_analyser.dialogs.compute_stats import ComputeStatsDlg
from silicon_analyser.helper.abstract.abstractmywindow import AbstractMyWindow
from silicon_analyser.grid import Grid
from silicon_analyser.treeitem import TreeItem
from silicon_analyser.helper.ai import appendFoundCellRects
# because debugging in multithread can cause problems (breakpoints don't work)
# I added this method ...
def isSingleThread():
    if "SINGLE_THREAD" not in os.environ:
        return False
    return "1" == os.environ["SINGLE_THREAD"]

def blockshaped(arr, nrows, ncols):
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

class Worker(QObject):
    _computeStatsDlg: ComputeStatsDlg
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    
    def __init__(self,myWindow: AbstractMyWindow, computeStatsDlg: ComputeStatsDlg):
        QObject.__init__(self)
        self._myWindow = myWindow
        self._computeStatsDlg = computeStatsDlg

    def run(self):
        self._computeStatsDlg.setStatus("Initialize keras ...")
        os.environ["KERAS_BACKEND"] = "torch"
        import keras
        self._computeStatsDlg.setStatus("... finished Initializing keras")
        
        def appendFoundRects(self, rectKeys, maxW, maxH, model_conv, MP):
            import keras_cv
            bx = 10000
            by = 10000
            data = self._myWindow.getImage().fetchFullData()[:,:,0:3]
            dx = data.shape[0]
            dy = data.shape[1]
            dx -= dx % bx
            dy -= dy % by
            maxCnt = 20
            data = data[0:dx,0:dy]
            print("data.shape", data.shape)
            model_conv.build(input_shape=[1,*data.shape[0:2],3])
            subdataIdx = 0
            cnt = 0
            for subdata in blockshaped(data, bx, by):
                if cnt < maxCnt:
                    print("subdata.shape",subdata.shape)
                    r = model_conv(np.array([subdata]))[0]
                    r = r.cpu().detach().numpy()
                    print("r.shape",r.shape)
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
                                self._myWindow.getImage().appendAIRect(key,x,y,ex,ey)
                                cnt += 1
                subdataIdx += 1

        class MyPlottingCallback(keras.callbacks.Callback):
            def __init__(self, plotDlg: ComputeStatsDlg):
                self._plotDlg = plotDlg
            
            def on_epoch_end(self, epoch, logs=None): 
                if logs is None:
                    return
                self._plotDlg.request_graph_update.emit(logs, epoch)
                if self._plotDlg.isStop():
                    self.model.stop_training = True # type: ignore
            
        class MyThresholdCallback(keras.callbacks.Callback):
            def __init__(self, threshold, patience):
                super(MyThresholdCallback, self).__init__()
                self.threshold = threshold
                self.patience = patience
                self.count = 0

            def on_epoch_end(self, epoch, logs=None): 
                if logs is None:
                    return
                val_acc = logs["val_accuracy"]
                if val_acc >= self.threshold:
                    if self.count > self.patience:
                        self.model.stop_training = True # type: ignore
                    else:
                        self.count += 1
                else:
                    self.count = 0
        
        print("_worker runs")
        try:
            self._computeStatsDlg.reset()
            selectedType = self._myWindow.getTree().selectedType()
            gridMode = (selectedType == TreeItem.TYPE_GRID) or (selectedType == TreeItem.TYPE_GRID_ITEM) or (selectedType == TreeItem.TYPE_AI_GRID) or (selectedType == TreeItem.TYPE_AI_GRID_ITEM)
            rects = self._myWindow.getImage().getRects()
            ignoreRects = self._myWindow.getImage().getAIIgnoreRects()
            self._myWindow.setStatusText("training in progress")

            if gridMode:
                grid: Grid = self._myWindow.getTree().getSelectedGrid()
                maxW, maxH, labels, countGroups, MP, train, vals = self.initTrainAndValsForGrid(grid)
            else:
                maxW, maxH, countGroups, MP, train, vals = self.initTrainAndValsForRects(rects, ignoreRects)

            model_conv, model_train = self.createModels(keras, countGroups, maxW, maxH, MP)
            
            if gridMode:
                aiGrid = self.prepareGridData(grid, labels, countGroups, maxW, maxH, train, vals)
            else:
                self.prepareRectData(rects, countGroups, ignoreRects, maxW, maxH, train, vals)
            
            callbacks = [MyPlottingCallback(self._computeStatsDlg),MyThresholdCallback(0.99,200)]
            model_train.compile(optimizer=keras.optimizers.Adam(learning_rate=0.002),loss="binary_crossentropy",metrics=["accuracy"])
            print("before fit")
            print("vals",vals)
            print("train.shape",train.shape)
            print("vals.shape",vals.shape)
            
            xtraining, ytraining, xvalidation, yvalidation = train_test_split(train,vals,shuffle = True,test_size=0.1) 

            history = model_train.fit(
                x = xtraining,
                y = xvalidation,
                epochs = 100000,
                verbose = 0,
                validation_data=(ytraining,yvalidation),
                shuffle = True,
                batch_size = 512,
                callbacks = callbacks
            )
            
            print("after fit")
            self._myWindow.setStatusText("Accuracy: %s" % history.history["accuracy"][-1])
            
            if gridMode:
                appendFoundCellRects(self._myWindow.getImage(), grid, aiGrid, maxW, maxH, model_train)
            else:
                appendFoundRects(self, list(rects.keys()), maxW, maxH, model_conv, MP)
            
            self._myWindow.getImage().drawImage()
            self._myWindow.setLastModel(aiGrid.name, model_train)
        except Exception as e:
            self._computeStatsDlg.setError(e)
        finally:
            self.finished.emit()
    
    # TODO: maybe deprecated, not shure yet
    def initTrainAndValsForRects(self, rects, ignoreRects):
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
        print("train.shape:",train.shape)
        print("vals.shape:",vals.shape)
        return maxW, maxH, countGroups, MP, train, vals

    def initTrainAndValsForGrid(self, grid:Grid) -> tuple[int, int, list[str], int, int, np.ndarray, np.ndarray]:
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
        print("train.shape:",train.shape)
        print("vals.shape:",vals.shape)
        return  maxW, maxH, labels, countGroups, MP, train, vals

    # TODO: maybe deprecated, not shure yet
    def prepareRectData(self, rects, countGroups, ignoreRects, maxW, maxH, train, vals):
        self._myWindow.getTree().clearAIItem()
        i = 0
        ii = 1
        print(f"adding ignore values ({len(ignoreRects)})")
            
        for n in range(0,100):
            x = random.randint(0,self._myWindow.imageWidth()-maxW)
            y = random.randint(0,self._myWindow.imageHeight()-maxH)
            data = self._myWindow.getImage().fetchData(x,y,x+maxW-1,y+maxH-1)
            train[i,0:data.shape[0],0:data.shape[1]] = data
            vals[i] = np.eye(countGroups,dtype=np.float32)[0]
            i += 1
            
        for x,y,ex,ey in ignoreRects:
            data = self._myWindow.getImage().fetchData(x,y,x+maxW-1,y+maxH-1)
            train[i,0:data.shape[0],0:data.shape[1]] = data
            vals[i] = np.eye(countGroups,dtype=np.float32)[0]
            i += 1
            
        print("adding values")
        for k in rects.keys():
            self._myWindow.getTree().addTreeItem(k,"ai")
            for x,y,ex,ey in rects[k]:
                data = self._myWindow.getImage().fetchData(x,y,x+maxW-1,y+maxH-1)
                    #np.save(f"samples/{i}.bin",data)
                train[i,0:maxH,0:maxW] = data
                vals[i] = np.eye(countGroups,dtype=np.float32)[ii]
                i += 1
            ii += 1

    def prepareGridData(self, grid: Grid, labels, countGroups, maxW, maxH, train, vals) -> Grid:
        self._myWindow.getTree().clearAIItem()
        i = 0
        ii = 0
        aiGrid, aiTreeItem = self._myWindow.getTree().addTreeItem(grid.name,TreeItem.TYPE_AI_GRID)
        for l in labels:
            self._myWindow.getTree().addTreeItem(l,TreeItem.TYPE_AI_GRID_ITEM,aiGrid,aiTreeItem)
            for cx in range(0,grid.cols):
                for cy in range(0,grid.rows):
                    if grid.isRectSet(cx,cy,l):
                        x = int(grid.x + cx*maxW)
                        y = int(grid.y + cy*maxH)
                        ex = x + maxW - 1
                        ey = y + maxH - 1
                        data = self._myWindow.getImage().fetchData(x,y,ex,ey)
                        train[i,0:maxH,0:maxW] = data
                        #np.save(f"samples/{l}_{cx:03d}_{cy:03d}_{x:04d}_{y:04d}.bin",data)
                        vals[i] = np.eye(countGroups,dtype=np.float32)[ii]
                        i += 1
            ii += 1
        return aiGrid

    def createModels(self, keras, countGroups, maxW, maxH, MP):
        conv2 = keras.layers.Conv2D(
                countGroups*5,
                name="conv2d_2",
                kernel_size=(int(maxH//MP-5),int(maxW//MP-5)),
                activation="softmax"
        )

        conv3 = keras.layers.Conv2D(
                countGroups,
                name="conv2d_3",
                kernel_size=(1+5,1+5),
                activation="softmax"
        )

        model_conv = keras.Sequential([
            keras.layers.BatchNormalization(),
            keras.layers.MaxPooling2D(MP),
            conv2,
            conv3
        ])

        model_train = keras.Sequential([
            keras.layers.Input((maxH,maxW,3)),
            keras.layers.BatchNormalization(),
            keras.layers.MaxPooling2D(MP),
            conv2,
            conv3,
            keras.layers.Reshape((countGroups,))
        ])
        model_train.summary()
        return model_conv,model_train
        
class ComputeBtn(QPushButton):
    _computeStatsDlg: ComputeStatsDlg

    def __init__(self, text: str):
        QPushButton.__init__(self, text)
        self._computeStatsDlg = ComputeStatsDlg()
        self.clicked.connect(self.buttonClicked)
      
    def initialize(self, myWindow: AbstractMyWindow):
        self._myWindow = myWindow
    
    def buttonClicked(self, event: QMouseEvent):
        print("ComputeBtn: buttonClicked")
        self._computeStatsDlg.show()
        self._worker = Worker(self._myWindow,self._computeStatsDlg)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread = QThread()
        self._worker.finished.connect(self._thread.quit)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(
            lambda: print("finished")
        )
        self._thread.finished.connect(
            lambda: self.setText("Compute")
        )
        self._thread.finished.connect(
            lambda: self.setEnabled(True)
        )
        self.setText("...")
        self.setEnabled(False)
        if isSingleThread():
            self._worker.run()
        else:
            self._thread.start()