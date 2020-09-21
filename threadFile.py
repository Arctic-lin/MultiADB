# -*- coding: utf-8 -*-
# @Time    : 2020/8/4 10:47
# @Author  : Arctic
# @FileName: threadFile.py
# @Software: PyCharm
# @Purpose : multiADB threadFile
from common import configLog
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import QThread
import subprocess
import re
import sip
import os

logger = configLog()
adb_progress = r".\lib\adb\adb.exe"
adb_pid = ""

#MainThread


class MyThread(QThread):
    sinOutStatus = pyqtSignal(str, str)
    sinOutProgress = pyqtSignal(str, int)
    sinOutMonkey = pyqtSignal(int, str)

    def __init__(self, testType, dev, *args):
        super().__init__()
        self.dev = dev
        self.testType = testType
        self.args = args

    def shellCmd(self, *args, need_stdout=0):
        cmd_line = [adb_progress] + ["-s", self.dev] + list(args)
        cmd_line_str = " ".join(cmd_line)
        logger.info('cmd:{}'.format(cmd_line_str))
        proc = subprocess.Popen(cmd_line_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        proc.wait()
        if need_stdout == 0:
            return stdout
        elif need_stdout == 1:
            return stderr
        elif need_stdout == 2:
            return stdout, stderr

    def isFileExistsInADB(self, phoneDir):
        if phoneDir == r"/sdcard" or r"/sdcard/":
            return True
        else:
            proc = self.shellCmd("shell ls -a %s" % phoneDir, need_stdout=2)
            if "No such file" in proc[1]:
                return False
            elif proc[0]:
                return True

    def mkdirDocument(self, phoneDir):
        if self.isFileExistsInADB(phoneDir):
            return logger.info("%s - PhoneDir is Exists,No need to creat" % self.dev)
        else:
            logger.info("%s - Creat File:%s..." % (self.dev, phoneDir))
            self.shellCmd("shell mkdir %s" % phoneDir)
            if self.isFileExistsInADB(phoneDir):
                return logger.info("%s - Creat Success..." % self.dev)

    #FOTA test
    def fotaTest(self):
        ######args0 = upgradeFile
        ######args1 = downgradeFile
        ######args2 = APkFile
        ######args3 = PhoneDir
        self.sinOutStatus.emit(self.dev, "设置Never Sleep")
        self.sinOutProgress.emit(self.dev, 5)
        # subprocess.call("adb -s %s shell settings put system screen_off_timeout 1" % self.dev)
        self.shellCmd("shell settings put system screen_off_timeout 1")
        self.sinOutProgress.emit(self.dev, 10)
        # 执行静音脚本
        self.sinOutStatus.emit(self.dev, "设置静音")
        self.sinOutProgress.emit(self.dev, 15)
        for i in range(1, 11):
            # subprocess.call("adb -s %s shell media volume --stream %d --set 0" % (self.dev, i))
            self.shellCmd("shell media volume --stream %d --set 0" % i)
        self.sinOutProgress.emit(self.dev, 25)
        # 推送文件
        self.sinOutStatus.emit(self.dev, "推送Upgrade文件")
        self.sinOutProgress.emit(self.dev, 30)
        # subprocess.call(r"adb -s %s push %s %s/upgrade.zip" % (self.dev, self.args[0] , self.args[3]), shell=True)
        self.shellCmd("push %s %s/upgrade.zip" % (self.args[0], self.args[3]))
        self.sinOutProgress.emit(self.dev, 50)
        self.sinOutStatus.emit(self.dev, "推送Downgrade文件")
        self.sinOutProgress.emit(self.dev, 55)
        # subprocess.call(r"adb -s %s push %s %s/downgrade.zip" % (self.dev, self.args[1] ,self.args[3]), shell=True)
        self.shellCmd("push %s %s/downgrade.zip" % (self.args[1], self.args[3]))
        self.sinOutProgress.emit(self.dev, 80)
        # 安装apk
        self.sinOutStatus.emit(self.dev, "安装APK")
        # subprocess.call("adb -s %s install -r %s" % (self.dev, self.args[2]))
        self.shellCmd("install -r %s"%(self.args[2]))
        self.sinOutProgress.emit(self.dev, 100)
        self.sinOutStatus.emit(self.dev, "完成")

    #pushFile
    def pushTest(self):
        #args0 = 0 or 1 来判断单个文件还是整个文件
        #args1 = dir
        #args2 = phoneDir
        self.sinOutStatus.emit(self.dev, "检查PhoneDir是否存在")
        self.sinOutProgress.emit(self.dev, 5)
        # self.mkdirDocument(self.args[1])
        self.sinOutStatus.emit(self.dev, "推送文件")
        self.sinOutProgress.emit(self.dev, 10)
        if os.path.isdir(self.args[0]):
            filesList = os.listdir(self.args[0])
            filesNum = len(filesList)
            progress_ = 90 // filesNum
            for i in range(filesNum):
                filesPath = os.path.join(self.args[0], filesList[i])
                self.sinOutStatus.emit(self.dev, "%s" % filesList[i])
                if os.path.isfile(filesPath):
                    filesSize = os.path.getsize(filesPath)
                    if filesSize > 1073741824:
                        self.sinOutStatus.emit(self.dev, "%s\n大于1GB,耐心等待"% filesList[i])
                self.shellCmd("push -p %s %s" % (filesPath, self.args[1]))
                self.sinOutProgress.emit(self.dev, 10 + progress_)
        self.sinOutStatus.emit(self.dev, "完成")
        self.sinOutProgress.emit(self.dev, 100)

    #install apk
    def installAPK(self):
        #args0 = src dir
        self.sinOutStatus.emit(self.dev, "安装文件")
        self.sinOutProgress.emit(self.dev, 5)
        apkList=[]
        for root, dirs, files in os.walk(self.args[0]):
            for i in files:
                if ".apk" in i:
                    apkList.append(os.path.join(self.args[0], i))
        count_progress=100//len(apkList)
        first = 0
        for i in apkList:
            first += count_progress
            self.sinOutStatus.emit(self.dev, "%s" % (os.path.split(i)[1]))
            self.shellCmd("install -r %s" % i)
            self.sinOutProgress.emit(self.dev, first)
        self.sinOutStatus.emit(self.dev, "完成")
        self.sinOutProgress.emit(self.dev, 100)

    #Mute
    def Mute(self):

        #args0 = loop
        #args1 = looptime
        self.sinOutStatus.emit(self.dev, "静音")
        self.sinOutProgress.emit(self.dev, 5)
        if self.args[0] == 0:
            count_ = 10
            for i in range(1, 11):
                # subprocess.call("adb -s %s shell media volume --stream %d --set 0" % (self.dev, i))
                self.shellCmd("shell media volume --stream %d --set 0" % i)
                self.sinOutProgress.emit(self.dev, count_)
                count_ +=10

        elif self.args[0] == 1:
            if self.args[1]:
                #loopTime = self.args[1]
                pass
        self.sinOutStatus.emit(self.dev, "完成")
    #Reboot
    def rebootDev(self):

        #args0 = reboot type
        self.sinOutStatus.emit(self.dev, "重启")
        self.sinOutProgress.emit(self.dev, 20)
        if self.args[0] == 0:
            self.shellCmd("reboot")
        elif self.args[0] == 1:
            self.shellCmd("reboot edl")
        self.sinOutProgress.emit(self.dev, 100)
        self.sinOutStatus.emit(self.dev, "完成")

    #Monkey
    def monkey(self):

        #args[0]=src
        #args[1]=apk
        if self.testType == "MonkeyMedia":
            if len(self.args) == 2:
                logger.info("拷贝媒体文件和安装APK")
                self.sinOutStatus.emit(self.dev, "Monkey文件")
                self.sinOutProgress.emit(self.dev, 40)
                self.shellCmd("push %s %s"%(self.args[0], "/sdcard/MonkeySource"))
                self.sinOutStatus.emit(self.dev, "安装APK")
                self.shellCmd("install -r %s"%(self.args[1]))
                self.sinOutProgress.emit(self.dev, 80)
                self.sinOutStatus.emit(self.dev, "完成")
                self.sinOutProgress.emit(self.dev, 100)
            elif len(self.args) == 1:
                if "apk" in self.args[0]:
                    logger.info("仅安装APK")
                    self.sinOutStatus.emit(self.dev, "安装apk")
                    self.sinOutProgress.emit(self.dev, 20)
                    self.shellCmd("install -r %s" % (self.args[0]))
                    self.sinOutStatus.emit(self.dev, "完成")
                    self.sinOutProgress.emit(self.dev, 100)
                else:
                    logger.info("仅导入媒体文件")
                    self.sinOutStatus.emit(self.dev, "Monkey文件")
                    self.sinOutProgress.emit(self.dev, 20)
                    self.shellCmd("push %s %s" % (self.args[0], "/sdcard/MonkeySource"))
                    self.sinOutStatus.emit(self.dev, "完成")
                    self.sinOutProgress.emit(self.dev, 100)
        elif self.testType == "MonkeyApply":
            logger.info("执行授权")
            self.sinOutProgress.emit(self.dev, 20)
            self.sinOutStatus.emit(self.dev, "推送后台脚本")
            self.sinOutProgress.emit(self.dev, 25)
            self.sinOutStatus.emit(self.dev, "推送静音脚本")
            self.shellCmd(r"push ./lib/Mute.sh /data/local/tmp")
            self.sinOutProgress.emit(self.dev, 40)
            self.sinOutStatus.emit(self.dev, "推送授权脚本")
            self.shellCmd(r"push main.sh /data/local/tmp")
            self.sinOutProgress.emit(self.dev, 100)
            self.sinOutStatus.emit(self.dev, "推送完成")
            self.shellCmd(r"shell < main.txt")

    def reAdbCommand(self, text):
        comm = []
        if ";" in text:
            eachCommand = text.split(";")
            for i in eachCommand:
                listCmd = i.split(" ")
                if ">" in listCmd or ">>" in listCmd:
                    text = listCmd[-1]
                    if "\\" in text:
                        j = os.path.split(text)
                        addDevInfo = os.path.join(j[0], self.dev+"_"+j[-1])
                    else:
                        addDevInfo = self.dev + listCmd[-1]
                    listCmd.pop(-1)
                    listCmd.append(addDevInfo)
                comm.append(listCmd)
        else:
            eachCommand = text.split(" ")
            if ">" in eachCommand or ">>" in eachCommand:
                text = eachCommand[-1]
                if "\\" in text:
                    j = os.path.split(text)
                    addDevInfo = os.path.join(j[0], self.dev+"_"+j[-1])
                else:
                    addDevInfo = self.dev + eachCommand[-1]
                text = self.dev + eachCommand[-1]
                eachCommand.pop(-1)
                eachCommand.append(addDevInfo)
            comm.append(eachCommand)
        return comm
    #UserDefine
    def userDefine(self):
        self.sinOutStatus.emit(self.dev, "处理ADB命令")
        self.sinOutProgress.emit(self.dev, 5)
        #args[0] = adbCommand
        getArgs = self.args[0]
        comm = self.reAdbCommand(getArgs)
        a = 5
        for i in comm:
            a +=5
            self.sinOutStatus.emit(self.dev, "执行ADB命令")
            self.sinOutProgress.emit(self.dev, a)
            if "adb" in i:
                i.pop(0)
            if "logcat" in i:
                self.sinOutStatus.emit(self.dev, "抓取Log中,需停止抓取,可拔掉手机")
            self.shellCmd(" ".join(i))
        self.sinOutStatus.emit(self.dev, "完成")
        self.sinOutProgress.emit(self.dev, 100)

    #文件导出
    def pullLog(self):
        #args[0] == /sdcard文件
        #args[1] == 电脑目录
        self.sinOutStatus.emit(self.dev, "在%s下生成%s文件夹"%(self.args[1], self.dev))
        self.sinOutProgress.emit(self.dev, 5)
        new_path = os.path.join(self.args[1], self.dev)
        # if os.path.isdir(self.args[1]):
        #     new_path = os.path.join(self.args[1], self.dev)
        if not os.path.isdir(new_path):
            os.mkdir(new_path)
        # self.mkdirDocument(self.args[1])
        self.sinOutStatus.emit(self.dev, "导出文件")
        self.sinOutProgress.emit(self.dev, 30)
        self.shellCmd("pull -p %s %s" % (self.args[0], new_path))
        self.sinOutStatus.emit(self.dev, "完成")
        self.sinOutProgress.emit(self.dev, 100)
        pass

    def test(self):
        print(self.testType, self.dev, self.args)
        self.sinOutStatus.emit(self.dev, "设置Never Sleep")
        self.sinOutProgress.emit(self.dev, 5)

    def checkTestType(self):
        if self.testType == "FOTA":
            self.fotaTest()
        elif self.testType =="PushFile":
            self.pushTest()
        elif self.testType =="InstallAPK":
            self.installAPK()
        elif self.testType =="Mute":
            self.Mute()
        elif self.testType =="Reboot":
            self.rebootDev()
        elif self.testType =="Userdefine":
            self.userDefine()
        elif self.testType =="MonkeyApply":
            self.monkey()
        elif self.testType == "MonkeyMedia":
            self.monkey()
        elif self.testType == "PullLog":
            self.pullLog()

    def run(self):
        self.checkTestType()


#GetDevThread
class GetDevThread(QThread):
    def __init__(self):
        super().__init__()

    def shellCmd(self, *args):
        cmd_line = [adb_progress] + list(args)
        cmd_line_str = " ".join(cmd_line)
        print('cmd:{}'.format(cmd_line_str))
        proc = subprocess.Popen(cmd_line_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        proc.wait()
        return stdout

    def getDevSN(self):
        devInfo = self.shellCmd("devices")
        devDecode = devInfo.decode("utf-8")
        devSN = re.findall("\n" + "(.*?)" + r"\t" + "(device|unauthorized|offline)", devDecode)
        # print(devSN)
        return devSN


#MonkeyThread
class MonkeyThread(QThread):
    sinOutMonkey = pyqtSignal(int, str)

    def __init__(self, testType, pushType, *args):
        super().__init__()
        self.testType = testType
        self.pushType = pushType
        self.args = args

    def shellCmd(self, *args):

        cmd_line = [adb_progress] + list(args)
        cmd_line_str = " ".join(cmd_line)
        print('cmd:{}'.format(cmd_line_str))
        proc = subprocess.Popen(cmd_line_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        proc.wait()
        return stdout

    def getDevSN(self):
        self.sinOutMonkey.emit(100, "正在进行Monkey初始化, 请连接仅一台测试设备进行初始化..")
        self.shellCmd("wait-for-device")
        devInfo = self.shellCmd("devices")
        devDecode = devInfo.decode("utf-8")
        devSN = re.findall("\n" + "(.*?)" + r"\t", devDecode)
        self.sinOutMonkey.emit(100, "检测到设备:%s" % devSN[0])
        return devSN

    def getPermmision(self):
        self.shellCmd("shell setprop debug.print.log True")
        self.shellCmd("shell setprop debug.tct.enable_monkey_log True")
        allGrantCmd = []
        cmdGetPkg = "shell monkey -c android.intent.category.LAUNCHER  -v -v -v 0"
        allPkg = self.shellCmd(cmdGetPkg).decode("utf-8")
        re_allPkg = re.findall("from\spackage\s*" + "(.*?)" + "\\)", allPkg)
        for pkg in re_allPkg:
            try:
                getFalse = subprocess.check_output \
                    ("%s shell dumpsys package %s | grep granted=false" % (adb_progress, pkg), encoding="utf-8")
                if getFalse:
                    re_getFalse = re.findall("\s*" + "(.*?)" + "\\:", getFalse)
                    for p in re_getFalse:
                        allGrantCmd.append("pm grant %s %s" % (pkg, p))
            except subprocess.CalledProcessError as e:
                logger.info("Warnning!!! %s" % e)
        return allGrantCmd

    def getDevLog(self):
        log_tools = {
            "com.tcl.logger":
                "am startservice -n com.tcl.logger/com.tcl.logger.service.LogSwitchService -a com.tcl.logger.turnon",
            "com.debug.loggerui":
                "am broadcast -a com.debug.loggerui.ADB_CMD -e cmd_name start --ei cmd_target 1 -f 0x01000000",
            "com.tct.feedback":
                "am start com.tct.feedback/.external.activity.MainActivity",
            "com.mediatek.mtklogger":
                "am broadcast -a com.mediatek.mtklogger.ADB_CMD -e cmd_name start --ei cmd_target 1"
        }
        for tools in log_tools.items():
            pmList = subprocess.check_output\
                ("adb shell pm list package %s" % (tools[0]), encoding="utf-8")
            if pmList:
                return tools
            else:
                self.sinOutMonkey.emit(100, "未检测到Log工具")
                return logger.info("No detect log tools")

    def getAddCmd(self):
        if self.args:
            _cmd = self.args[0]
            if "adb shell " in _cmd:
                _cmd = _cmd.replace("adb shell ", "")
            if ";" in _cmd:
                list_ccmd = _cmd.split(";")
                return list_ccmd
            else:
                return _cmd
        return False

    def creatShellSript(self):
        self.sinOutMonkey.emit(100, "获取设备APK信息...")
        allGrant = self.getPermmision()
        if allGrant:
            self.sinOutMonkey.emit(100, "获取设备Log工具...")
            log_tools = self.getDevLog()
            if log_tools:
                self.sinOutMonkey.emit(100, "Log工具为:%s\n生成脚本中..." % log_tools[0])
            with open("main.sh", "w", encoding="utf-8", newline='\n') as f:
                # 设置Never sleep
                f.writelines("settings put system screen_off_timeout 1\n")
                #授权命令
                for i in allGrant:
                    f.writelines("%s\n"%i)
            # 仅授权的话添加am启动Settings来辨识脚本执行完成
                if self.testType == "OnlyApply":
                    f.writelines("am start com.android.settings\n")
                # Log屏蔽
                elif self.testType == "MonkeyTest":
                    f.writelines("setprop debug.print.log false\n")
                    f.writelines("setprop debug.tct.enable_monkey_log false\n")
                    # 通过
                    if log_tools:
                        f.writelines(log_tools[1] + "\n")
                #写入额外指令内容
                _cmd = self.getAddCmd()
                if _cmd:
                    if isinstance(_cmd, str):
                        self.sinOutMonkey.emit(100, "添加额外命令:%s"%_cmd)
                        f.writelines(_cmd + "\n")
                    elif isinstance(_cmd, list):
                        for i in _cmd:
                            if i:
                                self.sinOutMonkey.emit(100, "添加额外命令:%s" % i)
                                f.writelines(i + "\n")
                ### 写入执行静音脚本指令
                if self.pushType == "nohup":
                    f.writelines(r"nohup sh /data/local/tmp/Mute.sh&" + "\n")
                else:
                    f.writelines(r"sh /data/local/tmp/Mute.sh&" + "\n")
            ### 执行脚本
            with open("main.txt", "w", encoding="utf-8") as f:
                if self.pushType == "nohup":
                    f.write(r"cd /data/local/tmp" + "\n" + "nohup sh main.sh&" + "\n")
                else:
                    f.write(r"cd /data/local/tmp" + "\n" + "sh main.sh&" + "\n")
            self.sinOutMonkey.emit(300, "完成")
        else:
            self.sinOutMonkey.emit(400, "未检测到需要授权的APP")


    def run(self):
        self.getDevSN()
        self.creatShellSript()

class ToolsThread(QThread):

    sinOutResult = pyqtSignal(int, str)

    def __init__(self, testType, dev, *args):
        super().__init__()
        self.dev = dev
        self.testType = testType
        self.args = args
        self.working = False

    def __del__(self):
        self.working = False

    def shellCmd(self, *args):

        cmd_line = [adb_progress] + ["-s %s" % self.dev] + list(args)
        cmd_line_str = " ".join(cmd_line)
        logger.info('cmd:{}'.format(cmd_line_str))
        proc = subprocess.Popen(cmd_line_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True)
        stdout, stderr = proc.communicate()
        proc.wait()
        return stdout

    def getAllPKG(self):
        self.sinOutResult.emit(200, "获取中")
        getLogStatus_hz = self.shellCmd("shell getprop debug.print.log")
        getLogStatus_sz = self.shellCmd("shell getprop debug.tct.enable_monkey_log")
        if getLogStatus_hz and "False" in getLogStatus_hz:
            logger.info("检测到MonkeyLog被屏蔽,正在打开")
            self.sinOutResult.emit(200, "检测到MonkeyLog被屏蔽,正在打开")
            self.shellCmd("shell setprop debug.print.log True")
        if getLogStatus_sz and "False" in getLogStatus_sz:
            logger.info("检测到MonkeyLog被屏蔽,正在打开")
            self.sinOutResult.emit(200, "检测到MonkeyLog被屏蔽,正在打开")
            self.shellCmd("shell setprop debug.tct.enable_monkey_log True")
        allGrantCmd = self.shellCmd("shell monkey -c android.intent.category.LAUNCHER -v -v -v 0")
        fileName = "%s_allPkgWithActivity.txt" % self.dev
        if allGrantCmd:
            rePkg = re.findall("from\spackage\s*" + "(.*?)" + "\\)", allGrantCmd)
            if rePkg:
                with open(fileName, "w") as f:
                    for i in rePkg:
                        f.write(i+"\n")
        if os.path.isfile("./%s"% fileName):
            os.system("notepad.exe ./%s"% fileName)
        self.sinOutResult.emit(200, "完成")

    def getCurrentPNG(self):
        self.shellCmd("exec-out screencap -p > %s.png"% self.dev)
        from PIL import Image
        img = Image.open("%s.png"% self.dev)
        img.show()

    def getDevInfo(self):
        devFingerPrint = self.shellCmd("shell getprop ro.build.fingerprint")
        cpu = self.shellCmd("shell getprop ro.board.platform.cpu.type")
        if cpu:
            self.sinOutResult.emit(200, "%s\n%s" % (devFingerPrint, cpu))
        else:
            self.sinOutResult.emit(200, "%s\n" % (devFingerPrint))

    def screenSize(self):
        screenSiize = self.shellCmd("shell wm size")
        logger.info(screenSiize)
        self.sinOutResult.emit(200, "%s" % (screenSiize))

    def killAdb_progress(self, pidID):
        if pidID:
            global adb_pid
            logger.info("Kill {}".format(pidID))
            os.popen('taskkill.exe /F /pid:'+str(pidID))
            adb_pid = ""
            return adb_pid
        else:
            return "No need to kill"

    def getCoo(self):
        cmd_ = "%s -s %s shell getevent" % (adb_progress, self.dev)
        self.working = True
        proc_getcoo = subprocess.Popen(cmd_, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        global adb_pid
        adb_pid = proc_getcoo.pid
        logger.info("currentPid:{}".format(adb_pid))
        dev_x = ""
        dev_y = ""
        while adb_pid:
            relinex = ""
            reliney = ""
            for i in range(4):
                line = proc_getcoo.stdout.readline().strip()
                if "0035" in line:
                    relinex = line
                elif "0036" in line:
                    reliney = line
            if relinex:
                dev_x = re.findall("0035\s" + "00000(.+)", relinex)
            if reliney:
                dev_y = re.findall("0036\s" + "00000(.+)", reliney)
            if dev_x and dev_y:
                xx = int(dev_x[0], 16)
                yy = int(dev_y[0], 16)
                xNy = str(xx) + "," + str(yy)
                self.sinOutResult.emit(200, "%s" % xNy)

    def getBrightness(self):
        bri_num = self.shellCmd("shell settings get system screen_brightness")
        self.sinOutResult.emit(300, bri_num)

    def setBrightness(self):
        if self.args:
            bri_num = self.args[0]
            self.shellCmd("shell settings put system screen_brightness %s" % bri_num)

    def getNowpkg(self):
        nowPkg = self.shellCmd("shell \"dumpsys activity top | grep ACTIVITY | awk 'END{print $2}'\"")
        if nowPkg:
            if "\n" in nowPkg:
                nowPkg = nowPkg.replace("\n", "")
            if "/" in nowPkg:
                pkg_ = nowPkg.split("/")[0]
                pkg_version = self.shellCmd("shell \"pm dump %s | grep versionName | sed 's/[ ]//g'\"" % pkg_)
                if pkg_version:
                    self.sinOutResult.emit(400, nowPkg+"\n"+pkg_version)
                    return
            self.sinOutResult.emit(400, nowPkg)

    def run(self):
        if adb_pid:
            self.killAdb_progress(adb_pid)
        if self.testType == "getDevInfo":
            self.getDevInfo()
        elif self.testType == "getCoordinate":
            self.getCoo()
        elif self.testType == "getScreenSize":
            self.screenSize()
        elif self.testType == "getBrightness":
            self.getBrightness()
        elif self.testType == "setBrightness":
            self.setBrightness()
        elif self.testType == "killAdb":
            if adb_pid:
                self.killAdb_progress(adb_pid)
        elif self.testType == "GetNokPkg":
            self.getNowpkg()
        elif self.testType == "getCurrentPNG":
            self.getCurrentPNG()
        elif self.testType == "getAllPKG":
            self.getAllPKG()


if __name__ == '__main__':
    # a = ToolsThread
    pass
