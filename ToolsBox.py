# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ToolsBox_backup.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class ToolsBox_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(326, 302)
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(10, 130, 301, 151))
        self.widget.setObjectName("widget")
        self.widget1 = QtWidgets.QWidget(self.widget)
        self.widget1.setGeometry(QtCore.QRect(0, 11, 301, 131))
        self.widget1.setObjectName("widget1")
        self.gridLayout = QtWidgets.QGridLayout(self.widget1)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_screenSize = QtWidgets.QPushButton(self.widget1)
        self.pushButton_screenSize.setObjectName("pushButton_screenSize")
        self.gridLayout.addWidget(self.pushButton_screenSize, 0, 0, 1, 1)
        self.pushButton_getBrightness = QtWidgets.QPushButton(self.widget1)
        self.pushButton_getBrightness.setObjectName("pushButton_getBrightness")
        self.gridLayout.addWidget(self.pushButton_getBrightness, 0, 1, 1, 1)
        self.pushButton_coordinate = QtWidgets.QPushButton(self.widget1)
        self.pushButton_coordinate.setObjectName("pushButton_coordinate")
        self.gridLayout.addWidget(self.pushButton_coordinate, 0, 2, 1, 1)
        self.pushButton_currentAtv = QtWidgets.QPushButton(self.widget1)
        self.pushButton_currentAtv.setObjectName("pushButton_currentAtv")
        self.gridLayout.addWidget(self.pushButton_currentAtv, 1, 0, 1, 1)
        self.pushButton_getCurrentPNG = QtWidgets.QPushButton(self.widget1)
        self.pushButton_getCurrentPNG.setObjectName("pushButton_getCurrentPNG")
        self.gridLayout.addWidget(self.pushButton_getCurrentPNG, 1, 1, 1, 1)
        self.pushButton_getAllPKG = QtWidgets.QPushButton(self.widget1)
        self.pushButton_getAllPKG.setObjectName("pushButton_getAllPKG")
        self.gridLayout.addWidget(self.pushButton_getAllPKG, 1, 2, 1, 1)
        self.pushButton_4 = QtWidgets.QPushButton(self.widget1)
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridLayout.addWidget(self.pushButton_4, 2, 0, 1, 1)
        self.pushButton_5 = QtWidgets.QPushButton(self.widget1)
        self.pushButton_5.setObjectName("pushButton_5")
        self.gridLayout.addWidget(self.pushButton_5, 2, 1, 1, 1)
        self.pushButton_adbCommand = QtWidgets.QPushButton(self.widget1)
        self.pushButton_adbCommand.setObjectName("pushButton_adbCommand")
        self.gridLayout.addWidget(self.pushButton_adbCommand, 2, 2, 1, 1)
        self.comboBox_devID = QtWidgets.QComboBox(Dialog)
        self.comboBox_devID.setGeometry(QtCore.QRect(70, 11, 151, 20))
        self.comboBox_devID.setObjectName("comboBox_devID")
        self.label_DevID = QtWidgets.QLabel(Dialog)
        self.label_DevID.setGeometry(QtCore.QRect(10, 11, 48, 21))
        self.label_DevID.setObjectName("label_DevID")
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setGeometry(QtCore.QRect(10, 120, 301, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.pushButton_lockDev = QtWidgets.QPushButton(Dialog)
        self.pushButton_lockDev.setGeometry(QtCore.QRect(238, 11, 71, 21))
        self.pushButton_lockDev.setObjectName("pushButton_lockDev")
        self.widget_info = QtWidgets.QWidget(Dialog)
        self.widget_info.setGeometry(QtCore.QRect(10, 40, 301, 81))
        self.widget_info.setObjectName("widget_info")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton_screenSize.setText(_translate("Dialog", "分辨率"))
        self.pushButton_getBrightness.setText(_translate("Dialog", "获取\\设置亮度"))
        self.pushButton_coordinate.setText(_translate("Dialog", "实时坐标"))
        self.pushButton_currentAtv.setText(_translate("Dialog", "当前Activity"))
        self.pushButton_getCurrentPNG.setText(_translate("Dialog", "截屏"))
        self.pushButton_getAllPKG.setText(_translate("Dialog", "获取所有APK"))
        self.pushButton_4.setText(_translate("Dialog", "PushButton"))
        self.pushButton_5.setText(_translate("Dialog", "PushButton"))
        self.pushButton_adbCommand.setText(_translate("Dialog", "ADB指令"))
        self.label_DevID.setText(_translate("Dialog", "DeviceID"))
        self.pushButton_lockDev.setText(_translate("Dialog", "Lock"))
