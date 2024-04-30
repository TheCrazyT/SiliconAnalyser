import abc
from numpy import ndarray
from PyQt5.QtCore import pyqtBoundSignal

class AbstractComputationMethod(abc.ABC):
    @abc.abstractmethod
    def loadOrCreateModel(self, countGroups:int, maxW:int, maxH:int, MP:int):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def fit(self, xtraining, ytraining, xvalidation, yvalidation, epochs:int = 100000):        
        raise NotImplementedError()
    
    @abc.abstractmethod
    def predict(self,x)-> ndarray:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def createModels(self, countGroups:int, maxW:int, maxH:int, MP:int):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def getLastModel(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def build(self, input_shape):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def getFinishText(self) -> str:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def getLastValAccuracy(self) -> float:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def setOnUpdate(self, onUpdate: pyqtBoundSignal):
        raise NotImplementedError()