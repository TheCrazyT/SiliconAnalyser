import logging

logger = logging.getLogger(__name__)

import torch
import importlib.metadata
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtCore import Qt, QItemSelection, QSemaphore
from PyQt5.QtWidgets import QFileDialog, QMenu, QTableView, QStatusBar, QAction
from PyQt5.QtGui import QPixmap, QStandardItem, QStandardItemModel
from os import path as p
import sys

import silicon_analyser.savefiles
from silicon_analyser.savefiles import Saving
from silicon_analyser.helper.abstract.abstracttreehelper import AbstractTreeHelper
from silicon_analyser.helper.abstract.abstractimage import AbstractImage
from silicon_analyser.helper.abstract.abstractmywindow import AbstractMyWindow
from silicon_analyser.helper.minimap import MiniMap
from silicon_analyser.helper.fullimage import FullImage
from silicon_analyser.helper.addlabelbtn import AddLabelBtn
from silicon_analyser.helper.computebtn import ComputeBtn
from silicon_analyser.helper.autocomputebtn import AutoComputeBtn
from silicon_analyser.helper.addgridbtn import AddGridBtn
from silicon_analyser.treeitem import TreeItem
from silicon_analyser.helper.properties import PropertiesUtil
from silicon_analyser.grid import Grid
from silicon_analyser.treeitem import TreeItem
from silicon_analyser.helper.tree import Tree

class MyWindow(AbstractMyWindow):
    _mainSemaphore: QSemaphore
    _tree: Tree
    _properties: QTableView
    _addLabelBtn: AddLabelBtn
    _autoComputeBtn: AutoComputeBtn
    _computeBtn: ComputeBtn
    _addGridBtn: AddGridBtn
    _statusBar: QStatusBar
    _minimap: MiniMap
    _image: FullImage
    _models: dict[str,object]
    _actionGridAddXRowsTop: QAction
    _actionGridAddXRowsBottom: QAction
    _actionGridRemoveXRowsTop: QAction
    _actionGridRemoveXRowsBottom: QAction
    _actionGridAddXColumnsLeft: QAction
    _actionGridAddXColumnsRight: QAction
    _actionGridRemoveXColumnsLeft: QAction
    _actionGridRemoveXColumnsRight: QAction
    _actionSaveModel: QAction
    _actionLoadModel: QAction
    _actionRemoveGrid: QAction
    _actionRemoveLabel: QAction
    _actionMade_by_TheCrazyT: QAction
    _actionUrl: QAction
    _actionSaveAsCsv: QAction
    _actionViewAsPixelimage: QAction
    _actionExportCellsToImages: QAction
    _actionDecisionTree: QAction
    _actionNeuralNetwork: QAction
    _actionSiliconpr0n: QAction

    autosave: bool
    menuBar: QMenu
    saving: Saving
    
    def __init__(self):
        AbstractMyWindow.__init__(self)
        path: str = p.abspath(p.join(p.dirname(__file__), '.')) + '/main_window.ui'
        uic.loadUi(path, self)
        self._mainSemaphore = QSemaphore(1)
        self.saving = Saving(self._mainSemaphore)
        tree: Tree = self._tree
        properties: QTableView = self._properties
                
        self._treeModel = QStandardItemModel()
        self._propertiesModel = QStandardItemModel()
        properties.setModel(self._propertiesModel)
        self._propertiesUtil = PropertiesUtil(self,self._properties)
        
        self._treeManualItem = QStandardItem("Manual")
        self._treeManualItem.setFlags(self._treeManualItem.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable |
                          QtCore.Qt.ItemFlag.ItemIsEnabled)
        self._treeManualItem.setCheckState(QtCore.Qt.CheckState.Unchecked)
        self._treeModel.appendRow(self._treeManualItem)
        self._treeAIItem = QStandardItem("AI")
        self._treeAIItem.setFlags(self._treeAIItem.flags() |QtCore.Qt.ItemFlag.ItemIsUserCheckable |
                          QtCore.Qt.ItemFlag.ItemIsEnabled)
        self._treeAIItem.setCheckState(QtCore.Qt.CheckState.Unchecked)
        self._treeModel.appendRow(self._treeAIItem)
        tree.setModel(self._treeModel)
        self._models = {}
        self._actionUrl.triggered.connect(self.openMainUrl)
        self._actionSiliconpr0n.triggered.connect(self.openSiliconpr0nUrl)

        imageFile: str
        if(len(sys.argv) < 2):
            dlg = QFileDialog()
            filenames = dlg.getOpenFileName(caption="Load image",filter="Image (*.png;*.jpg;*.bmp;*.gif)",initialFilter="Image (*.png;*.jpg;*.bmp;*.gif)")
            if(len(filenames) >= 1):
                imageFile = filenames[0]
        else:
            imageFile = sys.argv[1]
        self._pixmap = QPixmap(imageFile)
        self.setWindowTitle(f"SiliconAnalyser - {imageFile}")
        
        computeBtn: ComputeBtn = self._computeBtn
        autoComputeBtn: ComputeBtn = self._autoComputeBtn
        addGridBtn: AddGridBtn = self._addGridBtn
        addLabelBtn: AddLabelBtn = self._addLabelBtn
        minimap: MiniMap = self._minimap
        image: FullImage = self._image

        tree.initialize(self)
        computeBtn.initialize(self)
        autoComputeBtn.initialize(self)
        addGridBtn.initialize(self)
        addLabelBtn.initialize(self)
        minimap.initialize(self, self._pixmap)
        image.initialize(self, self._pixmap)
        
        self.disableComputeButton()
        self.disableAutoComputeButton()
        self.disableAddLabelButton()
        tree.evtTreeSelectionChanged.connect(self.treeSelectionChanged)

        self._actionDecisionTree.triggered.connect(self.decisionTreeChecked)
        self._actionNeuralNetwork.triggered.connect(self.neuralNetworkChecked)
        
        self.getAutoComputeBtn().active.connect(self.autoComputeActive)
        self.getAutoComputeBtn().unactive.connect(self.autoComputeUnactive)
        
        self._posX = 0
        self._posY = 0
        
        self._scale = 1.0
        self.drawImgAndMinimap()
        
        self.autosave = False
        
        if p.isfile(silicon_analyser.savefiles.SAVE_RECTS):
            with open(silicon_analyser.savefiles.SAVE_RECTS,"r") as f:
                rects = self.saving.loadRects()
                for k in rects.keys():
                    tree.addTreeItem(k)
                image.loadRects(rects)
        if p.isfile(silicon_analyser.savefiles.SAVE_GRIDS):
            grids: dict[str, Grid] = self.saving.loadGrids()
            for gridKey in grids.keys():
                grid, parentTreeItem = tree.addTreeItem(gridKey,TreeItem.TYPE_GRID)
                for gridItemKey in grids[gridKey].getLabels():
                    _, treeItem = tree.addTreeItem(gridItemKey,TreeItem.TYPE_GRID_ITEM, grid, parentTreeItem)
                    text = treeItem.data(TreeItem.TEXT)
                    if(not grids[gridKey]._rectsActive[text]):
                        treeItem.uncheck()
                tree.expandAll()
            image.loadGrids(grids)
        
        image.drawImage()
        self.autosave = True
        if(torch.cuda.is_available()):
            self.setSuccessStatus("CUDA successfully initialized")
        else:
            self.setSuccessStatus("CUDA not found")
        
        menuBar: QMenu = self.menuBar    

        version = importlib.metadata.version("silicon-analyser")
        action = menuBar.addAction(f"Version: {version}")
        action.triggered.connect(self.openMainUrl)
        
        self.saving.onSaving.connect(lambda : self.setStatusText("Saving ..."))
    
    def getMainSemaphore(self) -> QSemaphore:
        return self._mainSemaphore
    
    def getSaving(self) -> Saving:
        return self.saving
    
    def autoComputeActive(self):
        self.disableComputeButton()
        self.disableAddLabelButton()
        self.disableAddGridButton()
        self._actionDecisionTree.setEnabled(False)
        self._actionNeuralNetwork.setEnabled(False)
        
    def autoComputeUnactive(self):
        self.enableComputeButton()
        self.enableAddLabelButton()
        self.enableAddGridButton()
        self._actionDecisionTree.setEnabled(True)
        self._actionNeuralNetwork.setEnabled(True)
    
    def getAutoComputeBtn(self) -> AutoComputeBtn:
        return self._autoComputeBtn

    def decisionTreeChecked(self):
        if(self._actionDecisionTree.isChecked()):
            self._actionNeuralNetwork.setChecked(False)
            self.getAutoComputeBtn().computationMethodChanged.emit()

    def neuralNetworkChecked(self):
        if(self._actionNeuralNetwork.isChecked()):
            self._actionDecisionTree.setChecked(False)
            self.getAutoComputeBtn().computationMethodChanged.emit()
        
    def treeSelectionChanged(self, selection: QItemSelection):
        tree: Tree = self._tree
        selectedType: str|None = tree.selectedType()
        if not self.getAutoComputeBtn().isChecked():
            if((selectedType == TreeItem.TYPE_GRID_ITEM)
            or (selectedType == TreeItem.TYPE_GRID)
            or (selectedType == TreeItem.TYPE_AI_GRID)
            or (selectedType == TreeItem.TYPE_AI_GRID_ITEM)
            ):
                self.enableComputeButton()
                self.enableAutoComputeButton()
                self.enableAddLabelButton()
            else:
                self.disableComputeButton()
                self.disableAutoComputeButton()
                self.disableAddLabelButton()

    def openMainUrl(self) -> None:
        import webbrowser
        webbrowser.open('https://github.com/TheCrazyT/SiliconAnalyser')
        
    def openSiliconpr0nUrl(self) -> None:
        import webbrowser
        webbrowser.open('https://siliconpr0n.org/')
        
    def getModel(self, name):
        if name in self._models:
            return self._models[name]
        return None
    
    def hasModel(self, name) -> bool:
        if name in self._models:
            return True
        return False
    
    def setLastModel(self, name, model_train):
        self._models[name] = model_train
    
    def getImage(self) -> AbstractImage:
        return self._image
    
    def getMinimap(self) -> MiniMap:
        return self._minimap

    def imageWidth(self):
        return self.getImage().width()

    def imageHeight(self):
        return self.getImage().height()

    def setSuccessStatus(self, text):
        statusBar: QStatusBar = self._statusBar
        statusBar.setStyleSheet('background-color: #0ff000')
        statusBar.showMessage(text)

    def setErrorStatus(self, text):
        statusBar: QStatusBar = self._statusBar
        statusBar.setStyleSheet('background-color: #ff0000')
        statusBar.showMessage(text)
            
    def setStatusText(self, text):
        statusBar: QStatusBar = self._statusBar
        statusBar.setStyleSheet('')
        logger.info(f"status: {text}")
        statusBar.showMessage(text)
        
    def getTree(self) -> AbstractTreeHelper:
        return self._tree
    
    def getManualItem(self) -> QStandardItem:
        return self._treeManualItem
    
    def getAIItem(self) -> QStandardItem:
        return self._treeAIItem
    
    def getScale(self):
        return self._scale
    
    def getPos(self):
        return self._posX, self._posY

    def getPosX(self):
        return self._posX
    
    def getPosY(self):
        return self._posY
    
    def setPosX(self, x):
        self._posX = x
        self._posX = max(self._posX,0)
        self._posX = min(self._posX,self.getImage().getImageWidth()-self.imageWidth()/self.getScale())
    
    def setPosY(self, y):
        self._posY = y
        self._posY = max(self._posY,0)
        self._posY = min(self._posY,self.getImage().getImageHeight()-self.imageHeight()/self.getScale())
    
    def drawImgAndMinimap(self):
        self.getImage().drawImage()
        self.getMinimap().drawMinimap()
    
    def reloadProperyWindowByGrid(self, grid):
        return self._propertiesUtil.reloadProperyWindowByGrid(grid)
    
    def reloadPropertyWindow(self, selection: QItemSelection):
        return self._propertiesUtil.reloadPropertyWindow(selection)
    
    def keyPressEvent(self, keyEvent: QtGui.QKeyEvent):
        c = 10
        if keyEvent.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            c = 100
        if keyEvent.key() == Qt.Key.Key_Left:
            self.setPosX(self.getPosX() - c)
        if keyEvent.key() == Qt.Key.Key_Right:
            self.setPosX(self.getPosX() + c)
        if keyEvent.key() == Qt.Key.Key_Up:
            self.setPosY(self.getPosY() - c)
        if keyEvent.key() == Qt.Key.Key_Down:
            self.setPosY(self.getPosY() + c)
        self.drawImgAndMinimap()
            
    def wheelEvent(self,event):
        if event.angleDelta().y() > 0:
            self._scale += 0.25
        else:
            self._scale -= 0.25
        self._scale = max(self._scale,0.25)
        logger.info(self._scale)
        self.drawImgAndMinimap()
        
    def disableComputeButton(self):
        computeBtn: ComputeBtn = self._computeBtn
        computeBtn.setEnabled(False)

    def disableAutoComputeButton(self):
        autoComputeBtn: AutoComputeBtn = self._autoComputeBtn
        autoComputeBtn.setEnabled(False)
    
    def disableAddLabelButton(self):
        addLabelBtn: AddLabelBtn = self._addLabelBtn
        addLabelBtn.setEnabled(False)
    
    def disableAddGridButton(self):
        addGridBtn: AddGridBtn = self._addGridBtn
        addGridBtn.setEnabled(False)
    
    def enableComputeButton(self):
        computeBtn: ComputeBtn = self._computeBtn
        computeBtn.setEnabled(True)
    
    def enableAutoComputeButton(self):
        autoComputeBtn: AutoComputeBtn = self._autoComputeBtn
        autoComputeBtn.setEnabled(True)
    
    def enableAddLabelButton(self):
        addLabelBtn: AddLabelBtn = self._addLabelBtn
        addLabelBtn.setEnabled(True)
    
    def enableAddGridButton(self):
        addGridBtn: AddGridBtn = self._addGridBtn
        addGridBtn.setEnabled(True)