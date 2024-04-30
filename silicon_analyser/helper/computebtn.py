import logging

from silicon_analyser.helper.tree import Tree
logger = logging.getLogger(__name__)

from sklearn.model_selection import train_test_split
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QMouseEvent

from silicon_analyser.dialogs.compute_stats import ComputeStatsDlg
from silicon_analyser.helper.abstract.abstractcomputationmethod import AbstractComputationMethod
from silicon_analyser.helper.abstract.abstractmywindow import AbstractMyWindow
from silicon_analyser.grid import Grid
from silicon_analyser.helper.computation_methods.decision_tree import DecisionTree
from silicon_analyser.helper.computation_methods.neural_network import NeuralNetwork
from silicon_analyser.treeitem import TreeItem
from silicon_analyser.helper.ai import appendFoundCellRects, appendFoundRects, initTrainAndValsForRects, initTrainAndValsForGrid, prepareRectData, prepareGridData
from silicon_analyser.helper.common import isSingleThread


class Worker(QObject):
    _computeStatsDlg: ComputeStatsDlg
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    updateSignal = pyqtSignal([dict,int])

    
    def __init__(self,myWindow: AbstractMyWindow, computeStatsDlg: ComputeStatsDlg):
        QObject.__init__(self)
        self._myWindow = myWindow
        self._computeStatsDlg = computeStatsDlg

    def run(self):
        useDecisionTree = self._myWindow._actionDecisionTree.isChecked()
        useNeuralNetwork = self._myWindow._actionNeuralNetwork.isChecked()
        computationMethod: AbstractComputationMethod
        if useNeuralNetwork:
            self._computeStatsDlg.setStatus("Loading ...")
            computationMethod = NeuralNetwork(self._computeStatsDlg, self._computeStatsDlg.request_graph_update)
            self._computeStatsDlg.setStatus("Using neural network")
        
        if useDecisionTree:
            computationMethod = DecisionTree(self._computeStatsDlg, self._computeStatsDlg.request_graph_update)
            self._computeStatsDlg.setStatus("Using decision tree")
        
        logger.info("_worker runs")
        try:
            self._computeStatsDlg.reset()
            selectedType = self._myWindow.getTree().selectedType()
            gridMode = (selectedType == TreeItem.TYPE_GRID) or (selectedType == TreeItem.TYPE_GRID_ITEM) or (selectedType == TreeItem.TYPE_AI_GRID) or (selectedType == TreeItem.TYPE_AI_GRID_ITEM)
            rects = self._myWindow.getImage().getRects()
            ignoreRects = self._myWindow.getImage().getAIIgnoreRects()
            self._myWindow.setStatusText("training in progress")

            if gridMode:
                grid: Grid = self._myWindow.getTree().getSelectedGrid()
                maxW, maxH, labels, countGroups, MP, train, vals = initTrainAndValsForGrid(grid)
            else:
                maxW, maxH, countGroups, MP, train, vals = initTrainAndValsForRects(rects, ignoreRects)
            
            computationMethod.createModels(countGroups, maxW, maxH, MP)
            
            if gridMode:
                rectsActive = {}
                tree: Tree = self._myWindow.getTree()
                aiGrid: Grid|None = tree.getSelectedAIGrid()
                if aiGrid is None:
                    for l in labels:
                        rectsActive[l] = True
                else:
                    rectsActive = aiGrid.getRectLabelsActive()
                aiGrid = prepareGridData(self._myWindow.getTree(), self._myWindow.getImage(), grid, labels, rectsActive, countGroups, maxW, maxH, train, vals)
            else:
                prepareRectData(self._myWindow.getTree(), self._myWindow.getImage(), rects, countGroups, ignoreRects, maxW, maxH, train, vals)
            
            logger.info(f"before fit")
            logger.info(f"vals:{vals}")
            logger.info(f"train.shape:{train.shape}")
            logger.info(f"vals.shape:{vals.shape}")
            
            xtraining, ytraining, xvalidation, yvalidation = train_test_split(train,vals,shuffle = True,test_size=0.1) 
           
            self.updateSignal.connect(lambda x,y:self._computeStatsDlg.request_graph_update.emit(x, y))
            self.updateSignal.connect(lambda x,_:self._myWindow.setStatusText("Accuracy: %s" % x["accuracy"]))
            computationMethod.fit(xtraining, ytraining, xvalidation, yvalidation)
            if gridMode:
                appendFoundCellRects(self._myWindow.getImage(), grid, aiGrid, maxW, maxH, computationMethod)
            else:
                appendFoundRects(self._myWindow.getImage(), list(rects.keys()), maxW, maxH, MP, computationMethod)
            self._computeStatsDlg.setStatus(computationMethod.getFinishText())
           
            self._myWindow.getImage().drawImage()
            if useNeuralNetwork:
                self._myWindow.setLastModel(aiGrid.name, computationMethod.getLastModel())
        except Exception as e:
            logging.exception(e)
            self._computeStatsDlg.setError(e)
        finally:
            self.finished.emit()
        
class ComputeBtn(QPushButton):
    _computeStatsDlg: ComputeStatsDlg

    def __init__(self, text: str):
        QPushButton.__init__(self, text)
        self._computeStatsDlg = ComputeStatsDlg()
        self.clicked.connect(self.buttonClicked)
      
    def initialize(self, myWindow: AbstractMyWindow):
        self._myWindow = myWindow
    
    def finished(self):
        self.setText("Compute")
        self.setEnabled(True)
        logger.info("finished")
        
    def buttonClicked(self, event: QMouseEvent):
        logger.info("ComputeBtn: buttonClicked")
        self._computeStatsDlg.show()
        self._worker = Worker(self._myWindow,self._computeStatsDlg)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread = QThread()
        self._worker.finished.connect(self._thread.quit)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self.finished)
        self.setText("...")
        self.setEnabled(False)
        if isSingleThread():
            self._worker.run()
        else:
            self._thread.start()