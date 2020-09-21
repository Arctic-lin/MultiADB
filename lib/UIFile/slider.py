# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'slider.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!

import sys
import subprocess
import re
import sip
import os
from threadFile import MyThread,GetDevThread,MonkeyThread,ToolsThread
from pypinyin import lazy_pinyin
from PyQt5.QtWidgets import QMainWindow,QApplication,QFileDialog,QTableWidgetItem,QMessageBox,QProgressBar,QDialog,QComboBox
from PyQt5 import QtWidgets
from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import QThread


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(271, 190)
        self.horizontalSlider = QtWidgets.QSlider(Dialog)
        self.horizontalSlider.setGeometry(QtCore.QRect(30, 120, 211, 31))
        self.horizontalSlider.setMaximum(255)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(100, 90, 51, 20))
        self.lineEdit.setObjectName("lineEdit")

        self.retranslateUi(Dialog)
        self.lineEdit.textChanged['QString'].connect(Dialog.textChangeSlider)
        self.horizontalSlider.valueChanged['int'].connect(Dialog.SliderChangetext)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))

class SliderDialog(QDialog,Ui_Dialog):

    popUp = pyqtSignal()

    def __init__(self):
        super(SliderDialog,self).__init__()
        self.setupUi(self)

    zxc#123


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SliderDialog()
    window.show()
    sys.exit(app.exec_())