from PyQt5.QtWidgets import QApplication
import sys
from silicon_analyser.mywindow import MyWindow

def main_cli():
    app = QApplication(sys.argv)

    window = MyWindow()

    window.show()
    app.exec()

if __name__ == "__main__":
    main_cli()