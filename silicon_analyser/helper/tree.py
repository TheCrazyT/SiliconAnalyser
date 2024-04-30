import logging
logger = logging.getLogger(__name__)

from PIL import Image
import typing
import numpy as np
import re
from PyQt5.QtCore import QItemSelection, pyqtSignal, QItemSelectionModel
from PyQt5 import QtCore
from PyQt5.QtWidgets import QTreeView, QWidget, QAction, QFileDialog, QInputDialog
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from silicon_analyser.helper.abstract.abstractmywindow import AbstractMyWindow
from silicon_analyser.grid import Grid
from silicon_analyser.helper.abstract.abstracttreehelper import AbstractTreeHelper
from silicon_analyser.helper.abstract.abstractimage import AbstractImage
from silicon_analyser.treeitem import TreeItem
from silicon_analyser.grid import Grid
from silicon_analyser.dialogs.pixel_image import PixelImageDlg

class Tree(AbstractTreeHelper):
    _myWindow: AbstractMyWindow
    _actionGridAddXRowsBottom: QAction
    _actionGridAddXRowsTop: QAction
    _actionGridRemoveXRowsBottom: QAction
    _actionGridRemoveXRowsTop: QAction
    _actionGridAddXColumnsLeft: QAction
    _actionGridAddXColumnsRight: QAction
    _actionGridRemoveXColumnsLeft: QAction
    _actionGridRemoveXColumnsRight: QAction
    _actionSaveModel: QAction
    _actionLoadModel: QAction
    _actionRemoveGrid: QAction
    _actionRemoveLabel: QAction
    _actionSaveAsCsv: QAction
    _actionViewAsPixelimage: QAction
    _actionExportCellsToImages: QAction
    _pixelImageDlg: PixelImageDlg
    evtTreeSelectionChanged: pyqtSignal = pyqtSignal(QItemSelection)

    def __init__(self, parent: QWidget | None = ...) -> None: # type: ignore
        super().__init__(parent)
    
    def initialize(self, myWindow: AbstractMyWindow):
        self._myWindow = myWindow
        self.selectionModel().selectionChanged.connect(self.treeSelectionChanged)
        self._actionSaveModel = self._myWindow._actionSaveModel
        self._actionLoadModel = self._myWindow._actionLoadModel
        self._actionRemoveGrid = self._myWindow._actionRemoveGrid
        self._actionRemoveLabel = self._myWindow._actionRemoveLabel
        self._actionSaveAsCsv = self._myWindow._actionSaveAsCsv
        self._actionViewAsPixelimage = self._myWindow._actionViewAsPixelimage
        self._actionExportCellsToImages = self._myWindow._actionExportCellsToImages
        self._actionGridAddXRowsTop = self._myWindow._actionGridAddXRowsTop
        self._actionGridAddXRowsBottom = self._myWindow._actionGridAddXRowsBottom
        self._actionGridRemoveXRowsTop = self._myWindow._actionGridRemoveXRowsTop
        self._actionGridRemoveXRowsBottom = self._myWindow._actionGridRemoveXRowsBottom
        self._actionGridAddXColumnsLeft = self._myWindow._actionGridAddXColumnsLeft
        self._actionGridAddXColumnsRight = self._myWindow._actionGridAddXColumnsRight
        self._actionGridRemoveXColumnsLeft = self._myWindow._actionGridRemoveXColumnsLeft
        self._actionGridRemoveXColumnsRight = self._myWindow._actionGridRemoveXColumnsRight
        self.addAction(self._actionGridAddXRowsTop)
        self.addAction(self._actionGridAddXRowsBottom)
        self.addAction(self._actionGridRemoveXRowsTop)
        self.addAction(self._actionGridRemoveXRowsBottom)
        self.addAction(self._actionGridAddXColumnsLeft)
        self.addAction(self._actionGridAddXColumnsRight)
        self.addAction(self._actionGridRemoveXColumnsLeft)
        self.addAction(self._actionGridRemoveXColumnsRight)
        self.addAction(self._actionSaveModel)
        self.addAction(self._actionLoadModel)
        self.addAction(self._actionRemoveGrid)
        self.addAction(self._actionRemoveLabel)
        self.addAction(self._actionSaveAsCsv)
        self.addAction(self._actionViewAsPixelimage)
        self.addAction(self._actionExportCellsToImages)
        self._actionGridAddXRowsTop.triggered.connect(self.addTopRows)
        self._actionGridAddXRowsBottom.triggered.connect(self.addBottomRows)
        self._actionGridRemoveXRowsTop.triggered.connect(self.removeTopRows)
        self._actionGridRemoveXRowsBottom.triggered.connect(self.removeBottomRows)
        self._actionGridAddXColumnsLeft.triggered.connect(self.addLeftColumns)
        self._actionGridAddXColumnsRight.triggered.connect(self.addRightColumns)
        self._actionGridRemoveXColumnsLeft.triggered.connect(self.removeLeftColumns)
        self._actionGridRemoveXColumnsRight.triggered.connect(self.removeRightColumns)
        self._actionSaveModel.triggered.connect(self.saveModel)
        self._actionLoadModel.triggered.connect(self.loadModel)
        self._actionRemoveGrid.triggered.connect(self.removeGrid)
        self._actionRemoveLabel.triggered.connect(self.removeLabel)
        self._actionSaveAsCsv.triggered.connect(self.saveAsCsv)
        self._actionViewAsPixelimage.triggered.connect(self.viewAsPixelimage)
        self._actionExportCellsToImages.triggered.connect(self.exportCellsToImages)
        self._pixelImageDlg = PixelImageDlg()
    
    def exportCellsToImages(self, *args, **kwargs):
        logger.info("exportCellsToImages")
        grid: Grid|None = self.getSelectedGrid()
        if grid is None:
            return
        dlg: QFileDialog = QFileDialog()
        dlg.setLabelText(QFileDialog.DialogLabel.Accept, "Save")
        directoryPath: str = dlg.getExistingDirectory()
        if directoryPath is not None:
            for label in grid.getLabels():
                for rect in grid.getRects(label):
                  x, y = rect[0:2]
                  w = grid.width / grid.cols
                  h = grid.height / grid.rows
                  img: AbstractImage = self._myWindow.getImage()
                  arr = img.fetchData(grid.absX(x,y),grid.absY(y,x),int(grid.absX(x,y)+w),int(grid.absY(y,x)+h))
                  clean_label = re.sub("[^A-Za-z0-9]","_",label)
                  imgArr = np.zeros(arr.shape,np.uint8)
                  imgArr[:,:,0] = arr[:,:,2]
                  imgArr[:,:,1] = arr[:,:,1]
                  imgArr[:,:,2] = arr[:,:,0]
                  imgToSave = Image.fromarray(imgArr)
                  imgToSave.save(f"{directoryPath}/{clean_label}_{x:03}_{y:03}.png","PNG")
        logger.info("exportCellsToImages done")

    def viewAsPixelimage(self, *args, **kwargs):
        logger.info("viewAsPixelimage")
        grid: Grid|None
        selectedType = self.selectedType()
        if selectedType == TreeItem.TYPE_GRID_ITEM:
            grid = self.getSelectedGrid()
        elif selectedType == TreeItem.TYPE_AI_GRID_ITEM:
            grid = self.getSelectedAIGrid()
        if grid is None:
            return
        label = self.selectedLabel()
        if label is not None: 
            self._pixelImageDlg.show()
            self._pixelImageDlg.drawRects(grid.getRects(label))
    
    def saveAsCsv(self, *args, **kwargs):
        logger.info("saveAsCsv")
        dlg = QFileDialog()
        dlg.setLabelText(QFileDialog.DialogLabel.Accept, "Save")
        filenames = []
        filenames = dlg.getSaveFileName(caption="Save csv",filter="Comma separated values (*.csv)",initialFilter="Comma separated values (*.csv)")
        if(len(filenames) >= 1):
            grid:Grid|None
            if self.selectedType() == TreeItem.TYPE_GRID:
                grid = self.getSelectedGrid()
            if self.selectedType() == TreeItem.TYPE_AI_GRID:
                grid = self.getSelectedAIGrid()
            if grid is None:
                return
            with open(filenames[0],"w") as f:
                for r in range(0,grid.rows):
                    cells = []
                    for c in range(0,grid.cols):
                        labelFound = False
                        for l in grid.getLabels():
                            if grid.isRectSet(c,r,l):
                                labelFound = True
                                if l.isnumeric():
                                    cells.append(f'{l}')
                                else:
                                    cells.append(f'"{l}"')
                                break
                        if not labelFound:
                            cells.append(f'')
                    f.write(",".join(cells))
                    f.write("\n")
    
    def saveModel(self, *args, **kwargs):
        logger.info("saveModel")
        dlg = QFileDialog()
        dlg.setLabelText(QFileDialog.DialogLabel.Accept, "Save")
        filenames = []
        filenames = dlg.getSaveFileName(caption="Save trained model",filter="Trained model (*.h5)",initialFilter="Trained model (*.h5)")
        if(len(filenames) >= 1):
            import os
            os.environ["KERAS_BACKEND"] = "torch"
            from keras.models import Sequential
            grid = self.getSelectedGrid()
            if grid is not None:
                model: Sequential = self._myWindow.getModel(grid.name)
                model.save(filenames[0])
    
    
    def recreateAiTree(self, grid:Grid):
        self.clearAIItem(grid.name)
        aiGrid, aiTreeItem = self.addTreeItem(grid.name,TreeItem.TYPE_AI_GRID)
        for l in grid.getLabels():
            self.addTreeItem(l,TreeItem.TYPE_AI_GRID_ITEM,aiGrid,aiTreeItem)
        self.expandAll()
        return aiGrid
    
    def loadModel(self, *args, **kwargs):
        logger.info("loadModel")
        myWindow: AbstractMyWindow = self._myWindow
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setNameFilter("Trained model (*.h5)")
        filenames = []
        if dlg.exec_():
            filenames = dlg.selectedFiles()
        if(len(filenames) == 1):
            import os
            os.environ["KERAS_BACKEND"] = "torch"
            from keras.models import load_model
            from silicon_analyser.helper.ai import appendFoundCellRects
            grid: Grid|None = self.getSelectedGrid()
            if grid is not None:
                model = load_model(filenames[0])
                aiGrid = self.recreateAiTree(grid)
                myWindow.setLastModel(grid.name, model)
                img: AbstractImage = myWindow.getImage()
                appendFoundCellRects(img, grid, aiGrid, None, None, model) # type: ignore
                img.drawImage()
    
    def removeGrid(self, *args, **kwargs):
        logger.info("removeGrid")
        myWindow: AbstractMyWindow = self._myWindow
        grid: Grid|None = self.getSelectedGrid()
        if grid is None:
            return
        myWindow.getImage().removeGrid(grid.name)
        myWindow.getImage().drawImage()
        self.removeSelectedRow()

    def removeSelectedRow(self):
        index_list: list[QtCore.QModelIndex] = []                                                          
        for model_index in self.selectionModel().selectedRows():       
            index = QtCore.QPersistentModelIndex(model_index)         
            index_list.append(index)                                             

        for index in index_list:                                      
            self.model().removeRow(index.row(),index.parent())

    def removeLabel(self, *args, **kwargs):
        logger.info("removeLabel")
        myWindow: AbstractMyWindow = self._myWindow
        label = self.selectedLabel()
        if(self.selectedType() == TreeItem.TYPE_GRID_ITEM):
            grid: Grid|None = self.getSelectedGrid()
            if grid is None:
                return
            grid.removeRectGroup(label)
        elif(self.selectedType() == TreeItem.TYPE_MANUAL):
            myWindow.getImage().removeRectGroup(label)
        myWindow.getImage().drawImage()
        self.removeSelectedRow()

    def addLeftColumns(self, *args, **kwargs):
        logger.info("addLeftColumns")
        num,ok = QInputDialog.getInt(self,"How many columns to add?","enter a number",1)
        if ok:
            grid: Grid|None = self.getSelectedGrid()
            if grid is None:
                return
            for _ in range(0,num):
                grid.addLeftColumn()
            grid.recalcCell()
            myWindow: AbstractMyWindow = self._myWindow
            myWindow.getImage().drawImage()
            tree:Tree = self
            myWindow.reloadPropertyWindow(tree.selectionModel().selection())

    def addRightColumns(self, *args, **kwargs):
        logger.info("addRightColumns")
        num,ok = QInputDialog.getInt(self,"How many columns to add?","enter a number",1)
        if ok:
            grid: Grid|None = self.getSelectedGrid()
            if grid is None:
                return
            for _ in range(0,num):
                grid.addRightColumn()
            grid.recalcCell()
            myWindow: AbstractMyWindow = self._myWindow
            myWindow.getImage().drawImage()
            tree:Tree = self
            myWindow.reloadPropertyWindow(tree.selectionModel().selection())
                
    def removeLeftColumns(self, *args, **kwargs):
        logger.info("removeLeftColumns")
        num,ok = QInputDialog.getInt(self,"How many columns to remove?","enter a number",1)
        if ok:
            grid: Grid|None = self.getSelectedGrid()
            if grid is None:
                return
            for _ in range(0,num):
                grid.removeLeftColumn()
            grid.recalcCell()
            myWindow: AbstractMyWindow = self._myWindow
            myWindow.getImage().drawImage()
            tree:Tree = self
            myWindow.reloadPropertyWindow(tree.selectionModel().selection())

    def removeRightColumns(self, *args, **kwargs):
        logger.info("removeRightColumns")
        num,ok = QInputDialog.getInt(self,"How many columns to remove?","enter a number",1)
        if ok:
            grid: Grid|None = self.getSelectedGrid()
            if grid is None:
                return
            for _ in range(0,num):
                grid.removeRightColumn()
            grid.recalcCell()
            myWindow: AbstractMyWindow = self._myWindow
            myWindow.getImage().drawImage()
            tree:Tree = self
            myWindow.reloadPropertyWindow(tree.selectionModel().selection())

    def addTopRows(self, *args, **kwargs):
        logger.info("addTopRows")
        num,ok = QInputDialog.getInt(self,"How many rows to add?","enter a number",1)
        if ok:
            grid: Grid|None = self.getSelectedGrid()
            if grid is None:
                return
            for _ in range(0,num):
                grid.addTopRow()
            grid.recalcCell()
            myWindow: AbstractMyWindow = self._myWindow
            myWindow.getImage().drawImage()
            tree:Tree = self
            myWindow.reloadPropertyWindow(tree.selectionModel().selection())

    def addBottomRows(self, *args, **kwargs):
        logger.info("addBottomRows")
        num,ok = QInputDialog.getInt(self,"How many rows to add?","enter a number",1)
        if ok:
            grid: Grid|None = self.getSelectedGrid()
            if grid is None:
                return
            for _ in range(0,num):
                grid.addBottomRow()
            grid.recalcCell()
            myWindow: AbstractMyWindow = self._myWindow
            myWindow.getImage().drawImage()
            tree:Tree = self
            myWindow.reloadPropertyWindow(tree.selectionModel().selection())

    def removeTopRows(self, *args, **kwargs):
        logger.info("removeTopRows")
        num,ok = QInputDialog.getInt(self,"How many rows to remove?","enter a number",1)
        if ok:
            grid: Grid|None = self.getSelectedGrid()
            if grid is None:
                return
            for _ in range(0,num):
                grid.removeTopRow()
            grid.recalcCell()
            myWindow: AbstractMyWindow = self._myWindow
            myWindow.getImage().drawImage()
            tree:Tree = self
            myWindow.reloadPropertyWindow(tree.selectionModel().selection())

    def removeBottomRows(self, *args, **kwargs):
        logger.info("removeBottomRows")
        num,ok = QInputDialog.getInt(self,"How many rows to remove?","enter a number",1)
        if ok:
            grid: Grid|None = self.getSelectedGrid()
            if grid is None:
                return
            for _ in range(0,num):
                grid.removeBottomRow()
            grid.recalcCell()
            myWindow: AbstractMyWindow = self._myWindow
            myWindow.getImage().drawImage()
            tree:Tree = self
            myWindow.reloadPropertyWindow(tree.selectionModel().selection())
        
    def treeSelectionChanged(self, selection: QItemSelection):
        logger.info("treeSelectionChanged")
        myWindow: AbstractMyWindow = self._myWindow
        myWindow.reloadPropertyWindow(selection)
        tree = self
        selectedType = tree.selectedType()
        if((selectedType == TreeItem.TYPE_GRID_ITEM) or (selectedType == TreeItem.TYPE_GRID)):
            self._actionGridAddXRowsTop.setVisible(True)
            self._actionGridAddXRowsBottom.setVisible(True)
            self._actionGridAddXColumnsLeft.setVisible(True)
            self._actionGridAddXColumnsRight.setVisible(True)
            self._actionGridRemoveXRowsTop.setVisible(True)
            self._actionGridRemoveXRowsBottom.setVisible(True)
            self._actionGridRemoveXColumnsLeft.setVisible(True)
            self._actionGridRemoveXColumnsRight.setVisible(True)
            grid: Grid|None = self.getSelectedGrid()
            if grid is None:
                return
            if myWindow.hasModel(grid.name):
                self._actionSaveModel.setVisible(True)
            self._actionLoadModel.setVisible(True)
        else:
            self._actionGridAddXRowsTop.setVisible(False)
            self._actionGridAddXRowsBottom.setVisible(False)
            self._actionGridAddXColumnsLeft.setVisible(False)
            self._actionGridAddXColumnsRight.setVisible(False)
            self._actionGridRemoveXRowsTop.setVisible(False)
            self._actionGridRemoveXRowsBottom.setVisible(False)
            self._actionGridRemoveXColumnsLeft.setVisible(False)
            self._actionGridRemoveXColumnsRight.setVisible(False)
            self._actionSaveModel.setVisible(False)
            self._actionLoadModel.setVisible(False)
        if(selectedType == TreeItem.TYPE_GRID):
            self._actionRemoveGrid.setVisible(True)
            self._actionSaveAsCsv.setVisible(True)
            self._actionExportCellsToImages.setVisible(True)
        else:
            self._actionRemoveGrid.setVisible(False)
            self._actionSaveAsCsv.setVisible(False)
            self._actionExportCellsToImages.setVisible(False)
        if(selectedType == TreeItem.TYPE_AI_GRID):
            self._actionSaveAsCsv.setVisible(True)
        else:
            self._actionSaveAsCsv.setVisible(False)
        if(selectedType == TreeItem.TYPE_MANUAL):
            self._actionRemoveLabel.setVisible(True)
        else:
            self._actionRemoveLabel.setVisible(False)
        if(selectedType == TreeItem.TYPE_GRID_ITEM):
            self._actionRemoveLabel.setVisible(True)
        else:
            self._actionRemoveLabel.setVisible(False)
        if(selectedType == TreeItem.TYPE_AI_GRID_ITEM) or (selectedType == TreeItem.TYPE_GRID_ITEM):
            self._actionViewAsPixelimage.setVisible(True)
        else:
            self._actionViewAsPixelimage.setVisible(False)
        if(selectedType == TreeItem.TYPE_GRID_ITEM):
            myWindow.getImage().drawImage()
        if(selectedType == TreeItem.TYPE_AI_GRID_ITEM):
            myWindow.getImage().drawImage()
        self.evtTreeSelectionChanged.emit(selection)
            
    def addTreeItem(self, text, type="auto", parent_obj=None, parent_item=None) -> tuple[typing.Any | None, TreeItem]:
        obj: typing.Any = None
        myWindow: AbstractMyWindow = self._myWindow
        img = myWindow.getImage()
        tree: Tree = self
        if type == "auto":
            if tree.selectedType() == TreeItem.TYPE_GRID:
                type = TreeItem.TYPE_GRID_ITEM
            elif tree.selectedType() == TreeItem.TYPE_GRID_ITEM:
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
            treeItem: QStandardItem = myWindow.getManualItem()
        if type == TreeItem.TYPE_AI:
            treeItem: QStandardItem = myWindow.getAIItem()
        if type == TreeItem.TYPE_GRID:
            treeItem: QStandardItem = myWindow.getManualItem()
        if type == TreeItem.TYPE_AI_GRID:
            treeItem: QStandardItem = myWindow.getAIItem()
        if type == TreeItem.TYPE_GRID_ITEM:
            selectedItem = self.getSelectedItem()
            if selectedItem is not None:
                if selectedItem.data(TreeItem.TYPE) == TreeItem.TYPE_GRID:
                    treeItem: QStandardItem = selectedItem 
                else:
                    treeItem: QStandardItem = selectedItem.parent()
        if type == TreeItem.TYPE_AI_GRID_ITEM:
            selectedItem = self.getSelectedItem()
            if selectedItem is not None:
                treeItem: QStandardItem = selectedItem.parent()
        if parent_item is not None:
            treeItem: QStandardItem = parent_item
        tree: Tree = self
        treeItem.appendRow(item)
        item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable |
                        QtCore.Qt.ItemFlag.ItemIsEnabled |
                        QtCore.Qt.ItemFlag.ItemIsSelectable)
        item.setCheckState(QtCore.Qt.CheckState.Checked)
        if type in [TreeItem.TYPE_AI_GRID,TreeItem.TYPE_GRID,TreeItem.TYPE_MANUAL]:
            item.onChecked = self.itemChecked
        if type == TreeItem.TYPE_GRID_ITEM:
            item.onChecked = self.gridRectGroupChecked
        if type == TreeItem.TYPE_AI_GRID_ITEM:
            item.onChecked = self.aiGridRectGroupChecked
        if type == TreeItem.TYPE_AI:
            item.onChecked = self.aiItemChecked
        return obj, item
    
    def getSelectedItem(self) -> QStandardItem|None:
        tree: QTreeView = self
        selection = tree.selectedIndexes()
        cnt = len(selection)
        if(cnt == 0):
            return None
        sel = selection[0]
        model = typing.cast(QStandardItemModel, tree.model())
        return model.itemFromIndex(sel)
    
    def getSelectedGrid(self) -> Grid|None:
        myWindow: AbstractMyWindow = self._myWindow
        selectedItem = self.getSelectedItem()
        if selectedItem is None:
            return None
        type = selectedItem.data(TreeItem.TYPE)
        if type == TreeItem.TYPE_GRID_ITEM:
            return selectedItem.parent().data(TreeItem.OBJECT)
        if type == TreeItem.TYPE_AI_GRID_ITEM:
            gridName = selectedItem.parent().data(TreeItem.TEXT)
            manual: QStandardItem = myWindow.getManualItem()
            for r in range(0,manual.rowCount()):
                if manual.child(r).data(TreeItem.TEXT) == gridName:
                    return manual.child(r).data(TreeItem.OBJECT)
        if type == TreeItem.TYPE_AI_GRID:
            gridName = selectedItem.data(TreeItem.TEXT)
            manual: QStandardItem = myWindow.getManualItem()
            for r in range(0,manual.rowCount()):
                if manual.child(r).data(TreeItem.TEXT) == gridName:
                    return manual.child(r).data(TreeItem.OBJECT)
        return None if type != TreeItem.TYPE_GRID else selectedItem.data(TreeItem.OBJECT)

    def getSelectedAIGrid(self):
        myWindow: AbstractMyWindow = self._myWindow
        selectedItem = self.getSelectedItem()
        if selectedItem is None:
            return
        type = selectedItem.data(TreeItem.TYPE)
        if type == TreeItem.TYPE_AI_GRID_ITEM:
            return selectedItem.parent().data(TreeItem.OBJECT)
        if type == TreeItem.TYPE_GRID_ITEM:
            gridName = selectedItem.parent().data(TreeItem.TEXT)
            aiItem: QStandardItem = myWindow.getAIItem()
            for r in range(0,aiItem.rowCount()):
                if aiItem.child(r).data(TreeItem.TEXT) == gridName:
                    return aiItem.child(r).data(TreeItem.OBJECT)
        if type == TreeItem.TYPE_GRID:
            gridName = selectedItem.data(TreeItem.TEXT)
            aiItem: QStandardItem = myWindow.getAIItem()
            for r in range(0,aiItem.rowCount()):
                if aiItem.child(r).data(TreeItem.TEXT) == gridName:
                    return aiItem.child(r).data(TreeItem.OBJECT)
        return None if type != TreeItem.TYPE_AI_GRID else selectedItem.data(TreeItem.OBJECT)
    
    def isItemSelected(self, rectLabel, gridName, gridItemType) -> bool:
        selectedItem = self.getSelectedItem()
        if selectedItem is None:
            return False
        type = selectedItem.data(TreeItem.TYPE)
        if type != gridItemType:
            return False
        if selectedItem.parent().data(TreeItem.TEXT) != gridName:
            return False
        if selectedItem.data(TreeItem.TEXT) != rectLabel:
            return False
        return True
    
    def clearAIItem(self, name:str|None = None):
        myWindow: AbstractMyWindow = self._myWindow
        treeAIItem = myWindow.getAIItem()
        if treeAIItem.hasChildren():
            if name is None:
                treeAIItem.removeRows(0,treeAIItem.rowCount())
                treeAIItem.clearData()
                myWindow.getImage().clearAIRects()
            else:
                for i in range(0,treeAIItem.rowCount()):
                    child = treeAIItem.child(i)
                    if child.data(TreeItem.TEXT) == name:
                        child.removeRows(0,treeAIItem.rowCount())
                        child.clearData()
    
    def selectedType(self) -> str|None:
        sel = self.getSelectedItem()
        if sel is None:
            return None
        return sel.data(TreeItem.TYPE)
    
    def selectedLabel(self) -> str|None:
        sel = self.getSelectedItem()
        if sel is None:
            return None
        return sel.data(TreeItem.TEXT)
    
    def aiGridRectGroupChecked(self, treeItem: TreeItem, checked, text):
        myWindow: AbstractMyWindow = self._myWindow
        img = myWindow.getImage()
        grid = treeItem.parent().data(TreeItem.OBJECT)
        if checked:
            img.activateAIGridRectGroup(grid,text)
        else:
            img.deactivateAIGridRectGroup(grid,text)
        
    def gridRectGroupChecked(self, treeItem: TreeItem, checked, text):
        myWindow: AbstractMyWindow = self._myWindow
        img = myWindow.getImage()
        grid = treeItem.parent().data(TreeItem.OBJECT)
        if checked:
            img.activateGridRectGroup(grid,text)
        else:
            img.deactivateGridRectGroup(grid,text)
        img.drawImage()
        
    def aiItemChecked(self, treeItem: TreeItem, checked, text):
        myWindow: AbstractMyWindow = self._myWindow
        img = myWindow.getImage()
        if checked:
            img.activateAIRectGroup(text)
        else:
            img.deactivateAIRectGroup(text)
    
    def itemChecked(self, treeItem: TreeItem, checked, text):
        myWindow: AbstractMyWindow = self._myWindow
        img = myWindow.getImage()
        if checked:
            img.activateRectGroup(text)
        else:
            img.deactivateRectGroup(text)