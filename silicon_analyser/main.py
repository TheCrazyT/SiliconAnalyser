import logging
from PyQt5.QtWidgets import QApplication
import sys
from silicon_analyser.mywindow import MyWindow

def main_cli():
    logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',level=logging.INFO)
    app = QApplication(sys.argv)

    window = MyWindow()

    window.show()
    app.exec()

if __name__ == "__main__":
    main_cli()