import logging
logger = logging.getLogger(__name__)

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from sklearn.model_selection import train_test_split

from silicon_analyser.grid import Grid
from silicon_analyser.helper.abstract.abstractcomputationmethod import AbstractComputationMethod
from silicon_analyser.helper.abstract.abstractimage import AbstractImage
from silicon_analyser.helper.abstract.abstractmywindow import AbstractMyWindow
from silicon_analyser.helper.ai import appendFoundCellRects, appendFoundRects, initTrainAndValsForGrid, initTrainAndValsForRects, prepareGridData, prepareRectData
from silicon_analyser.helper.computation_methods.decision_tree import DecisionTree
from silicon_analyser.helper.computation_methods.neural_network import NeuralNetwork
from silicon_analyser.helper.tree import Tree
from silicon_analyser.treeitem import TreeItem

class Worker(QObject):
    finished = pyqtSignal(AbstractComputationMethod)
    completed = pyqtSignal()
    updateSignal = pyqtSignal([dict,int])
    
    def __init__(self, myWindow: AbstractMyWindow, computationMethod:AbstractComputationMethod|None, lastSelectedGrid: Grid|None, lastSelectedAIGrid: Grid|None, lastSelectedType: str|None):
        QObject.__init__(self)
        self._myWindow = myWindow
        self.updateSignal.connect(lambda logs,epoch:logger.info(f"epoch: {epoch} accuracy: {logs['accuracy']} val_accuracy: {logs['val_accuracy']}"))
        self.updateSignal.connect(lambda logs,epoch:myWindow.setStatusText(f"epoch: {epoch} accuracy: {logs['accuracy']} val_accuracy: {logs['val_accuracy']}"))
        self.computationMethod = computationMethod
        self.lastSelectedGrid = lastSelectedGrid
        self.lastSelectedAIGrid = lastSelectedAIGrid
        self.lastSelectedType = lastSelectedType
        self.triggered = True
    
    def trigger(self):
        logger.info("trigger")
        self.triggered = True
        
    def run(self):
        self.running = True
        myWindow: AbstractMyWindow = self._myWindow
        useDecisionTree = myWindow._actionDecisionTree.isChecked()
        useNeuralNetwork = myWindow._actionNeuralNetwork.isChecked()
        computationMethod: AbstractComputationMethod
        img: AbstractImage = myWindow.getImage()
        tree: Tree = myWindow.getTree()
        intitialitedCellWidth: float
        intitialitedCellHeight: float
        
        selectedType = self.lastSelectedType
        gridMode = (selectedType == TreeItem.TYPE_GRID) or (selectedType == TreeItem.TYPE_GRID_ITEM) or (selectedType == TreeItem.TYPE_AI_GRID) or (selectedType == TreeItem.TYPE_AI_GRID_ITEM)
        if gridMode:
            maybeGrid: Grid|None = self.lastSelectedGrid
            if maybeGrid is None:
                return
            grid = maybeGrid
            intitialitedCellWidth = grid.getCellWidth()
            intitialitedCellHeight = grid.getCellHeight()

        
        if self.computationMethod is None:
            if useNeuralNetwork:
                myWindow.setStatusText("Loading ...")
                computationMethod = NeuralNetwork(None,self.updateSignal)
                myWindow.setStatusText("Using neural network")
            
            if useDecisionTree:
                computationMethod = DecisionTree(None,self.updateSignal)
                myWindow.setStatusText("Using decision tree")
        else:
            computationMethod = self.computationMethod
            computationMethod.setOnUpdate(self.updateSignal)
            myWindow.setStatusText("Loaded last model")
        logger.info("worker runs")
        while self.running:
            QThread.sleep(1)
            try:
                logger.info("acquire semaphore")
                self._myWindow.getMainSemaphore().acquire()
                logger.info("semaphore acquired")
                if self.triggered:
                    self.triggered = False
                    logger.info("worker trigger runs")
                    try:
                        rects = img.getRects()
                        ignoreRects = img.getAIIgnoreRects()
                        myWindow.setStatusText("training in progress")

                        grid: Grid
                        if gridMode:
                            maybeGrid: Grid|None = self.lastSelectedGrid
                            if maybeGrid is None:
                                return
                            grid = maybeGrid
                            
                            if (grid.getCellHeight() != intitialitedCellHeight) or (grid.getCellWidth() != intitialitedCellWidth):
                                break
                            maxW, maxH, labels, countGroups, MP, train, vals = initTrainAndValsForGrid(grid)
                        else:
                            maxW, maxH, countGroups, MP, train, vals = initTrainAndValsForRects(rects, ignoreRects)
                        
                        computationMethod.loadOrCreateModel(countGroups, maxW, maxH, MP)
                        
                        aiGrid: Grid
                        if gridMode:
                            maybeAiGrid: Grid|None = self.lastSelectedAIGrid
                            rectsActive = {}
                            if maybeAiGrid is None:
                                for l in labels:
                                    rectsActive[l] = True
                            else:
                                aiGrid = maybeAiGrid
                                rectsActive = aiGrid.getRectLabelsActive()
                            aiGrid = prepareGridData(tree, img, grid, labels, rectsActive, countGroups, maxW, maxH, train, vals)
                            self.lastSelectedAIGrid = aiGrid
                        else:
                            prepareRectData(tree, img, rects, countGroups, ignoreRects, maxW, maxH, train, vals)
                        
                        xtraining, ytraining, xvalidation, yvalidation = train_test_split(train,vals,shuffle = True,test_size=0.1) 
                    
                        computationMethod.fit(xtraining, ytraining, xvalidation, yvalidation, 1)
                        if gridMode:
                            appendFoundCellRects(img, grid, aiGrid, maxW, maxH, computationMethod)
                        else:
                            appendFoundRects(img, list(rects.keys()), maxW, maxH, MP, computationMethod)
                        myWindow.setStatusText(computationMethod.getFinishText())
                    
                        img.drawImage()
                        if useNeuralNetwork:
                            myWindow.setLastModel(aiGrid.name, computationMethod.getLastModel())
                    except Exception as e:
                        logging.exception("Exception during auto-compute")
                        myWindow.setErrorStatus(repr(e))
                        break
                    finally:
                        self.finished.emit(computationMethod)
            finally:
                logger.info("release semaphore")
                self._myWindow.getMainSemaphore().release()
                logger.info("semaphore released")
        self.running = False
        self.completed.emit()

class AutoComputeBtn(QPushButton):
    computationMethodChanged = pyqtSignal()
    active = pyqtSignal()
    unactive = pyqtSignal()
    
    def initialize(self, myWindow: AbstractMyWindow):
        self._worker: Worker|None = None
        self._myWindow = myWindow
        self.lastComputationMethod = None
        self.lastSelectedGrid = None
        self.lastSelectedAIGrid = None
        self.lastSelectedType: str|None = None
        self.clicked.connect(self.buttonClicked)
        myWindow.getImage().onRectChanged.connect(self.rectSet)
        self.computationMethodChanged.connect(self.onComputationMethodChanged)
        
    def onComputationMethodChanged(self):
        logger.info("onComputationMethodChanged")
        self.lastComputationMethod = None
        
    def finished(self, lastComputationMethod: AbstractComputationMethod):
        logger.info("finished")
        self.lastComputationMethod = lastComputationMethod
        lastAccuracy = lastComputationMethod.getLastValAccuracy()
        if lastAccuracy < 1.0:
            logger.info("timer start")
            if self._worker is not None:
                self._worker.trigger()
        else:
            logger.info(f"timer stop (lastAccuracy={lastAccuracy})")
    
    def rectSet(self):
        logger.info("rectSet event")
        logger.info("timer start")
        if self._worker is not None:
            self._worker.trigger()
    
    def newThread(self):
        logger.info("newThread")
        self._worker = Worker(self._myWindow, self.lastComputationMethod, self.lastSelectedGrid, self.lastSelectedAIGrid, self.lastSelectedType)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread = QThread()
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self.finished)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()
        self._worker.completed.connect(self.activateButton)
        self._worker.completed.connect(lambda:logger.info("worker completed"))
    
    def activateButton(self):
        self.unactive.emit()
        self.setChecked(False)
        
    def buttonClicked(self, event: QMouseEvent):
        logger.info("AutoComputeBtn: buttonClicked")
        tree: Tree = self._myWindow.getTree()
        self.lastSelectedGrid = tree.getSelectedGrid()
        self.lastSelectedAIGrid = tree.getSelectedAIGrid()
        self.lastSelectedType = tree.selectedType()
        if self.isChecked():
            self.active.emit()
            self.newThread()
            if self._worker is not None:
                self._worker.trigger()
        else:
            self.unactive.emit()
            if self._worker is not None:
                self._worker.running = False
            self._thread.quit()
