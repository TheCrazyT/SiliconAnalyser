from PyQt5 import QtCore, uic
from PyQt5.QtCore import Qt, QItemSelection
from PyQt5.QtWidgets import QFileDialog, QTableView, QStatusBar, QAction, QPushButton
from PyQt5.QtGui import QPixmap, QStandardItem, QStandardItemModel
from os import path as p
import sys

import silicon_analyser.savefiles
from silicon_analyser.savefiles import loadGrids, loadRects
from silicon_analyser.helper.abstract.abstracttreehelper import AbstractTreeHelper
from silicon_analyser.helper.abstract.abstractimage import AbstractImage
from silicon_analyser.helper.abstract.abstractmywindow import AbstractMyWindow
from silicon_analyser.helper.minimap import MiniMap
from silicon_analyser.helper.fullimage import FullImage
from silicon_analyser.helper.addlabelbtn import AddLabelBtn
from silicon_analyser.helper.computebtn import ComputeBtn
from silicon_analyser.helper.addgridbtn import AddGridBtn
from silicon_analyser.treeitem import TreeItem
from silicon_analyser.helper.properties import PropertiesUtil
from silicon_analyser.grid import Grid
from silicon_analyser.treeitem import TreeItem
from silicon_analyser.helper.tree import Tree

class MyWindow(AbstractMyWindow):
    _tree: Tree
    _properties: QTableView
    _addLabelBtn: AddLabelBtn
    _computeBtn: ComputeBtn
    _addGridBtn: AddGridBtn
    _statusBar: QStatusBar
    _minimap: MiniMap
    _image: FullImage
    _models: dict
    _actionGridAddRowTop: QAction
    _actionSaveModel: QAction
    _actionLoadModel: QAction
    _actionRemoveGrid: QAction
    _actionRemoveLabel: QAction
    _actionMade_by_TheCrazyT: QAction
    _actionUrl: QAction
    _actionSaveAsCsv: QAction
    autosave: bool
    
    def __init__(self):
        AbstractMyWindow.__init__(self)
        uic.loadUi(p.abspath(p.join(p.dirname(__file__), '.')) + '/main_window.ui', self)
        tree: Tree = self._tree
        properties: QTableView = self._properties
                
        self._treeModel = QStandardItemModel()
        self._propertiesModel = QStandardItemModel()
        properties.setModel(self._propertiesModel)
        self._propertiesUtil = PropertiesUtil(self,self._properties)
        
        self._treeManualItem = QStandardItem("Manual")
        self._treeManualItem.setFlags(QtCore.Qt.ItemIsUserCheckable |
                          QtCore.Qt.ItemIsEnabled)
        self._treeManualItem.setCheckState(QtCore.Qt.Unchecked)
        self._treeModel.appendRow(self._treeManualItem)
        self._treeAIItem = QStandardItem("AI")
        self._treeAIItem.setFlags(QtCore.Qt.ItemIsUserCheckable |
                          QtCore.Qt.ItemIsEnabled)
        self._treeAIItem.setCheckState(QtCore.Qt.Unchecked)
        self._treeModel.appendRow(self._treeAIItem)
        tree.setModel(self._treeModel)
        self._models = {}
        self._actionUrl.triggered.connect(self.openMainUrl)

        if(len(sys.argv) < 2):
            dlg = QFileDialog()
            filenames = dlg.getOpenFileName(caption="Load image",filter="Image (*.png;*.jpg;*.bmp;*.gif)",initialFilter="Trained model (*.h5)")
            if(len(filenames) >= 1):
                self._pixmap = QPixmap(filenames[0])
        else:
            self._pixmap = QPixmap(sys.argv[1])
        
        computeBtn: ComputeBtn = self._computeBtn
        addGridBtn: AddGridBtn = self._addGridBtn
        addLabelBtn: AddLabelBtn = self._addLabelBtn
        minimap: MiniMap = self._minimap
        image: FullImage = self._image

        tree.initialize(self)
        computeBtn.initialize(self)
        addGridBtn.initialize(self)
        addLabelBtn.initialize(self)
        minimap.initialize(self, self._pixmap)
        image.initialize(self, self._pixmap)
        
        computeBtn.setDisabled(True)
        addLabelBtn.setDisabled(True)
        tree.evtTreeSelectionChanged.connect(self.treeSelectionChanged)
        
        self._posX = 0
        self._posY = 0
        
        self._scale = 1.0
        self.drawImgAndMinimap()
        
        self.autosave = False
        
        if p.isfile(silicon_analyser.savefiles.SAVE_RECTS):
            with open(silicon_analyser.savefiles.SAVE_RECTS,"r") as f:
                rects = loadRects()
                for k in rects.keys():
                    self.getTree().addTreeItem(k)
                image.loadRects(rects)
        if p.isfile(silicon_analyser.savefiles.SAVE_GRIDS):
            grids: dict[Grid] = loadGrids()
            for gridKey in grids.keys():
                grid, parentTreeItem = self.getTree().addTreeItem(gridKey,TreeItem.TYPE_GRID)
                for gridItemKey in grids[gridKey].getLabels():
                    _, treeItem = self.getTree().addTreeItem(gridItemKey,TreeItem.TYPE_GRID_ITEM, grid, parentTreeItem)
                    text = treeItem.data(TreeItem.TEXT)
                    if(not grids[gridKey]._rectsActive[text]):
                        treeItem.setCheckState(QtCore.Qt.Unchecked)
            image.loadGrids(grids)
        
        image.drawImage()
        self.autosave = True
        
    def treeSelectionChanged(self, selection: QItemSelection):
        tree: Tree = self._tree
        selectedType: str = tree.selectedType()
        computeBtn: ComputeBtn = self._computeBtn
        addLabelBtn: AddLabelBtn = self._addLabelBtn
        if((selectedType == TreeItem.TYPE_GRID_ITEM)
           or (selectedType == TreeItem.TYPE_GRID)
           or (selectedType == TreeItem.TYPE_AI_GRID)
           or (selectedType == TreeItem.TYPE_AI_GRID_ITEM)
           ):
            computeBtn.setDisabled(False)
            addLabelBtn.setDisabled(False)
        else:
            computeBtn.setDisabled(True)
            addLabelBtn.setDisabled(True)

    def openMainUrl(self):
        import webbrowser
        return webbrowser.open('https://github.com/TheCrazyT/SiliconAnalyser')
        
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
            
    def setStatusText(self, text):
        self._statusBar.showMessage(text)
        
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
    
    def setPosY(self, y):
        self._posY = y
    
    def drawImgAndMinimap(self):
        self.getImage().drawImage()
        self.getMinimap().drawMinimap()
    
    def reloadProperyWindowByGrid(self, grid):
        return self._propertiesUtil.reloadProperyWindowByGrid(grid)
    
    def reloadPropertyWindow(self, selection: QItemSelection):
        return self._propertiesUtil.reloadPropertyWindow(selection)
    
    def keyPressEvent(self, event):
        c = 10
        if event.modifiers() & Qt.ShiftModifier:
            c = 100
        if event.key() == Qt.Key_Left:
            self._posX -= c
            self._posX = max(self._posX,0)
        if event.key() == Qt.Key_Right:
            self._posX += c
            self._posX = min(self._posX,self._pixmap.width())
        if event.key() == Qt.Key_Up:
            self._posY -= c
            self._posY = max(self._posY,0)
        if event.key() == Qt.Key_Down:
            self._posY += c
            self._posY = min(self._posY,self._pixmap.height())
        self.drawImgAndMinimap()
            
    def wheelEvent(self,event):
        #print(event.angleDelta())
        if event.angleDelta().y() > 0:
            self._scale += 0.25
        else:
            self._scale -= 0.25
        self._scale = max(self._scale,0.25)
        print(self._scale)
        self.drawImgAndMinimap()