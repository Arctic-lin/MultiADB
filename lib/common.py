# -*- coding: utf-8 -*-
# @Time    : 2020/8/4 10:43
# @Author  : Arctic
# @FileName: common.py
# @Software: PyCharm
# @Purpose :

import logging

def configLog():
    logging.basicConfig\
        (level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)
