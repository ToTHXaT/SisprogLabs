from typing import *

from PyQt5.QtWidgets import QTableWidgetItem

from FirstPass import do_first_pass, FPR
from SecondPass import do_second_pass
from tko import TKO
from ui.first import Ui_MainWindow

fpr_l: List[FPR] = None


def setup_handlers(mw: Ui_MainWindow):
    def pass1_handler2():
        global fpr_l
        mw.err1.clear()
        mw.src2.clear()
        mw.err2.clear()
        mw.src3.clear()
        mw.tm.clear()
        mw.pass2.setEnabled(False)
        try:
            tko = TKO(mw.tko)

            src_text = mw.src.toPlainText()
            tsi_table = mw.tsi

            fpr_l = do_first_pass(src_text, tko)

            tsi_table.setColumnCount(4)

            tsi_table.setRowCount(fpr_l[0].tsi.__len__())

            inserted = 0

            for fpr in fpr_l:
                rw = inserted
                rowCount = inserted + fpr.tsi.__len__()
                tsi_table.setRowCount(rowCount)
                for i, (k, (v, tp, prg)) in enumerate(fpr.tsi.items(), inserted):
                    tsi_table.setItem(i, 0, QTableWidgetItem(f'{k}'))

                    if v >= 0:
                        tsi_table.setItem(i, 1, QTableWidgetItem(f'{hex(v)[2:].zfill(6)}'))
                    else:
                        tsi_table.setItem(i, 1, QTableWidgetItem(f'-'))
                    tsi_table.setItem(i, 2, QTableWidgetItem(f'{tp}'))
                    tsi_table.setItem(i, 3, QTableWidgetItem(f'{prg}'))

                inserted += fpr.tsi.__len__()

            mw.src2.appendPlainText(fpr.res_line)

        except Exception as e:
            mw.err1.appendPlainText(str(e))
            mw.src2.clear()
            mw.tsi.clear()
            raise e
        else:
            mw.err1.appendPlainText(" !--- Succesful ---! ")
            mw.pass2.setEnabled(True)

    mw.pass1.clicked.connect(pass1_handler2)

    def pass2_handler2():
        mw.err2.clear()
        mw.src3.clear()
        mw.tm.clear()
        global fpr_l

        inserted = 0
        for fpr in fpr_l:
            try:
                frmt = mw.format_choose.currentText()
                H, I, E, tm = do_second_pass(fpr, frmt)
            except Exception as e:
                mw.err2.appendPlainText(str(e))
                mw.src3.clear()
                raise e
                return
            else:
                mw.err2.appendPlainText(" !--- Succesful ---! ")

            mw.src3.appendPlainText(H)
            mw.src3.appendPlainText(I)
            mw.src3.appendPlainText(E)
            mw.src3.appendPlainText("\n")

            mw.tm.setRowCount(inserted + len(tm))
            for i, (tmi, name) in enumerate(tm, inserted):
                mw.tm.setItem(i, 0, QTableWidgetItem(tmi))
                mw.tm.setItem(i, 1, QTableWidgetItem(name))

            inserted += len(tm)

    mw.pass2.clicked.connect(pass2_handler2)

    mw.pass2.setEnabled(False)
