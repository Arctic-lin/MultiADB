# -*- coding: utf-8 -*-
# @Time    : 2020/7/18 15:45
# @Author  : Arctic
# @FileName: changeCNtoEn.py
# @Software: PyCharm
# @Purpose :

from pypinyin import lazy_pinyin
import os
import time
scr = r"D:\Chaos\MyFiles\ForLife\test"
befor = []
after = []
after_same = []

def getName(scr):
    old = []
    new = []
    new_new = []
    a=0
    if os.path.isdir(scr):
        for i in os.listdir(scr):
            old.append(i)
            i = i.replace(" ","")
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
    return old,new_new

def reName(type,src,list):
    if type == 0:
        for i in range(len(list[0])):
            os.rename(src + "\\" + list[0][i],src + "\\" + list[1][i])
    elif type == 1:
        for i in range(len(list[0])):
            os.rename(src + "\\" + list[1][i],src + "\\" + list[0][i])

b = getName(scr)
reName(scr,b)