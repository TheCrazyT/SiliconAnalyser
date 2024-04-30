from PyQt5.QtCore import pyqtBoundSignal
import numpy as np
from numpy import ndarray

from silicon_analyser.dialogs.compute_stats import ComputeStatsDlg
from silicon_analyser.helper.abstract.abstractcomputationmethod import AbstractComputationMethod

class NeuralNetwork(AbstractComputationMethod):

    def __init__(self, computeStatsDlg: ComputeStatsDlg|None, onUpdate: pyqtBoundSignal):
        self.last_accuracy: float = 0
        self.last_val_accuracy: float = 0
        self._computeStatsDlg = computeStatsDlg
        import os
        os.environ["KERAS_BACKEND"] = "torch"
        import keras
        self.keras = keras
        self.model_train = None
        self._onUpdate = onUpdate
    
    def setOnUpdate(self, onUpdate: pyqtBoundSignal):
        self._onUpdate = onUpdate
    
    def getLastValAccuracy(self) -> float:
        return self.last_val_accuracy
    
    def loadOrCreateModel(self, countGroups:int, maxW:int, maxH:int, MP:int):
        if self.model_train is None:
            self.createModels(countGroups, maxW, maxH, MP)
    
    def createModels(self, countGroups:int, maxW:int, maxH:int, MP:int):
        def createModelsSub(keras, countGroups, maxW, maxH, MP):
            if maxH//MP-5>1 and maxW//MP-5>1:
                conv2 = keras.layers.Conv2D(
                        countGroups*5,
                        name="conv2d_2",
                        kernel_size=(int(maxH//MP-5),int(maxW//MP-5)),
                        activation="softmax"
                )
                conv3 = keras.layers.Conv2D(
                        countGroups,
                        name="conv2d_3",
                        kernel_size=(1+5,1+5),
                        activation="softmax"
                )
            else:
                conv2 = None
                conv3 = keras.layers.Conv2D(
                        countGroups,
                        name="conv2d_3",
                        kernel_size=(int(maxH//MP),int(maxW//MP)),
                        activation="softmax"
                )
            
            conv_layers = [conv2,conv3]
            if conv2 is None:
                conv_layers = [conv3]

            model_train = keras.Sequential([
                keras.layers.Input((maxH,maxW,3)),
                keras.layers.BatchNormalization(),
                keras.layers.MaxPooling2D(MP),
                *conv_layers,
                keras.layers.Reshape((countGroups,))
            ])
            model_train.summary()
            return model_train
        self.model_train = createModelsSub(self.keras,countGroups, maxW, maxH, MP)
    
    def getLastModel(self):
        return self.model_train
    
    def getFinishText(self) -> str:
        return f"Accuracy: {self.last_accuracy} Val Accuracy: {self.last_val_accuracy}"
    
    def fit(self, xtraining, ytraining, xvalidation, yvalidation, epochs:int = 100000):
        if self.model_train is None:
            raise RuntimeError("model not initialized")
        import os
        os.environ["KERAS_BACKEND"] = "torch"
        import keras

        class MyProgressCallback(keras.callbacks.Callback):
            def __init__(self, onUpdate: pyqtBoundSignal):
                self._onUpdate = onUpdate
            
            def on_epoch_end(self, epoch, logs=None): 
                if logs is None:
                    return
                self._onUpdate.emit(logs, epoch)

        class MyPlottingCallback(keras.callbacks.Callback):
            def __init__(self, plotDlg: ComputeStatsDlg, onUpdate: pyqtBoundSignal):
                self._plotDlg = plotDlg
                self._onUpdate = onUpdate
            
            def on_epoch_end(self, epoch, logs=None): 
                if logs is None:
                    return
                self._onUpdate.emit(logs, epoch)
                if self._plotDlg.isStop():
                    self.model.stop_training = True # type: ignore
                
        class MyThresholdCallback(keras.callbacks.Callback):
            def __init__(self, threshold, patience):
                super(MyThresholdCallback, self).__init__()
                self.threshold = threshold
                self.patience = patience
                self.count = 0

            def on_epoch_end(self, epoch, logs=None): 
                if logs is None:
                    return
                val_acc = logs["val_accuracy"]
                if val_acc >= self.threshold:
                    if self.count > self.patience:
                        self.model.stop_training = True # type: ignore
                    else:
                        self.count += 1
                else:
                    self.count = 0
        if self._computeStatsDlg is not None:
            callbacks = [MyPlottingCallback(self._computeStatsDlg, self._onUpdate),MyThresholdCallback(0.99,200)]
        else:
            callbacks = [MyProgressCallback(self._onUpdate)]
        self.model_train.compile(optimizer=keras.optimizers.Adam(learning_rate=0.002),loss="binary_crossentropy",metrics=["accuracy"])
        history = self.model_train.fit(
                    x = xtraining,
                    y = xvalidation,
                    epochs = epochs,
                    verbose = 0,
                    validation_data=(ytraining,yvalidation),
                    shuffle = True,
                    batch_size = 512,
                    callbacks = callbacks
                )
        self.last_accuracy = history.history["accuracy"][-1]
        self.last_val_accuracy = history.history["val_accuracy"][-1]

    def build(self, input_shape):
        if self.model_train is not None:
            self.model_train.build(input_shape=input_shape)
    
    def predict(self, subdata) -> ndarray:
        if self.model_train is None:
            raise Exception("not initialized")
        r = self.model_train(np.array(subdata))
        r = r.cpu().detach().numpy()
        return r