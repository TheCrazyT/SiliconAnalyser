# Installation

Install from source:

`pip install .`

Install from pip:

`pip install silicon-analyser`

# Information

Code will use your graphic card for acceleration.
(but only if correct pytorch is installed, see "Additional info" below)

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

# Additional info

* you might need to install cuda-specific [PyTorch](https://pytorch.org/get-started/previous-versions/#linux-and-windows-4) for accelerated computing
    * check your graphic driver version for compatible cuda version!

# Keys

* Use up/down/left/right to navigate
* Hold shift to move faster
* Scroll-wheel to zoom out
* Click on minimap to get directly to a position
* Right click on tree-items (left navigation menu) for additional options

![image](https://raw.githubusercontent.com/TheCrazyT/SiliconAnalyser/main/docs/small_tutorial.gif)

# TODO

* show loading screen on start (pytorch with cuda support takes a bit to load)
* auto-compute to calculate in background while you are selecting new cells for your labels
* ai-model configuration
* possibility to rotate grid
* maybe store your model on a public place? (for others to use)
