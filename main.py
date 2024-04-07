from PyQt5.QtWidgets import QApplication
import sys
from mywindow import MyWindow

app = QApplication(sys.argv)

window = MyWindow()

window.show()
app.exec()