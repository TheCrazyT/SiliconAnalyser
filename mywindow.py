import json
import savefiles
from savefiles import loadGrids, loadRects
from PyQt5 import QtCore, uic
from PyQt5.QtCore import Qt, QItemSelection
from PyQt5.QtWidgets import QTreeView, QTableView, QStatusBar
from PyQt5.QtGui import QPixmap, QStandardItem, QStandardItemModel
from helper.abstract.abstracttreehelper import AbstractTreeHelper
from helper.abstract.abstractimage import AbstractImage
from helper.abstract.abstractmywindow import AbstractMyWindow
from helper.minimap import MiniMap
from helper.fullimage import FullImage
from helper.addlabelbtn import AddLabelBtn
from helper.computebtn import ComputeBtn
from helper.addgridbtn import AddGridBtn
from treeitem import TreeItem
from os import path
from helper.properties import PropertiesUtil
from grid import Grid
from treeitem import TreeItem
from helper.tree import Tree
import sys


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
    autosave: bool
    
    def __init__(self):
        AbstractMyWindow.__init__(self)
        uic.loadUi('main_window.ui', self)
        self._treeModel = QStandardItemModel()
        self._propertiesModel = QStandardItemModel()
        self._properties.setModel(self._propertiesModel)
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
        self._tree.setModel(self._treeModel)
        self._models = {}

        self._pixmap = QPixmap(sys.argv[1])
        
        self._tree.initialize(self)
        self._computeBtn.initialize(self)
        self._addGridBtn.initialize(self)
        self._addLabelBtn.initialize(self)
        self._minimap.initialize(self, self._pixmap)
        self._image.initialize(self, self._pixmap)
        
        self._posX = 0
        self._posY = 0
        
        self._scale = 1.0
        self.drawImgAndMinimap()
        
        self.autosave = False
        
        if path.isfile(savefiles.SAVE_RECTS):
            with open(savefiles.SAVE_RECTS,"r") as f:
                rects = loadRects()
                for k in rects.keys():
                    self.getTree().addTreeItem(k)
                self._image.loadRects(rects)
        if path.isfile(savefiles.SAVE_GRIDS):
            grids: list[Grid] = loadGrids()
            for gridKey in grids.keys():
                grid, parentTreeItem = self.getTree().addTreeItem(gridKey,TreeItem.TYPE_GRID)
                for gridItemKey in grids[gridKey].getLabels():
                    _, treeItem = self.getTree().addTreeItem(gridItemKey,TreeItem.TYPE_GRID_ITEM, grid, parentTreeItem)
                    text = treeItem.data(TreeItem.TEXT)
                    if(not grids[gridKey]._rectsActive[text]):
                        treeItem.setCheckState(QtCore.Qt.Unchecked)
            self._image.loadGrids(grids)
        
        self._image.drawImage()
        self.autosave = True
        
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

    def imageWidth(self):
        return self._image.width()

    def imageHeight(self):
        return self._image.height()
            
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
        self._image.drawImage()
        self._minimap.drawMinimap()
    
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