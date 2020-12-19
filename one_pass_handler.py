from typing import *

from PyQt5.QtWidgets import QTableWidget

from OnePass import do_one_pass
from tko import TKO
from ui.first import Ui_MainWindow

tko: TKO
src_text: str
tsi_table: QTableWidget
one_pass_fn: Callable


def setup_handlers(mw: Ui_MainWindow):
    def handle_one_pass():
        mw.src2.appendPlainText(str(one_pass_fn.__next__()))

    mw.one_step.clicked.connect(handle_one_pass)

    def handle_full():
        pass

    mw.full_pass.clicked.connect(handle_full)

    def handle_reset():
        global tko, src_text, tsi_table, one_pass_fn
        tko = TKO(mw.tko)
        src_text = mw.src.toPlainText()
        tsi_table = mw.tsi

        mw.src2.clear()
        mw.tsi.clear()
        mw.tm.clear()
        mw.err1.clear()

        one_pass_fn = do_one_pass(src_text, tko)

    mw.full_pass.clicked.connect(handle_reset)

    handle_reset()
