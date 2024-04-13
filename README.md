# Installation

Install from source:

`pip install .`

Install from pip:

`pip install silicon-analyser`

# Information

Code will use your graphic card for acceleration.

Frameworks/Libraries used:
* [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
* [PyTorch](https://pytorch.org/)
* [Keras](https://keras.io/)
* [PyQtGraph](https://www.pyqtgraph.org/)

# Small example

* start
* select image
* add grid
* press mouse down on image and drag your rectangle for your grid
* adjust x,y,cols,rows,width,height manualy to fit
* add label (while grid is selected)
  * give it a random name
* with that label selected, select cells for that label (for example cells that mark a "1")
* select grid (for example "grid_0" again)
* add another label (while grid is selected)
  * give it a random name
* with that label selected, select cells for that label (for example cells that mark a "0")
* with enough "1" and "0" labels drawn, click the "Compute" button
  * ai will find images in the grid that have the same properties
  * click "stop" once the results are satisfied
    * maximum for "acc" and "val_acc" is 1.00, the closer you are to those values, the better are the results
    * results depend on many factors:
      * the amount of cells you selected
      * how good your grid matches the current image
      * the quality of your image
      * ...
    * "acc" stands for "accuracy", "val" for "validation"
* found ai-cells will be drawn green

![image](https://raw.githubusercontent.com/TheCrazyT/SiliconAnalyser/main/docs/small_tutorial.gif)

# TODO

* export of ai-cells as bit-image
* auto-compute to calculate in background while you are selecting new cells for your labels
* possibility to rotate grid
* maybe store your model on a public place? (for others to use)
