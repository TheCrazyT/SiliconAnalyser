from numpy import ndarray
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from PyQt5.QtCore import pyqtBoundSignal

from silicon_analyser.dialogs.compute_stats import ComputeStatsDlg
from silicon_analyser.helper.abstract.abstractcomputationmethod import AbstractComputationMethod

class DecisionTree(AbstractComputationMethod):
    def __init__(self, computeStatsDlg: ComputeStatsDlg|None, onUpdate: pyqtBoundSignal):
        self.decisionTree = DecisionTreeClassifier(criterion = 'entropy')
        self._computeStatsDlg = computeStatsDlg
        self._onUpdate = onUpdate
        self.last_accuracy: float = 0.0
    
    def loadOrCreateModel(self, countGroups:int, maxW:int, maxH:int, MP:int):
        pass

    def createModels(self, countGroups:int, maxW:int, maxH:int, MP:int):
        pass
    
    def build(self, input_shape):
        pass
    
    def getLastValAccuracy(self) -> float:
        return self.last_accuracy
    
    def getLastModel(self):
        return None
    
    def setOnUpdate(self, onUpdate: pyqtBoundSignal):
        self._onUpdate = onUpdate

    
    def fit(self, xtraining, ytraining, xvalidation, yvalidation, epochs:int = 0):        
        xtraining2 = xtraining.reshape(xtraining.shape[0],xtraining.shape[1]*xtraining.shape[2]*xtraining.shape[3])
        ytraining2 = ytraining.reshape(ytraining.shape[0],ytraining.shape[1]*ytraining.shape[2]*ytraining.shape[3])
        self.decisionTree.fit(xtraining2, xvalidation)
        y2 = self.decisionTree.predict(ytraining2)
        print("after fit")
        accuracy = accuracy_score(y2, yvalidation)
        self._onUpdate.emit({"loss":1,"val_loss":1,"accuracy":accuracy,"val_accuracy":accuracy}, 0)
        self._onUpdate.emit({"loss":1,"val_loss":1,"accuracy":accuracy,"val_accuracy":accuracy}, 1)
        self.last_accuracy = accuracy # type: ignore
    
    def getFinishText(self) -> str:
        return "Decision tree finished with accuracy: %s" % self.last_accuracy
    
    def predict(self, subdata) -> ndarray:
        subdata = subdata.reshape(subdata.shape[0],subdata.shape[1]*subdata.shape[2]*subdata.shape[3])
        return self.decisionTree.predict(subdata)