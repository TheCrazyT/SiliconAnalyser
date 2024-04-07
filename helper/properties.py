from savefiles import saveGrids
from grid import Grid
from PyQt5.QtWidgets import QTableView
from PyQt5.QtCore import QItemSelection, QModelIndex, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from treeitem import TreeItem
from helper.abstract.abstractmywindow import AbstractMyWindow

class PropertiesUtil:
    def __init__(self, myWindow: AbstractMyWindow,properties: QTableView):
        self._properties = properties
        self._myWindow = myWindow
        properties.model().dataChanged.connect(self.dataChanged)
    
    def dataChanged(self,*args,**kwargs):
        print("dataChanged")
        valueCol: QModelIndex = args[0]
        if valueCol.column() != 1:
            return
        row = valueCol.row()
        model: QStandardItemModel = self._properties.model()
        nameCol = model.item(row,0)
        name = nameCol.data(Qt.DisplayRole)
        value = valueCol.data(Qt.DisplayRole)
        print(name)
        print(value)
        grid: Grid = self._myWindow.getTree().getSelectedGrid()
        if(name == "cols"):
            grid.cols = int(value)
        if(name == "rows"):
            grid.rows = int(value)
        if(name == "x"):
            grid.x = int(value)
        if(name == "y"):
            grid.y = int(value)
        if(name == "width"):
            grid.width = int(value)
        if(name == "height"):
            grid.height = int(value)
        self._myWindow.getImage().drawImage()
        saveGrids(self._myWindow.getImage().getGrids())
    
    def reloadPropertyWindow(self,selection: QItemSelection):
        table: QTableView = self._properties
        model = table.model()
        model.removeRows(0,model.rowCount())
        cnt = selection.count()
        if(cnt == 0):
            return
        sel = selection.takeFirst()
        if(len(sel.indexes())==0):
            return
        typeStr = sel.indexes()[0].data(TreeItem.TYPE)
        if(typeStr == TreeItem.TYPE_GRID):
            grid: Grid = sel.indexes()[0].data(TreeItem.OBJECT)
            self.reloadProperyWindowByGrid(grid)

    def reloadProperyWindowByGrid(self, grid):
        table: QTableView = self._properties
        model = table.model()
        rowPosition = model.rowCount()
        model.removeRows(0,model.rowCount())
        model.insertRow(rowPosition,[QStandardItem("name"),QStandardItem(grid.name)])
        if grid is not None:
            rowPosition = model.rowCount()
            model.insertRow(rowPosition,[QStandardItem("x"),QStandardItem(f"{grid.x}")])
            rowPosition = model.rowCount()
            model.insertRow(rowPosition,[QStandardItem("y"),QStandardItem(f"{grid.y}")])
            rowPosition = model.rowCount()
            model.insertRow(rowPosition,[QStandardItem("cols"),QStandardItem(f"{grid.cols}")])
            rowPosition = model.rowCount()
            model.insertRow(rowPosition,[QStandardItem("rows"),QStandardItem(f"{grid.rows}")])
            rowPosition = model.rowCount()
            model.insertRow(rowPosition,[QStandardItem("width"),QStandardItem(f"{grid.width}")])
            rowPosition = model.rowCount()
            model.insertRow(rowPosition,[QStandardItem("height"),QStandardItem(f"{grid.height}")])

  