# -*- coding: utf-8 -*-
# @Time    : 2020/7/15 11:38
# @Author  : Arctic
# @FileName: run.py
# @Software: PyCharm
# @Purpose :
# import logging
# logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

from lib.common import configLog
from lib.UIFile.main_ui import Ui_MainWindow
import sys
import subprocess
import re
import sip
import os
from lib.threadFile import MyThread, GetDevThread, MonkeyThread, ToolsThread
from pypinyin import lazy_pinyin
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QTableWidgetItem, QMessageBox, QProgressBar, QDialog, QComboBox
from lib.UIFile.ToolsBox import ToolsBox_Dialog
from PyQt5 import QtWidgets
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import QThread
from lib.UIFile.monkeyDialog import Ui_Dialog


devList = []
logger = configLog()
monkeyType, pushType, addCmd = "", "", ""
adb_progress = r".\lib\adb\adb.exe"

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.main_ui = Ui_MainWindow()
        self.setupUi(self)
        self.rbtn_fota.clicked.connect(lambda: self.radioEvent(self.rbtn_fota))
        self.rbtn_pushFile.clicked.connect(lambda: self.radioEvent(self.rbtn_pushFile))
        self.rbtn_installAPk.clicked.connect(lambda: self.radioEvent(self.rbtn_installAPk))
        self.rbtn_mute.clicked.connect(lambda: self.radioEvent(self.rbtn_mute))
        self.rbtn_edlMode.clicked.connect(lambda: self.radioEvent(self.rbtn_edlMode))
        self.rbtn_userdefine.clicked.connect(lambda: self.radioEvent(self.rbtn_userdefine))
        self.rbtn_monkeyPreset.clicked.connect(lambda: self.radioEvent(self.rbtn_monkeyPreset))
        self.rbtn_pushLog.clicked.connect(lambda: self.radioEvent(self.rbtn_pushLog))
        self.rbtn_tools.clicked.connect(lambda: self.radioEvent(self.rbtn_tools))
        self.btn_run.setEnabled(False)

    def radioEvent(self, btn):
        if self.widget.children():
            for i in self.widget.children():
                self.widget.children().remove(i)
                sip.delete(i)
        if btn == self.rbtn_fota:
            self.addFotaInterface()
        elif btn == self.rbtn_pushFile:
            self.addPushfileInterface()
        elif btn == self.rbtn_installAPk:
            self.addInstallInterface()
        elif btn == self.rbtn_mute:
            self.addMuteInterface()
        elif btn == self.rbtn_edlMode:
            self.addEdlModeInterface()
        elif btn == self.rbtn_userdefine:
            self.addUserDefineInterface()
        elif btn == self.rbtn_monkeyPreset:
            self.addMonkeyPresetInterface()
        elif btn == self.rbtn_pushLog:
            self.addPullLog()
        elif btn == self.rbtn_tools:
            self.addToolsBox()
        logger.info(btn.text())

    def openToolsBox(self):

        self.toolBoxMain = ToolsBoxDialog()
        self.hide()
        self.toolBoxMain.showUI()

    def flashDev(self):

        logger.info("%s" % self.btn_flashDev.text())
        devList.clear()
        self.btn_lockDev.setEnabled(True)
        self.btn_run.setEnabled(False)
        self.getDevSN = GetDevThread()
        devSN = self.getDevSN.getDevSN()
        self.tableWidget.clearContents()
        if devSN:
            self.tableWidget.setRowCount(len(devSN))
            for i in range(len(devSN)):
                if devSN[i][-1]:
                    newItem_deivceId = QTableWidgetItem(devSN[i][0])
                    if devSN[i][-1] == "device":
                        newItem_status = QTableWidgetItem("normal")
                    else:
                        newItem_status = QTableWidgetItem(devSN[i][-1])
                    self.tableWidget.setItem(i, 0, newItem_deivceId)
                    self.tableWidget.setItem(i, 1, newItem_status)
                    logger.info("检测到设备:%s,连接状态:%s" % (devSN[i][0], devSN[i][-1]))
        else:
            logger.info("未检测到连接设备")

    def lockDev(self):
        devList.clear()
        if self.tableWidget.rowCount():
            for i in range(self.tableWidget.rowCount()):
                if self.tableWidget.item(i, 0):
                    devSingleId = self.tableWidget.item(i, 0).text()
                    devSingleStatus = self.tableWidget.item(i, 1).text()
                    if devSingleStatus == "unauthorized":
                        QMessageBox.warning(self, "错误", "%s is %s"% (devSingleId,devSingleStatus), QMessageBox.Ok)
                        return False
                    elif devSingleStatus == "offline":
                        QMessageBox.warning(self, "错误", "%s is %s" % (devSingleId, devSingleStatus), QMessageBox.Ok)
                        return False
                    else:
                        devList.append(devSingleId)
                        self.tableWidget.item(i, 1).setText("Lock")
                else:
                    QMessageBox.warning(self, "错误", "未检测到设备", QMessageBox.Ok)
                    return False
        else:
            QMessageBox.warning(self, "错误", "未检测到设备", QMessageBox.Ok)
            return False
        self.btn_lockDev.setEnabled(False)
        self.btn_run.setEnabled(True)

    def run(self):
        if self.tableWidget.rowCount():
            thread_pool=[]
            for i in range(self.tableWidget.rowCount()):
                devSingleId = self.tableWidget.item(i, 0).text()
                #FOTA测试
                if self.rbtn_fota.isChecked():
                    testType = "FOTA"
                    upgrade = self.addLineEdit_upGrade.text()
                    dograde = self.addLineEdit_downGrade.text()
                    apkgrade = self.addLineEdit_fota_apkFile.text()
                    if not self.addLineEdit_fota_phoneDir.text():
                        self.addLineEdit_fota_phoneDir.setText("/sdcard")
                    phonedir = self.addLineEdit_fota_phoneDir.text()
                    self.th = MyThread(testType,devSingleId,upgrade,dograde,apkgrade,phonedir)
                    self.th.sinOutStatus.connect(self.devStatus)
                    self.th.sinOutProgress.connect(self.devProgress)
                    thread_pool.append(self.th)

                #pushFile
                if self.rbtn_pushFile.isChecked():
                    testType = "PushFile"
                    src = self.addLineEdit_push_srcFile.text()
                    if not self.addLineEdit_push_toFile.text():
                        self.addLineEdit_push_toFile.setText("/sdcard")
                    phonedir = self.addLineEdit_push_toFile.text()
                    getname = self.getName(src)
                    self.reName(0,src,getname)
                    self.th = MyThread(testType,devSingleId,src,phonedir)
                    self.th.sinOutStatus.connect(self.devStatus)
                    self.th.sinOutProgress.connect(self.devProgress)
                    thread_pool.append(self.th)

                #installAPK
                if self.rbtn_installAPk.isChecked():
                    testType = "InstallAPK"
                    src = self.addLineEdit_ins_srcFile.text()
                    getname = self.getName(src)
                    self.reName(0, src, getname)
                    self.th = MyThread(testType, devSingleId, src)
                    self.th.sinOutStatus.connect(self.devStatus)
                    self.th.sinOutProgress.connect(self.devProgress)
                    thread_pool.append(self.th)

                #Mute
                if self.rbtn_mute.isChecked():
                    testType = "Mute"
                    if self.addRBtn_onlyOne.isChecked():
                        loop=0
                        looptime=300
                    elif self.addRBtn_loop.isChecked():
                        loop=1
                        if not self.addLineEdit_loop.text():
                            self.addLineEdit_loop.setText("300")
                        looptime=self.addLineEdit_loop.text()

                    self.th = MyThread(testType,devSingleId, loop, int(looptime))
                    self.th.sinOutStatus.connect(self.devStatus)
                    self.th.sinOutProgress.connect(self.devProgress)
                    thread_pool.append(self.th)

                #Reboot
                if self.rbtn_edlMode.isChecked():
                    testType = "Reboot"
                    if self.addRbtn_reboot.isChecked():
                        reboot = 0
                    elif self.addRbtn_rebootEDL.isChecked():
                        reboot = 1
                    self.th = MyThread(testType, devSingleId, reboot)
                    self.th.sinOutStatus.connect(self.devStatus)
                    self.th.sinOutProgress.connect(self.devProgress)
                    thread_pool.append(self.th)

                #Monkey
                if self.rbtn_monkeyPreset.isChecked():
                    if self.addRadioBtn_MonkeyApply.isChecked() and self.addBtn_init.isEnabled():
                        button = QMessageBox.warning(self, "错误", "未进行初始化", QMessageBox.Yes)
                        if button == QMessageBox.Yes:
                            logger.info("未进行初始化")
                            return False
                    if self.addRadioBtn_MonkeyMedia.isChecked():
                        testType = "MonkeyMedia"
                        srcFile=""
                        apk=""
                        if self.addCheckBox_MonkeyAPK.isChecked():
                            apk = r".\lib\monkeySource\DataFiller.apk"
                        if self.addCheckBox_MonkeyMedia.isChecked():
                            srcFile = r".\lib\monkeySource"
                        if srcFile and apk:
                            self.th = MyThread(testType, devSingleId, srcFile ,apk)
                        elif srcFile and not apk:
                            self.th = MyThread(testType, devSingleId, srcFile)
                        elif apk and not srcFile:
                            self.th = MyThread(testType, devSingleId, apk)
                    elif self.addRadioBtn_MonkeyApply.isChecked():
                        testType = "MonkeyApply"
                        self.th = MyThread(testType,devSingleId,self.addRadioBtn_MonkeyApply.isChecked())
                    self.th.sinOutStatus.connect(self.devStatus)
                    self.th.sinOutProgress.connect(self.devProgress)
                    thread_pool.append(self.th)

                #UserDefine
                if self.rbtn_userdefine.isChecked():
                    testType = "Userdefine"
                    adb_command = self.addCommand.toPlainText()
                    if not adb_command:
                        # button = QMessageBox.warning(self, "Warning", "输入框为空", QMessageBox.Yes)
                        # if button == QMessageBox.Yes:
                        #     logger.info("Error:输入框为空")
                        #     return False
                        adb_command = "shell settings put global device_provisioned 1;" \
                                      "shell settings put secure user_setup_complete 1;" \
                                      "reboot"
                        self.th = MyThread(testType, devSingleId, adb_command)
                        self.th.sinOutStatus.connect(self.devStatus)
                        self.th.sinOutProgress.connect(self.devProgress)
                        thread_pool.append(self.th)
                    else:
                        self.th = MyThread(testType, devSingleId, adb_command)
                        self.th.sinOutStatus.connect(self.devStatus)
                        self.th.sinOutProgress.connect(self.devProgress)
                        thread_pool.append(self.th)

                #Pull log
                if self.rbtn_pushLog.isChecked():
                    testType = "PullLog"
                    if not self.addLineEdit_pull_toFile.text():
                        self.addLineEdit_pull_toFile.setText(r"/sdcard/TCTReport")
                    _from = self.addLineEdit_pull_toFile.text()
                    to = self.addLineEdit_pull_srcFile.text()
                    if os.path.isdir(to):
                        self.th = MyThread(testType, devSingleId, _from, to)
                        self.th.sinOutStatus.connect(self.devStatus)
                        self.th.sinOutProgress.connect(self.devProgress)
                        thread_pool.append(self.th)
                    else:
                        button = QMessageBox.warning(self, "Warning", "文件目录不存在", QMessageBox.Yes)
                        if button == QMessageBox.Yes:
                            logger.info("Error:文件目录不存在")
                            return False

            for th in thread_pool:
                th.start()
            for th in thread_pool:
                QThread.exec(th)

    def reName(self, testType, src, getName):
        if getName[0] == getName[1]:
            return logger.info("No need change File name")
        if testType == 0:
            if isinstance(getName[0], list):
                for i in range(len(getName[0])):
                    logger.info("Change %s to %s" % (getName[0][i], getName[1][i]))
                    srcPath = os.path.join(src,getName[0][i])
                    rePath = os.path.join(src,getName[1][i])
            elif isinstance(getName[0],str):
                logger.info("Change %s to %s" % (getName[0], getName[1]))
                srcPath = src
                splitSrc = os.path.split(src)
                rePath = os.path.join(splitSrc[0],getName[1])
            os.rename(srcPath,rePath)
        elif testType == 1:
            for i in range(len(getName[0])):
                logger.info("Change back %s to %s" % (getName[1][i], getName[0][i]))
                if isinstance(getName[0],list):
                    srcPath = os.path.join(src,getName[0][i])
                    rePath = os.path.join(src,getName[1][i])
                elif isinstance(getName[0], str):
                    srcPath = src
                    splitSrc = os.path.split(src)
                    rePath = os.path.join(splitSrc[0], getName[1])
                os.rename(rePath,srcPath)

    def getName(self, scr):
        old = []
        new = []
        new_new = []
        a = 0
        if os.path.isdir(scr):
            for i in os.listdir(scr):
                old.append(i)
                i = i.replace(" ", "")
                changeCNtoPinyin = lazy_pinyin(i)
                joinChange = ''.join(changeCNtoPinyin)
                new.append(joinChange)
            for i in new:
                if i not in new_new:
                    new_new.append(i)
                else:
                    a += 1
                    k = i.split(".")
                    h = k[0] + str(a) + "." + k[1]
                    new_new.append(h)
            return old, new_new
        else:
            old = os.path.split(scr)[-1]
            new = ''.join(lazy_pinyin(old))
            return old, new

    def devStatus(self,devid,devstate):
        if self.tableWidget.rowCount():
            for i in range(self.tableWidget.rowCount()):
                if self.tableWidget.item(i, 0) != None:
                    text = self.tableWidget.item(i, 0).text()
                    if text == devid:
                        newItem_deivceId = QTableWidgetItem(devstate)
                        self.tableWidget.setItem(i,1,newItem_deivceId)

    def devProgress(self,devid,int_value):
        if self.tableWidget.rowCount():
            for i in range(self.tableWidget.rowCount()):
                if self.tableWidget.item(i, 0) != None:
                    text = self.tableWidget.item(i, 0).text()
                    if text == devid:
                        qbar = QProgressBar()
                        qbar.setValue(int_value)
                        qbar.setStyleSheet("QProgressBar{color:black}")
                        self.tableWidget.setCellWidget(i, 2, qbar)

    def addFotaInterface(self):
        layout = QtWidgets.QGridLayout()
        #========================控件信息============================#
        self.addLable_upGrade = QtWidgets.QLabel(u"UpGrade File:")
        self.addLable_downGrade = QtWidgets.QLabel(u"DownGrade File:")
        self.addLable_apkFile = QtWidgets.QLabel(u"APK File:")
        self.addLable_phoneDir = QtWidgets.QLabel(u"Phone Dir:")
        self.addLineEdit_upGrade = QtWidgets.QLineEdit()
        self.addLineEdit_downGrade = QtWidgets.QLineEdit()
        self.addLineEdit_fota_apkFile = QtWidgets.QLineEdit()
        self.addLineEdit_fota_phoneDir = QtWidgets.QLineEdit()
        self.addLineEdit_fota_phoneDir.setPlaceholderText(r"/sdcard")
        self.addBtn_upGrade = QtWidgets.QPushButton(u"...")
        self.addBtn_downGrade = QtWidgets.QPushButton(u"...")
        self.addBtn_fota_apkFile = QtWidgets.QPushButton(u"...")
        #========================添加控件============================#
        layout.addWidget(self.addLable_upGrade,1,0)
        layout.addWidget(self.addLineEdit_upGrade,1,1)
        layout.addWidget(self.addBtn_upGrade,1,2)
        layout.addWidget(self.addLable_downGrade,2,0)
        layout.addWidget(self.addLineEdit_downGrade,2,1)
        layout.addWidget(self.addBtn_downGrade,2,2)
        layout.addWidget(self.addLable_apkFile,3,0)
        layout.addWidget(self.addLineEdit_fota_apkFile,3,1)
        layout.addWidget(self.addBtn_fota_apkFile,3,2)
        layout.addWidget(self.addLable_phoneDir,4,0)
        layout.addWidget(self.addLineEdit_fota_phoneDir,4,1,1,2)
        #=======================OK and Cancel======================#
        self.addBtn_upGrade.clicked.connect(lambda :self.chooseFiles(0,self.addLineEdit_upGrade))
        self.addBtn_downGrade.clicked.connect(lambda :self.chooseFiles(0,self.addLineEdit_downGrade))
        self.addBtn_fota_apkFile.clicked.connect(lambda :self.chooseFiles(1,self.addLineEdit_fota_apkFile))
        self.widget.setLayout(layout)

    def chooseFiles(self,intt,lineEdit):
        if intt == 0:
            file = QFileDialog.getOpenFileName(self, "选择文件", filter="Zip file (*.zip)")
        elif intt == 1:
            file = QFileDialog.getOpenFileName(self, "选择文件", filter="APK file (*.apk)")
        if file:
            lineEdit.setText(file[0])
            logger.info("%s" % file[0])

    def addPushfileInterface(self):
        layout = QtWidgets.QGridLayout()
        # ========================控件信息============================#
        self.addLable_srcFile = QtWidgets.QLabel(u"文件目录:")
        self.addLable_toFile = QtWidgets.QLabel(u"目标目录:")
        self.addLineEdit_push_srcFile = QtWidgets.QLineEdit()
        self.addLineEdit_push_toFile = QtWidgets.QLineEdit()
        self.addLineEdit_push_toFile.setPlaceholderText("/sdcard")
        # self.addBtn_push_singleFile = QtWidgets.QPushButton(u"单个文件")
        self.addBtn_push_multiFile = QtWidgets.QPushButton(u"文件目录")
        self.addFrame = QtWidgets.QFrame()
        self.addFrame.setFrameShape(QtWidgets.QFrame.HLine)
        self.addFrame.setFrameShadow(QtWidgets.QFrame.Sunken)
        # ========================添加控件============================#
        layout.addWidget(self.addLable_srcFile, 1, 0)
        layout.addWidget(self.addLineEdit_push_srcFile, 1, 1,1,3)
        layout.addWidget(self.addLable_toFile, 4, 0)
        layout.addWidget(self.addLineEdit_push_toFile, 4, 1,1,3)
        layout.addWidget(self.addFrame,3,0,1,4)
        # layout.addWidget(self.addBtn_push_singleFile, 2, 2)
        layout.addWidget(self.addBtn_push_multiFile, 2, 3)
        # =======================OK and Cancel======================#
        # self.addBtn_push_singleFile.clicked.connect(lambda: self.pushChoose(0, self.addLineEdit_push_srcFile))
        self.addBtn_push_multiFile.clicked.connect(lambda: self.pushChoose(1, self.addLineEdit_push_srcFile))
        self.widget.setLayout(layout)

    def addPullLog(self):
        layout = QtWidgets.QGridLayout()
        # ========================控件信息============================#
        self.addLable_pull_srcFile = QtWidgets.QLabel(u"文件目录:")
        self.addLable_pull_toFile = QtWidgets.QLabel(u"Log目录:")
        self.addLineEdit_pull_srcFile = QtWidgets.QLineEdit()
        self.addLineEdit_pull_toFile = QtWidgets.QLineEdit()
        self.addLineEdit_pull_toFile.setPlaceholderText("/sdcard/TCTReport")
        self.addBtn_pull_multiFile = QtWidgets.QPushButton(u"文件目录")
        self.addFrame = QtWidgets.QFrame()
        self.addFrame.setFrameShape(QtWidgets.QFrame.HLine)
        self.addFrame.setFrameShadow(QtWidgets.QFrame.Sunken)
        # ========================添加控件============================#
        layout.addWidget(self.addLable_pull_srcFile, 1, 0)
        layout.addWidget(self.addLineEdit_pull_srcFile, 1, 1,1,3)
        layout.addWidget(self.addLable_pull_toFile, 4, 0)
        layout.addWidget(self.addLineEdit_pull_toFile, 4, 1,1,3)
        layout.addWidget(self.addFrame,3,0,1,4)
        layout.addWidget(self.addBtn_pull_multiFile, 2, 3)
        # =======================OK and Cancel======================#
        self.addBtn_pull_multiFile.clicked.connect(lambda: self.pushChoose(1, self.addLineEdit_pull_srcFile))
        self.widget.setLayout(layout)

    def pushChoose(self,intt,lineEdit):
        if intt == 0:
            file = QFileDialog.getOpenFileName(self, "选择文件")
            if file:
                lineEdit.setText(file[0])
                logger.info("%s" % file[0])
        elif intt == 1:
            file = QFileDialog.getExistingDirectory(self, "选择文件")
            if file:
                lineEdit.setText(file)
                logger.info("%s" % file)

    def addInstallInterface(self):
        layout = QtWidgets.QGridLayout()
        # ========================控件信息============================#
        # use_info=u'\n单个文件:仅安装一个应用\n' \
        #          '文件目录:安装目录下的所以APK文件\n' \
        #          'PS:\n因ADB的特殊性,安装APK会把源文件名中带有中文\n' \
        #          '的包名改成拼音\n'
        use_info = u'\n' \
                   '文件目录:安装目录下的所以APK文件\n' \
                   'PS:\n因ADB的特殊性,安装APK会把源文件名中带有中文\n' \
                   '的包名改成拼音\n'
        self.addLable_des = QtWidgets.QLabel(use_info)
        self.addFrame = QtWidgets.QFrame()
        self.addFrame.setFrameShape(QtWidgets.QFrame.HLine)
        self.addFrame.setFrameShadow(QtWidgets.QFrame.Sunken)
        addFrame2 = QtWidgets.QFrame()
        self.addLable_ins_scrFile = QtWidgets.QLabel(u"文件目录:")
        self.addLineEdit_ins_srcFile = QtWidgets.QLineEdit()
        # self.addBtn_ins_singleFile = QtWidgets.QPushButton(u"单个文件")
        self.addBtn_ins_multiFile = QtWidgets.QPushButton(u"文件目录")
        # ========================添加控件============================#
        layout.addWidget(self.addLable_des, 1, 0,1,0)
        layout.addWidget(self.addFrame,2,0,1,0)
        layout.addWidget(self.addLable_ins_scrFile, 3, 0)
        layout.addWidget(self.addLineEdit_ins_srcFile, 3, 1,1,3)
        # layout.addWidget(self.addBtn_ins_singleFile, 4, 2)
        layout.addWidget(self.addBtn_ins_multiFile, 4, 3)
        # layout.addWidget(addFrame2,4,0)
        # =======================OK and Cancel======================#
        # self.addBtn_ins_singleFile.clicked.connect(lambda: self.installChoose(0, self.addLineEdit_ins_srcFile))
        self.addBtn_ins_multiFile.clicked.connect(lambda: self.installChoose(1, self.addLineEdit_ins_srcFile))
        self.widget.setLayout(layout)

    def installChoose(self,intt,lineEdit):
        if intt == 0:
            file = QFileDialog.getOpenFileName(self, "选择文件",filter="APK file (*.apk)")
            if file:
                lineEdit.setText(file[0])
                logger.info("%s" % file[0])
        elif intt == 1:
            file = QFileDialog.getExistingDirectory(self, "选择文件")
            if file:
                lineEdit.setText(file)
                logger.info("%s" % file)

    def addMuteInterface(self):
        layout = QtWidgets.QGridLayout()
        # ========================控件信息============================#
        use_info = u'\n1.仅执行一次静音\n' \
                   '2.循环执行,循环间隔时间执行一次静音\n'
        self.addLable_des = QtWidgets.QLabel(use_info)
        self.addFrame = QtWidgets.QFrame()
        self.addFrame.setFrameShape(QtWidgets.QFrame.HLine)
        self.addFrame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.addRBtn_onlyOne = QtWidgets.QRadioButton(u"仅执行一次")
        self.addRBtn_loop = QtWidgets.QRadioButton(u"循环执行")
        self.addLable_loop = QtWidgets.QLabel(u"循环间隔:")
        self.addLineEdit_loop = QtWidgets.QLineEdit()
        self.addLable_second = QtWidgets.QLabel(u"秒")
        self.addLable_blank1 = QtWidgets.QLabel()
        self.addLable_blank2 = QtWidgets.QLabel(" "*30)
        # ========================添加控件============================#
        layout.addWidget(self.addLable_des, 1, 0,1,4)
        layout.addWidget(self.addFrame, 2, 0, 1, 0)
        layout.addWidget(self.addRBtn_onlyOne, 3, 0,1,4)
        layout.addWidget(self.addRBtn_loop, 4, 0,1,4)
        layout.addWidget(self.addLable_loop, 5, 0)
        layout.addWidget(self.addLineEdit_loop,5,1)
        layout.addWidget(self.addLable_second, 5, 2)
        layout.addWidget(self.addLable_blank2, 5, 3)
        layout.addWidget(self.addLable_blank1, 6, 0)
        # =======================OK and Cancel======================#
        self.addRBtn_loop.setChecked(True)
        need_disable = [self.addLable_second,self.addLineEdit_loop,self.addLable_loop]
        self.addRBtn_onlyOne.clicked.connect(lambda :self.disableMute(0,need_disable))
        self.addRBtn_loop.clicked.connect(lambda: self.disableMute(1,need_disable))
        self.addLineEdit_loop.setPlaceholderText("300")
        _reg = QtCore.QRegExp('[1-9][0-9]{1,4}')
        self.addLineEdit_loop.setValidator(QtGui.QRegExpValidator(_reg,self))
        self.widget.setLayout(layout)

    def disableMute(self,intt,listt):
        if intt == 0:
            for i in listt:
                i.setEnabled(False)
        elif intt == 1:
            for i in listt:
                i.setEnabled(True)

    def addEdlModeInterface(self):
        layout = QtWidgets.QGridLayout()
        # ========================控件信息============================#
        self.addRbtn_reboot = QtWidgets.QRadioButton(u"adb reboot")
        self.addRbtn_rebootEDL = QtWidgets.QRadioButton(u"adb reboot edl")
        # ========================添加控件============================#
        layout.addWidget(self.addRbtn_reboot, 2, 0, 1, 4)
        layout.addWidget(self.addRbtn_rebootEDL, 3, 0, 1, 4)
        # =======================OK and Cancel======================#
        self.addRbtn_reboot.setChecked(True)
        self.widget.setLayout(layout)

    def addToolsBox(self):
        layout = QtWidgets.QGridLayout()
        # ========================控件信息============================#
        self.addPushBtn_tools = QtWidgets.QPushButton(u"工具箱")
        # ========================添加控件============================#
        layout.addWidget(self.addPushBtn_tools, 2, 0, 1, 4)
        # =======================OK and Cancel======================#
        self.addPushBtn_tools.setChecked(True)
        self.addPushBtn_tools.clicked.connect(lambda: self.openToolsBox())
        self.widget.setLayout(layout)

    def addUserDefineInterface(self):
        layout = QtWidgets.QGridLayout()
        # ========================控件信息============================#
        self.addCommand = QtWidgets.QPlainTextEdit()
        self.addCommand.setPlaceholderText("逐条输入adb指令并以\";\"分段\n例如:\nadb shell dumpsys meminfo;\n"
                                     "adb shell input kevent 3")
        # ========================添加控件============================#
        layout.addWidget(self.addCommand, 1, 0)
        # =======================OK and Cancel======================#
        self.widget.setLayout(layout)

    def addMonkeyPresetInterface(self):
        layout = QtWidgets.QGridLayout()
        # ========================控件信息============================#
        self.addRadioBtn_MonkeyMedia = QtWidgets.QRadioButton(u"拷贝媒体文件")
        self.addRadioBtn_MonkeyApply = QtWidgets.QRadioButton(u"App授权")
        self.addCheckBox_MonkeyMedia = QtWidgets.QCheckBox(u"Media文件")
        self.addCheckBox_MonkeyAPK = QtWidgets.QCheckBox(u"数据导入APK")
        self.addCheckBox_MonkeyonlyApply = QtWidgets.QCheckBox(u"仅授权")
        self.addCheckBox_MonkeyTest = QtWidgets.QCheckBox(u"Monkey测试")
        self.addCheckBox_MonkeyNohup = QtWidgets.QCheckBox(u"nohup")
        self.addCheckBox_MonkeyAddCmd = QtWidgets.QCheckBox(u"额外命令")
        self.addLineEdit_MonkeyAddCmd = QtWidgets.QLineEdit()
        self.addLineEdit_MonkeyAddCmd.setGeometry(QtCore.QRect(50,50,50,50))
        self.addLineEdit_MonkeyAddCmd.setEnabled(False)
        self.addDone = QtWidgets.QLabel("fail")
        pix = QtGui.QPixmap("./lib/fail.ico")
        self.addDone.setPixmap(pix)
        self.addFrame = QtWidgets.QFrame()
        self.addFrame.setFrameShape(QtWidgets.QFrame.HLine)
        self.addFrame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.addBtn_init = QtWidgets.QPushButton(u"初始化")
        # ========================添加控件============================#
        layout.addWidget(self.addRadioBtn_MonkeyMedia,1,0,1,2)
        layout.addWidget(self.addCheckBox_MonkeyMedia, 2, 0, 1, 1)
        layout.addWidget(self.addCheckBox_MonkeyAPK, 2, 1, 1, 2)
        layout.addWidget(self.addFrame,3,0,1,4)
        layout.addWidget(self.addRadioBtn_MonkeyApply, 4, 0, 1, 1)
        layout.addWidget(self.addCheckBox_MonkeyonlyApply, 5, 0, 1, 1)
        layout.addWidget(self.addCheckBox_MonkeyTest, 5, 1, 1, 1)
        layout.addWidget(self.addCheckBox_MonkeyNohup, 5, 2, 1, 1)
        layout.addWidget(self.addCheckBox_MonkeyAddCmd, 6, 0, 1, 1)
        layout.addWidget(self.addLineEdit_MonkeyAddCmd, 7, 0, 1, 3)
        layout.addWidget(self.addBtn_init, 8, 0, 1, 1)
        layout.addWidget(self.addDone,8,1,1,1)

        # =======================OK and Cancel======================#
        self.addCheckBox_MonkeyMedia.setChecked(True)
        self.addCheckBox_MonkeyNohup.setChecked(True)
        self.addRadioBtn_MonkeyMedia.clicked.connect(lambda: self.monkeyTestBtnEvent(self.addRadioBtn_MonkeyMedia))
        self.addRadioBtn_MonkeyApply.clicked.connect(lambda: self.monkeyTestBtnEvent(self.addRadioBtn_MonkeyApply))
        self.addCheckBox_MonkeyTest.clicked.connect(lambda: self.monkeyTestCheckBox(
            self.addCheckBox_MonkeyTest,self.addCheckBox_MonkeyTest.isChecked()))
        self.addCheckBox_MonkeyonlyApply.clicked.connect(lambda: self.monkeyTestCheckBox(
            self.addCheckBox_MonkeyonlyApply, self.addCheckBox_MonkeyonlyApply.isChecked()))
        self.addBtn_init.clicked.connect(
            lambda: self.monkeyDiaLogShow(self.addCheckBox_MonkeyonlyApply.isChecked(),self.addCheckBox_MonkeyNohup.isChecked()))
        self.addCheckBox_MonkeyAddCmd.clicked.connect(lambda: self.monkeyTestCheckBox(
            self.addCheckBox_MonkeyAddCmd, self.addCheckBox_MonkeyAddCmd.isChecked()))
        #Checkbox Enable/Disable关系
        self.addRadioBtn_MonkeyApply.setChecked(True)
        self.monkeyTestBtnEvent(self.addRadioBtn_MonkeyApply)
        self.widget.setLayout(layout)


    def monkeyTestBtnEvent(self,RbtnSelect):
        media = [self.addCheckBox_MonkeyMedia,self.addCheckBox_MonkeyAPK]
        apply = [self.addCheckBox_MonkeyonlyApply,self.addCheckBox_MonkeyTest,self.addCheckBox_MonkeyNohup,
                 self.addCheckBox_MonkeyAddCmd,self.addLineEdit_MonkeyAddCmd]
        if RbtnSelect == self.addRadioBtn_MonkeyMedia:
            for i in apply:
                i.setEnabled(False)
            for i in media:
                i.setEnabled(True)
            self.addBtn_init.setEnabled(False)
        elif RbtnSelect == self.addRadioBtn_MonkeyApply:
            for i in apply:
                i.setEnabled(True)
            for i in media:
                i.setEnabled(False)
            self.addBtn_init.setEnabled(True)
        if not self.addCheckBox_MonkeyAddCmd.isChecked():
            self.addLineEdit_MonkeyAddCmd.setEnabled(False)

    def monkeyTestCheckBox(self,checkBoxSelect,enable):
        checkBox = [self.addRadioBtn_MonkeyApply,self.addCheckBox_MonkeyTest]
        if checkBoxSelect == self.addCheckBox_MonkeyonlyApply:
            self.addCheckBox_MonkeyTest.setDisabled(enable)
            if enable == True:
                self.addCheckBox_MonkeyTest.setChecked(False)
        elif checkBoxSelect == self.addCheckBox_MonkeyTest:
            self.addCheckBox_MonkeyonlyApply.setDisabled(enable)
            if enable == True:
                self.addCheckBox_MonkeyonlyApply.setChecked(False)
        elif checkBoxSelect == self.addCheckBox_MonkeyAddCmd:
            self.addLineEdit_MonkeyAddCmd.setEnabled(enable)


    def monkeyDiaLogShow(self,onlyApply,nohup):
        if not self.addCheckBox_MonkeyonlyApply.isChecked() and not self.addCheckBox_MonkeyTest.isChecked():
            button = QMessageBox.warning(self, "错误", "请选择一种执行类型\n仅授权 or Monkey测试", QMessageBox.Yes)
            if button == QMessageBox.Yes:
                logger.info("未选择执行类型")
                return False
        global monkeyType,pushType,addCmd
        monkeyType, pushType, addCmd = "","",""
        if onlyApply:
            monkeyType = "OnlyApply"
        else:
            monkeyType = "MonkeyTest"
        if nohup:
            pushType = "nohup"
        else:
            pushType = "sh"
        if self.addCheckBox_MonkeyAddCmd.isChecked():
            cmd = self.addLineEdit_MonkeyAddCmd.text()
            if cmd:
                addCmd = cmd
        self.monkeyDialog = MonkeyDialog()
        self.monkeyDialog.dialogSignl.connect(self.slot_inner)
        self.monkeyDialog.show()

    def slot_inner(self,code):
        if code == 300:
            pix = QtGui.QPixmap("./lib/done.ico")
            self.addDone.setPixmap(pix)
            self.addBtn_init.setEnabled(False)

class MonkeyDialog(QDialog,Ui_Dialog):
    dialogSignl = pyqtSignal(int)

    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        if addCmd:
            self.th = MonkeyThread(monkeyType,pushType,addCmd)
        else:
            self.th = MonkeyThread(monkeyType, pushType)
        self.th.sinOutMonkey.connect(self.getMessage)
        self.th.start()
        logger.info("执行类型:%s,后台执行方式:%s"%(monkeyType,pushType))
        self.msgLog = []

    def getMessage(self,getCode,getMsg):
        self.msgLog.append(getMsg)
        self.label.setText(u"%s"%("\n".join(self.msgLog)))
        self.label.adjustSize()
        if getCode == 200:
            self.close()
        elif getCode == 300:
            button = QMessageBox.information(self, "Info", getMsg, QMessageBox.Yes)
            if button == QMessageBox.Yes:
                logger.info("完成")
                self.dialogSignl.emit(getCode)
                self.destroy()
                self.close()
                return True
        elif getCode == 400:
            button = QMessageBox.information(self, "Info", getMsg, QMessageBox.Yes)
            if button == QMessageBox.Yes:
                logger.info("完成")
                self.dialogSignl.emit(getCode)
                self.destroy()
                self.close()
                return True

    def run(self):
        pass


class ToolsBoxDialog(QDialog,ToolsBox_Dialog):

    popUp = pyqtSignal()

    def __init__(self):
        super(ToolsBoxDialog,self).__init__()
        self.setupUi(self)
        self.pushButton_lockDev.clicked.connect(self.lockDev)
        self.pushButton_getBrightness.clicked.connect(self.brightness)
        self.pushButton_screenSize.clicked.connect(self.getScreenSize)
        self.pushButton_coordinate.clicked.connect(self.getCoordinate)
        self.pushButton_currentAtv.clicked.connect(self.getNowpkg)
        self.pushButton_getCurrentPNG.clicked.connect(self.getScreenshot)
        self.pushButton_getAllPKG.clicked.connect(self.getAllPKG)
        self.comboBox_devID.close()
        self.comboBox_devID = CustomComboBox(self)
        self.comboBox_devID.setGeometry(QtCore.QRect(70, 11, 151, 20))
        self.comboBox_devID.currentIndexChanged.connect(self.enableLock)
        self.index = 0

    def addInterface(self,ui_type):
        if self.widget_info.children():
            for i in self.widget_info.children():
                self.widget_info.children().remove(i)
                sip.delete(i)
        layout = QtWidgets.QGridLayout()
        if ui_type == "Label":
            # ========================控件信息============================#
            self.label_DevInfo = QtWidgets.QLabel("Device Info")
            self.label_DevInfo.setWordWrap(True)
            # ========================添加控件============================#
            layout.addWidget(self.label_DevInfo, 2, 0, 1, 4)
        elif ui_type == "Slider":
            self.label_briNum = QtWidgets.QLabel("Value:")
            self.btn_briNum_set = QtWidgets.QPushButton("设置")
            self.btn_briNum_get = QtWidgets.QPushButton("获取")
            self.lineEdit_briNum = QtWidgets.QLineEdit()
            self.slider_briNum = QtWidgets.QSlider()
            self.slider_briNum.setMaximum(255)
            self.slider_briNum.setOrientation(QtCore.Qt.Horizontal)
            layout.addWidget(self.label_briNum, 2, 0, 1, 1)
            layout.addWidget(self.lineEdit_briNum, 2, 1, 1, 1)
            layout.addWidget(self.btn_briNum_set,2, 3, 1, 1)
            layout.addWidget(self.btn_briNum_get, 2, 2, 1, 1)
            layout.addWidget(self.slider_briNum, 3, 0, 1, 4)
            self.lineEdit_briNum.textChanged['QString'].connect(lambda :self.textChangeSlider())
            self.slider_briNum.valueChanged['int'].connect(lambda :self.SliderChangetext())
            self.btn_briNum_set.clicked.connect(lambda :self.setBrightnessByadb())
            self.btn_briNum_get.clicked.connect(lambda: self.getBrightnessByadb())
        elif ui_type == "Plain":
            self.plainText = QtWidgets.QPlainTextEdit()
            layout.addWidget(self.plainText)
        self.widget_info.setLayout(layout)

    def lockFirst(self):
        devId = self.comboBox_devID.currentText()
        lock_btn = self.pushButton_lockDev.isEnabled()
        if devId and not lock_btn:
            return devId
        if lock_btn:
            button = QMessageBox.information(self, "未锁定设备", "请先锁定设备", QMessageBox.Yes)
            if button == QMessageBox.Yes:
                logger.info("未锁定设备")
                return False

    def textChangeSlider(self):
        textNum = self.lineEdit_briNum.text()
        if not textNum:
            textNum = 0
        self.slider_briNum.setValue(int(textNum))

    def SliderChangetext(self):
        sliderNum = self.slider_briNum.value()
        self.lineEdit_briNum.setText(str(sliderNum))

    def setBrightnessByadb(self):
        devId = self.lockFirst()
        if devId:
            bri_num = self.lineEdit_briNum.text()
            self.th = ToolsThread("setBrightness",devId,bri_num)
            self.th.start()

    def getAllPKG(self):
        self.addInterface("Label")
        devId = self.lockFirst()
        if devId:
            self.th = ToolsThread("getAllPKG", devId)
            self.th.sinOutResult.connect(self.getMsg)
            self.th.start()

    def getBrightnessByadb(self):
        devId = self.lockFirst()
        if devId:
            self.th = ToolsThread("getBrightness", devId)
            self.th.sinOutResult.connect(self.getMsg)
            self.th.start()

    def getNowpkg(self):
        self.addInterface("Plain")
        devId = self.lockFirst()
        if devId:
            # devId = self.comboBox_devID.currentText()
            self.th = ToolsThread("GetNokPkg", devId)
            self.th.sinOutResult.connect(self.getMsg)
            self.th.start()

    def getScreenshot(self):
        devId = self.lockFirst()
        if devId:
            self.th = ToolsThread("getCurrentPNG", devId)
            self.th.start()

    def enableLock(self):
        self.pushButton_lockDev.setEnabled(True)

    def showUI(self):
        self.show()

    def lockDev(self):
        self.addInterface("Label")
        devId = self.comboBox_devID.currentText()
        if devId:
            self.pushButton_lockDev.setEnabled(False)
            self.th = ToolsThread("getDevInfo",devId)
            self.th.sinOutResult.connect(self.getMsg)
            self.th.start()

    def getMsg(self,code,text):
        if code == 200:
            try:
                self.label_DevInfo.setText(text)
            except RuntimeError as e:
                print(e)
        if code == 300:
            try:
                self.lineEdit_briNum.setText(text)
                self.slider_briNum.setValue(int(text))
            except RuntimeError as e:
                print(e)
        if code == 400:
            try:
                self.plainText.setPlainText(text)
            except RuntimeError as e:
                print(e)

    def brightness(self):
        devId = self.comboBox_devID.currentText()
        self.th = ToolsThread("killAdb",devId)
        # self.th.sinOutResult.connect(self.getMsg)
        self.th.start()
        self.addInterface("Slider")

    def getScreenSize(self):
        self.addInterface("Label")
        # devId = self.comboBox_devID.currentText()
        devId = self.lockFirst()
        if devId:
            self.th = ToolsThread("getScreenSize", devId)
            self.th.sinOutResult.connect(self.getMsg)
            self.th.start()

    def getCoordinate(self):
        self.addInterface("Label")
        devId = self.lockFirst()
        if devId:
            self.th = ToolsThread("getCoordinate",devId)
            self.th.sinOutResult.connect(self.getMsg)
            self.th.start()

class CustomComboBox(QComboBox):
    popUP = pyqtSignal()

    def __init__(self,parent = None):
        super(CustomComboBox,self).__init__(parent)

    def showPopup(self):
        self.clear()
        self.insertItem(0,"None")
        index = 1
        devInfo = subprocess.check_output("%s devices"%adb_progress, encoding="utf-8")
        devSN = re.findall("\n" + "(.*?)" + r"\tdevice", devInfo)
        if devSN:
            for i in devSN:
                self.insertItem(index,i)
                index += 1
        QComboBox.showPopup(self)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())