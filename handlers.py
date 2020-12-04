from PyQt5.QtWidgets import QTableWidgetItem

from FirstPass import do_first_pass, FPR
from SecondPass import do_second_pass
from tko import TKO
from ui.first import Ui_MainWindow

fpr: FPR = None


def setup_handlers(mw: Ui_MainWindow):
    def pass1_handler2():
        global fpr
        mw.err1.clear()
        mw.src2.clear()
        mw.err2.clear()
        mw.src3.clear()
        mw.pass2.setEnabled(False)
        try:
            tko = TKO(mw.tko)

            src_text = mw.src.toPlainText()
            tsi_table = mw.tsi

            fpr = do_first_pass(src_text, tko)

            tsi_table.setRowCount(len(fpr.tsi))
            tsi_table.setColumnCount(2)

            for i, (k, v) in enumerate(fpr.tsi.items()):
                tsi_table.setItem(i, 0, QTableWidgetItem(f'{k}'))
                tsi_table.setItem(i, 1, QTableWidgetItem(f'{hex(v)[2:].zfill(6)}'))

            mw.src2.appendPlainText(fpr.res_line)

        except Exception as e:
            mw.err1.appendPlainText(str(e))
            mw.src2.clear()
            mw.tsi.clear()
        else:
            mw.err1.appendPlainText(" --- Succesful --- ")
            mw.pass2.setEnabled(True)

    mw.pass1.clicked.connect(pass1_handler2)

    def pass2_handler2():
        mw.err2.clear()
        mw.src3.clear()
        global fpr
        try:
            H,I,E = do_second_pass(fpr)
        except Exception as e:
            mw.err2.appendPlainText(str(e))
            mw.src3.clear()
            return
        else:
            mw.err2.appendPlainText(" --- Succesful --- ")

        mw.src3.appendPlainText(H)
        mw.src3.appendPlainText(I)
        mw.src3.appendPlainText(E)

    mw.pass2.clicked.connect(pass2_handler2)

    mw.pass2.setEnabled(False)
