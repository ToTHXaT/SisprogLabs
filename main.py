import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem

from one_pass_handler import setup_handlers
from ui.first import Ui_MainWindow


def load_from_files(mw: Ui_MainWindow):
    with open('source.txt', 'r') as file:
        mw.src.appendPlainText(file.read())

    with open('tko.txt', 'r') as file:

        tko_raw = file.read()
        tko_lines = (i for i in tko_raw.split('\n', 2) if i != '')

        for i, tko_line in enumerate(tko_lines):
            for j, tko_item in enumerate(tko_line.split()):
                mw.tko.setItem(i, j, QTableWidgetItem(tko_item))


def main():
    app = QtWidgets.QApplication(sys.argv)

    win = QtWidgets.QMainWindow()

    mw = Ui_MainWindow()
    mw.setupUi(win)

    load_from_files(mw)

    win.show()

    setup_handlers(mw)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


