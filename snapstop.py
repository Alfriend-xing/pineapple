#coding=utf-8

#查找并关闭python进程和chrome进程

import os
import psutil

#获取当前工作目录
# print(os.getcwd())
for i in psutil.pids():
    try:
        pro=psutil.Process(i)
        if 'python' in pro.name() and os.getcwd() in pro.exe() and len(pro.children(recursive = True))>0:
            print(pro.name(),'+',pro.exe())
            print(pro.children(recursive = True))
            pch=pro.children(recursive = True)
            for p in pch:
                p.terminate()
            pro.terminate()
        # if 'chromed' in pro.name():
        #     print(pro.name(),'+',pro.exe())
        #     print(pro.children(recursive = True))
        # elif 'chrome' in pro.name():
        #     print(pro.name(),'+',pro.exe())
    except:
        pass


