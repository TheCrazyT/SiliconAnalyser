from helper.abstract.abstractmywindow import AbstractMyWindow
from grid import Grid
from helper.abstract.abstracttreehelper import AbstractTreeHelper
from treeitem import TreeItem
from PyQt5.QtCore import QItemSelection
from PyQt5 import QtCore
from PyQt5.QtWidgets import QTreeView, QWidget, QAction, QFileDialog
from PyQt5.QtGui import QStandardItem
from grid import Grid

class Tree(AbstractTreeHelper):
    _myWindow: AbstractMyWindow

    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)
    
    def initialize(self, myWindow: AbstractMyWindow):
        self._myWindow = myWindow
        self.selectionModel().selectionChanged.connect(self.treeSelectionChanged)
        self._actionGridAddRowTop: QAction = self._myWindow._actionGridAddRowTop
        self._actionSaveModel: QAction = self._myWindow._actionSaveModel
        self._actionLoadModel: QAction = self._myWindow._actionLoadModel
        self.addAction(self._actionGridAddRowTop)
        self.addAction(self._actionSaveModel)
        self.addAction(self._actionLoadModel)
        self._actionGridAddRowTop.triggered.connect(self.addTopRow)
        self._actionSaveModel.triggered.connect(self.saveModel)
        self._actionLoadModel.triggered.connect(self.loadModel)
    
    def saveModel(self, *args, **kwargs):
        print("saveModel")
        dlg = QFileDialog()
        dlg.setLabelText(QFileDialog.DialogLabel.Accept, "Save")
        filenames = []
        filenames = dlg.getSaveFileName(caption="Save trained model",filter="Trained model (*.h5)",initialFilter="Trained model (*.h5)")
        if(len(filenames) >= 1):
            from keras.models import Sequential
            grid = self.getSelectedGrid()
            model: Sequential = self._myWindow.getModel(grid.name)
            model.save(filenames[0])
    
    def loadModel(self, *args, **kwargs):
        print("loadModel")
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setNameFilter("Trained model (*.h5)")
        filenames = []
        if dlg.exec_():
            filenames = dlg.selectedFiles()
        if(len(filenames) == 1):
            from keras.models import load_model
            self._myWindow.setLastModel(load_model(filenames[0]))
    
    def addTopRow(self, *args, **kwargs):
        print("addTopRow")
        grid: Grid = self.getSelectedGrid()
        grid.addTopRow()
        
    def treeSelectionChanged(self, selection: QItemSelection):
        print("treeSelectionChanged")
        self._myWindow.reloadPropertyWindow(selection)
        tree = self._myWindow.getTree()
        selectedType = tree.selectedType()
        if((selectedType == TreeItem.TYPE_GRID_ITEM) or (selectedType == TreeItem.TYPE_GRID)):
            self._actionGridAddRowTop.setVisible(True)
            grid: Grid = self.getSelectedGrid()
            if self._myWindow.hasModel(grid.name):
                self._actionSaveModel.setVisible(True)
            self._actionLoadModel.setVisible(True)
        else:
            self._actionGridAddRowTop.setVisible(False)
            self._actionSaveModel.setVisible(False)
            self._actionLoadModel.setVisible(False)
        if(selectedType == TreeItem.TYPE_GRID_ITEM):
            self._myWindow.getImage().drawImage()
        if(selectedType == TreeItem.TYPE_AI_GRID_ITEM):
            self._myWindow.getImage().drawImage()
            
    def addTreeItem(self, text, type="auto", parent_obj=None, parent_item=None) -> tuple[Grid, TreeItem]:
        obj = None
        img = self._myWindow.getImage()
        tree = self._myWindow.getTree()
        if type == "auto":
            if tree.selectedType() == TreeItem.TYPE_GRID:
                type = TreeItem.TYPE_GRID_ITEM
            else:
                type = TreeItem.TYPE_MANUAL
        if type == TreeItem.TYPE_AI_GRID:
            obj = img.appendAIGrid(text)
            img.activateAIGrid(text)
        if type == TreeItem.TYPE_GRID:
            obj = img.appendGrid(text)
            img.activateGrid(text)
        if type == TreeItem.TYPE_AI_GRID_ITEM:
            grid = parent_obj
            if grid is None:
                grid = self.getSelectedAIGrid()
            obj = img.appendAIGridRectGroup(grid,text)
            img.activateAIGridRectGroup(grid,text)
        if type == TreeItem.TYPE_GRID_ITEM:
            grid = parent_obj
            if grid is None:
                grid = self.getSelectedGrid()
            obj = img.appendGridRectGroup(grid,text)
            img.activateGridRectGroup(grid,text)
        if type == TreeItem.TYPE_MANUAL:
            img.appendRectGroup(text)
            img.activateRectGroup(text)
        if type == TreeItem.TYPE_AI:
            img.appendAIRectGroup(text)
            img.activateAIRectGroup(text)
        item: TreeItem = TreeItem(text, type, obj)
        if type == TreeItem.TYPE_MANUAL:
            treeItem: QStandardItem = self._myWindow.getManualItem()
        if type == TreeItem.TYPE_AI:
            treeItem: QStandardItem = self._myWindow.getAIItem()
        if type == TreeItem.TYPE_GRID:
            treeItem: QStandardItem = self._myWindow.getManualItem()
        if type == TreeItem.TYPE_AI_GRID:
            treeItem: QStandardItem = self._myWindow.getAIItem()
        if type == TreeItem.TYPE_GRID_ITEM:
            treeItem: QStandardItem = self.getSelectedGrid()
        if type == TreeItem.TYPE_AI_GRID_ITEM:
            treeItem: QStandardItem = self.getSelectedAIGrid()
        if parent_item is not None:
            treeItem: QStandardItem = parent_item
        tree: QTreeView = self
        treeItem.appendRow(item)
        tree.expandAll()
        selModel = tree.selectionModel()
        tree.clearSelection()
        selModel.select(tree.model().indexFromItem(item), selModel.Select)
        item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                        QtCore.Qt.ItemIsEnabled |
                        QtCore.Qt.ItemIsSelectable)
        item.setCheckState(QtCore.Qt.Checked)
        if type in [TreeItem.TYPE_AI_GRID,TreeItem.TYPE_GRID,TreeItem.TYPE_MANUAL]:
            item.onChecked = self.itemChecked
        if type == TreeItem.TYPE_GRID_ITEM:
            item.onChecked = self.gridRectGroupChecked
        if type == TreeItem.TYPE_AI_GRID_ITEM:
            item.onChecked = self.aiGridRectGroupChecked
        if type == TreeItem.TYPE_AI:
            item.onChecked = self.aiItemChecked
        return obj, item
    
    def getSelectedItem(self) -> QStandardItem:
        tree: QTreeView = self
        selection = tree.selectedIndexes()
        cnt = len(selection)
        if(cnt == 0):
            return
        sel = selection[0]
        return tree.model().itemFromIndex(sel)
    
    def getSelectedGrid(self):
        type = self.getSelectedItem().data(TreeItem.TYPE)
        if type == TreeItem.TYPE_GRID_ITEM:
            return self.getSelectedItem().parent().data(TreeItem.OBJECT)
        if type == TreeItem.TYPE_AI_GRID_ITEM:
            gridName = self.getSelectedItem().parent().data(TreeItem.TEXT)
            manual: QStandardItem = self._myWindow.getManualItem()
            for r in range(0,manual.rowCount()):
                if manual.child(r).data(TreeItem.TEXT) == gridName:
                    return manual.child(r).data(TreeItem.OBJECT)
        if type == TreeItem.TYPE_AI_GRID:
            gridName = self.getSelectedItem().data(TreeItem.TEXT)
            manual: QStandardItem = self._myWindow.getManualItem()
            for r in range(0,manual.rowCount()):
                if manual.child(r).data(TreeItem.TEXT) == gridName:
                    return manual.child(r).data(TreeItem.OBJECT)
        return None if type != TreeItem.TYPE_GRID else self.getSelectedItem().data(TreeItem.OBJECT)

    def getSelectedAIGrid(self):
        type = self.getSelectedItem().data(TreeItem.TYPE)
        return None if type != TreeItem.TYPE_AI_GRID else self.getSelectedItem().data(TreeItem.OBJECT)
    
    def isItemSelected(self, rectLabel, gridName, gridItemType) -> bool:
        type = self.getSelectedItem().data(TreeItem.TYPE)
        if type != gridItemType:
            return False
        if self.getSelectedItem().parent().data(TreeItem.TEXT) != gridName:
            return False
        if self.getSelectedItem().data(TreeItem.TEXT) != rectLabel:
            return False
        return True
    
    def clearAIItem(self):
        treeAIItem = self._myWindow.getAIItem()
        if treeAIItem.hasChildren():
            treeAIItem.removeRows(0,treeAIItem.rowCount())
        treeAIItem.clearData()
        self._myWindow.getImage().clearAIRects()
    
    def selectedType(self) -> str:
        sel = self.getSelectedItem()
        if sel is None:
            return None
        return sel.data(TreeItem.TYPE)
    
    def selectedLabel(self) -> str:
        sel = self.getSelectedItem()
        if sel is None:
            return None
        return sel.data(TreeItem.TEXT)
    
    def aiGridRectGroupChecked(self, treeItem: TreeItem, checked, text):
        img = self._myWindow.getImage()
        grid = treeItem.parent().data(TreeItem.OBJECT)
        if checked:
            img.activateAIGridRectGroup(grid,text)
        else:
            img.deactivateAIGridRectGroup(grid,text)
        img.drawImage()
        
    def gridRectGroupChecked(self, treeItem: TreeItem, checked, text):
        img = self._myWindow.getImage()
        grid = treeItem.parent().data(TreeItem.OBJECT)
        if checked:
            img.activateGridRectGroup(grid,text)
        else:
            img.deactivateGridRectGroup(grid,text)
        img.drawImage()
        
    def aiItemChecked(self, treeItem: TreeItem, checked, text):
        img = self._myWindow.getImage()
        if checked:
            img.activateAIRectGroup(text)
        else:
            img.deactivateAIRectGroup(text)
    
    def itemChecked(self, treeItem: TreeItem, checked, text):
        img = self._myWindow.getImage()
        if checked:
            img.activateRectGroup(text)
        else:
            img.deactivateRectGroup(text)