# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/first.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1347, 919)
        self.cw = QtWidgets.QWidget(MainWindow)
        self.cw.setObjectName("cw")
        self.full_pass = QtWidgets.QPushButton(self.cw)
        self.full_pass.setGeometry(QtCore.QRect(30, 710, 90, 32))
        self.full_pass.setObjectName("full_pass")
        self.tko = QtWidgets.QTableWidget(self.cw)
        self.tko.setGeometry(QtCore.QRect(20, 320, 331, 311))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.tko.setFont(font)
        self.tko.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tko.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tko.setShowGrid(True)
        self.tko.setRowCount(10)
        self.tko.setColumnCount(3)
        self.tko.setObjectName("tko")
        item = QtWidgets.QTableWidgetItem()
        self.tko.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tko.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tko.setHorizontalHeaderItem(2, item)
        self.tko.horizontalHeader().setVisible(False)
        self.tko.verticalHeader().setVisible(False)
        self.src = QtWidgets.QPlainTextEdit(self.cw)
        self.src.setGeometry(QtCore.QRect(20, 10, 331, 281))
        font = QtGui.QFont()
        font.setFamily("Monospace")
        font.setPointSize(12)
        self.src.setFont(font)
        self.src.setObjectName("src")
        self.err1 = QtWidgets.QPlainTextEdit(self.cw)
        self.err1.setGeometry(QtCore.QRect(810, 640, 431, 281))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.err1.setFont(font)
        self.err1.setFocusPolicy(QtCore.Qt.NoFocus)
        self.err1.setAcceptDrops(False)
        self.err1.setUndoRedoEnabled(False)
        self.err1.setReadOnly(True)
        self.err1.setObjectName("err1")
        self.src2 = QtWidgets.QPlainTextEdit(self.cw)
        self.src2.setGeometry(QtCore.QRect(810, 10, 431, 621))
        font = QtGui.QFont()
        font.setFamily("Monospace")
        font.setPointSize(12)
        self.src2.setFont(font)
        self.src2.setReadOnly(True)
        self.src2.setObjectName("src2")
        self.tsi = QtWidgets.QTableWidget(self.cw)
        self.tsi.setGeometry(QtCore.QRect(360, 10, 441, 621))
        self.tsi.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tsi.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tsi.setTabKeyNavigation(False)
        self.tsi.setProperty("showDropIndicator", False)
        self.tsi.setDragDropOverwriteMode(False)
        self.tsi.setShowGrid(True)
        self.tsi.setRowCount(2)
        self.tsi.setColumnCount(3)
        self.tsi.setObjectName("tsi")
        self.tsi.horizontalHeader().setVisible(False)
        self.tsi.horizontalHeader().setHighlightSections(False)
        self.tsi.verticalHeader().setVisible(False)
        self.tsi.verticalHeader().setHighlightSections(False)
        self.one_step = QtWidgets.QPushButton(self.cw)
        self.one_step.setGeometry(QtCore.QRect(140, 710, 90, 32))
        self.one_step.setObjectName("one_step")
        self.tm = QtWidgets.QTableWidget(self.cw)
        self.tm.setEnabled(False)
        self.tm.setGeometry(QtCore.QRect(360, 640, 441, 261))
        self.tm.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tm.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tm.setTabKeyNavigation(False)
        self.tm.setProperty("showDropIndicator", False)
        self.tm.setDragDropOverwriteMode(False)
        self.tm.setRowCount(2)
        self.tm.setColumnCount(2)
        self.tm.setObjectName("tm")
        self.tm.horizontalHeader().setVisible(False)
        self.tm.horizontalHeader().setHighlightSections(False)
        self.tm.verticalHeader().setVisible(False)
        self.tm.verticalHeader().setHighlightSections(False)
        self.format_choose = QtWidgets.QComboBox(self.cw)
        self.format_choose.setEnabled(False)
        self.format_choose.setGeometry(QtCore.QRect(30, 650, 221, 21))
        self.format_choose.setObjectName("format_choose")
        self.format_choose.addItem("")
        self.format_choose.addItem("")
        self.format_choose.addItem("")
        self.reset = QtWidgets.QPushButton(self.cw)
        self.reset.setGeometry(QtCore.QRect(80, 800, 90, 32))
        self.reset.setObjectName("reset")
        MainWindow.setCentralWidget(self.cw)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionLoad = QtWidgets.QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionLoad_2 = QtWidgets.QAction(MainWindow)
        self.actionLoad_2.setObjectName("actionLoad_2")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.full_pass.setText(_translate("MainWindow", "Full"))
        item = self.tko.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Name"))
        item = self.tko.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Code"))
        item = self.tko.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Count"))
        self.one_step.setText(_translate("MainWindow", "One step"))
        self.format_choose.setItemText(0, _translate("MainWindow", "DIrect"))
        self.format_choose.setItemText(1, _translate("MainWindow", "Relative"))
        self.format_choose.setItemText(2, _translate("MainWindow", "Mixed"))
        self.reset.setText(_translate("MainWindow", "Reset"))
        self.actionLoad.setText(_translate("MainWindow", "Load"))
        self.actionLoad_2.setText(_translate("MainWindow", "Load"))
