from typing import *

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from OnePass import do_one_pass
from tko import TKO
from ui.first import Ui_MainWindow

tko: TKO
src_text: str
tsi_table: QTableWidget
one_pass_fn: Callable


def setup_handlers(mw: Ui_MainWindow):
    was_first = False

    def handle_one_pass():
        global src_text, one_pass_fn
        nonlocal was_first
        is_end = False
        if not was_first:
            was_first = True
            mw.src.setReadOnly(True)
            mw.err1.clear()
            mw.src2.clear()
            mw.tsi.clear()
            mw.tm.clear()

            src_text = mw.src.toPlainText()

            frmt = mw.format_choose.currentText()

            one_pass_fn = do_one_pass(src_text, tko, frmt)

        try:
            module_l = one_pass_fn.__next__()
        except StopIteration:
            is_end = True
            mw.err1.appendPlainText(" --- Success --- ")
            mw.one_step.setEnabled(False)
            return True
        except Exception as e:
            mw.one_step.setEnabled(False)
            mw.full_pass.setEnabled(False)
            mw.err1.appendPlainText(str(e))
            return True

        mw.src2.clear()
        mw.tsi.clear()
        mw.tm.clear()
        mw.err1.clear()

        tsi_table.setColumnCount(5)

        tsi_table.setRowCount(module_l[0].tsi.__len__())

        inserted = 0

        for module in module_l:
            mw.src2.appendPlainText(str(module))

            rw = inserted
            row_count = inserted + module.tsi.__len__()
            tsi_table.setRowCount(row_count)
            for i, (k, (v, tp, prg, ref_list)) in enumerate(module.tsi.items(), inserted):
                tsi_table.setItem(i, 0, QTableWidgetItem(f'{k}'))

                if v >= 0:
                    tsi_table.setItem(i, 1, QTableWidgetItem(f'{hex(v)[2:].zfill(6)}'))
                else:
                    tsi_table.setItem(i, 1, QTableWidgetItem(f'-'))
                tsi_table.setItem(i, 2, QTableWidgetItem(f'{tp}'))
                tsi_table.setItem(i, 3, QTableWidgetItem(f'{prg}'))
                tsi_table.setItem(i, 4, QTableWidgetItem(' '.join(str(k) for k in ref_list)))

            inserted += module.tsi.__len__()

            inserted = 0
            tm = module.tm.lst
            mw.tm.setRowCount(inserted + len(tm) + 1)
            for i, (tmi, name) in enumerate(tm, inserted):
                mw.tm.setItem(i, 0, QTableWidgetItem(tmi))
                mw.tm.setItem(i, 1, QTableWidgetItem(name))

            mw.tm.setItem(inserted + len(tm), 0, QTableWidgetItem(''))
            mw.tm.setItem(inserted + len(tm), 1, QTableWidgetItem(''))

            inserted += 1

            inserted += len(tm)

        return is_end

    mw.one_step.clicked.connect(handle_one_pass)

    def handle_full():
        while not handle_one_pass():
            pass

    mw.full_pass.clicked.connect(handle_full)

    def handle_reset():
        global tko, src_text, tsi_table, one_pass_fn
        nonlocal was_first
        mw.one_step.setEnabled(True)
        mw.full_pass.setEnabled(True)
        tko = TKO(mw.tko)
        mw.src.setReadOnly(False)
        tsi_table = mw.tsi
        was_first = False

        # mw.src2.clear()
        # mw.tsi.clear()
        # mw.tm.clear()
        # mw.err1.clear()

    mw.reset.clicked.connect(handle_reset)

    handle_reset()
