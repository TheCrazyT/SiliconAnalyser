import typing
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton
from pyqtgraph import PlotWidget
from numpy import linspace
import os.path as p

class ComputeStatsDlg(QDialog):
    _lossgraph: PlotWidget
    _accuracygraph: PlotWidget
    _loss: typing.Any
    _val_loss: typing.Any
    _accuracy: typing.Any
    _val_accuracy: typing.Any
    _lblStatus: QLabel
    _btnStop: QPushButton
    request_graph_update = pyqtSignal([dict,int])
    
    def __init__(self):
        super().__init__()
        uic.loadUi(p.abspath(p.join(p.dirname(__file__), '.')) + '/compute_stats.ui', self)
        self._loss = linspace(0,0,self.width())
        self._val_loss = linspace(0,0,self.width())
        self._accuracy = linspace(0,0,self.width())
        self._val_accuracy = linspace(0,0,self.width())
        
        legend = self._lossgraph.addLegend()
        self._loss_curve = self._lossgraph.plot(pen='r')
        self._val_loss_curve = self._lossgraph.plot(pen='g')
        legend.addItem(self._loss_curve,'loss')
        legend.addItem(self._val_loss_curve ,'val_loss')
        
        legend = self._accuracygraph.addLegend()
        self._accuracy_curve = self._accuracygraph.plot(pen='r')
        self._val_accuracy_curve = self._accuracygraph.plot(pen='g')
        legend.addItem(self._accuracy_curve,'accuracy')
        legend.addItem(self._val_accuracy_curve,'val_accuracy')
        
        self._btnStop.clicked.connect(self.stop)
        self.request_graph_update.connect(self.updateGraph)
        
        self._lastX = 0
        self._stop = False
    
    def isStop(self):
        return self._stop

    def stop(self):
        self._stop = True
    
    def reset(self):
        self._stop = False
    
    def updateGraph(self,logs,epoch):
        self._lastX += 1

        self._loss[:-1] = self._loss[1:]
        self._val_loss[:-1] = self._val_loss[1:]
        self._accuracy[:-1] = self._accuracy[1:]
        self._val_accuracy[:-1] = self._val_accuracy[1:]

        loss, val_loss, accuracy, val_accuracy = logs["loss"], logs["val_loss"], logs["accuracy"], logs["val_accuracy"]

        self._loss[-1] = loss
        self._val_loss[-1] = val_loss
        self._accuracy[-1] = accuracy
        self._val_accuracy[-1] = val_accuracy
        
        self._loss_curve.setData(self._loss)
        self._loss_curve.setPos(self._lastX,0)
        self._val_loss_curve.setData(self._val_loss)
        self._val_loss_curve.setPos(self._lastX,0)

        self._accuracy_curve.setData(self._accuracy)
        self._accuracy_curve.setPos(self._lastX,0)
        self._val_accuracy_curve.setData(self._val_accuracy)
        self._val_accuracy_curve.setPos(self._lastX,0)
        
        self._lblStatus.setText(f"Status: epoch: {epoch: <10} loss: {loss:.6f} val_loss: {val_loss:.6f} acc: {accuracy:.2f} val_acc: {val_accuracy:.2f}")

        QtGui.QGuiApplication.processEvents()
    
    def setError(self,error: Exception):
        self._lblStatus.setStyleSheet("QLabel { background-color : red; color : black; }")
        self._lblStatus.setText(str(error))
        QtGui.QGuiApplication.processEvents()
    
    def setStatus(self,text: str):
        self._lblStatus.setStyleSheet("QLabel { color : black; }")
        self._lblStatus.setText(text)
        QtGui.QGuiApplication.processEvents()