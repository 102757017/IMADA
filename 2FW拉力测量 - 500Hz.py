#!/usr/bin/python
# -*- coding: UTF-8 -*-
from PyQt5 import  QtWidgets
import sys
from PyQt5.uic import loadUi
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np
import serial
import time
from getports import main
from types import MethodType

import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from assy import gen_K
    

#创建一个matplotlib图形绘制类
class MyFigure(FigureCanvas):
    def __init__(self,width=5, height=4, dpi=100):
        #第一步：创建一个创建Figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        #第二步：在父类中激活Figure窗口
        super(MyFigure,self).__init__(self.fig) #此句必不可少，否则不能显示图形
        #第三步：创建一个子图，用于绘制图形用，111表示子图编号，如matlab的subplot(1,1,1)
        self.axes = self.fig.add_subplot(111)
        #设置子图纵坐标范围
        self.axes.set_ylim(0, 100) 
        #第四步：就是画图，【可以在此类中画，也可以在其它类中画】
    def plotwave(self,data):
        n=len(data)
        force=np.zeros((n), dtype=float)
        for index, item in enumerate(data):
            force[index]=float(item)
        force=abs(force)
        n=gen_K(force)
        self.axes.plot(force,label="Force")
        if n[4]==1:
            #添加垂直直线
            self.axes.axvline(x=n[0],ls="-",c="green")
            self.axes.axvline(x=n[1],ls="-",c="green")
            self.axes.axvline(x=n[2],ls="-",c="green")
            self.axes.axvline(x=n[3],ls="-",c="green")
            #添加X坐标注释
            self.axes.annotate(str(n[0]), xy=(n[0], 0), xytext=(n[0], 100))
            self.axes.annotate(str(n[1]), xy=(n[1], 0), xytext=(n[1], 100))
            self.axes.annotate(str(n[2]), xy=(n[2], 0), xytext=(n[2], 100))
            self.axes.annotate(str(n[3]), xy=(n[3], 0), xytext=(n[3], 100))
            
            #arrowprops 箭头参数,参数类型为字典dict。shrink：总长度的一部分，从两端“收缩”facecolor：箭头颜色
            self.axes.annotate('min:'+str(n[5][1]), xy=n[5], xytext=(n[5][0],5),arrowprops=dict(facecolor='black', shrink=0.001))
            self.axes.annotate('min:'+str(n[6][1]), xy=n[6], xytext=(n[6][0],8.5),arrowprops=dict(facecolor='black', shrink=0.01))
            self.axes.annotate('min:'+str(n[7][1]), xy=n[7], xytext=(n[7][0],10),arrowprops=dict(facecolor='black', shrink=0.01))
            self.axes.annotate('max:'+str(n[8][1]), xy=n[8], xytext=(n[8][0],65),arrowprops=dict(facecolor='black', shrink=0.05))
            self.axes.annotate('max:'+str(n[9][1]), xy=n[9], xytext=(n[9][0],60),arrowprops=dict(facecolor='black', shrink=0.05))
            self.axes.annotate('max:'+str(n[10][1]), xy=n[10], xytext=(n[10][0],55),arrowprops=dict(facecolor='black', shrink=0.05))       


# 由于pyqt的主进程是UI进程，主进程中使用循环语句，会导致进程阻塞，UI界面会卡死，因此必须将耗时的作业放在子进程内操作，因此使用QThread创建子进程
class MyThread(QThread):
    # 创建一个信号，该信号会传递一个str类型的参数给槽函数
    finish = pyqtSignal(list)

    def __init__(self, parent=None):
        # super主要来调用父类方法来显示调用父类,要将子类Child和self传递进去
        # 首先找到MyThread的父类（QThread），然后把类MyThread的对象self转换为类QThread的对象，然后“被转换”的QThread对象调用自己的__init__函数
        super(MyThread, self).__init__(parent)

        # 设置标志位，用来中断子进程内的循环语句
        self.flag = True

    def set_flag_true(self):
        self.flag = True

    def set_flag_false(self):
        self.flag = False

    # 重写QThread的run函数，将子进程要执行的操作放在此函数内，线程的start方法会执行run函数
    def run(self):
        t = time.time()
        now = time.strftime("%Y-%m-%d %H_%M_%S", time.localtime(time.time()))
        fname = now + r"data.txt"
        f = open(fname, 'w')  # 覆盖模式
        data=[]
        rec_err=0
        self.ser.flushInput()
        self.ser.write(b"XFU2\r")
        while self.flag:
            #print("正在执行")
            try:
                self.ser.write(b"XAR\r")
                time.sleep(0.002)
                rec=self.ser.read(21)
                self.ser.flushInput()
                if len(rec)<21:
                    rec_err+=1
                else:
                    F = float(rec.decode("GBK")[1:7]) * 4.448
                    #print(F)
                    data.append(F)
            except BaseException as e:
                print("产生错误：",e)
                print(rec.decode("GBK"))
        
        self.ser.write(b"XFU0\r")
        f.write(str(data[1:]))
        f.close()
        
        # 发射信号，传递时间参数
        self.finish.emit(data)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        loadUi('form1.ui', self)

        #建立画板
        self.graphicsView.scene = QGraphicsScene(self)
        self.graphicsView.setScene(self.graphicsView.scene)
        self.graphicsView.draw=""
        self.graphicsView.flag=False

        #创建一个线程
        self.thread=MyThread()
        #连接子进程内的信号与槽函数，该槽函数用来跟新button的显示值
        self.thread.finish.connect(self.draw)

        # 数据采集按钮
        self.pushButton.setEnabled(False)
        self.pushButton.clicked.connect(self.show_table)

        # 停止采集按钮
        self.pushButton_3.setEnabled(False)
        self.pushButton_3.clicked.connect(self.stop)

        #建立串口连接
        self.pushButton_2.clicked.connect(self.conect_com)

        # 重写showPopup函数
        def showPopup(self):
            # 先清空原有的选项
            self.clear()
            items_list = main()
            self.addItems(items_list)
            QtWidgets.QComboBox.showPopup(self)  # 弹出选项框

        #使用MethodType将函数转换为方法，再绑定到实例上去
        self.comboBox.showPopup=MethodType(showPopup, self.comboBox)


    # 定义槽函数
    def show_table(self):
        self.pushButton.setEnabled(False)
        self.pushButton_3.setEnabled(True)
        self.thread.set_flag_true()
        self.thread.start()


    def stop(self):
        self.thread.set_flag_false()
        self.pushButton.setEnabled(True)

    def draw(self,data):
        #设置图形的大小
        self.F = MyFigure(width=15, height=5, dpi=100)
        self.F.plotwave(data[1:])
        # 将图形元素添加到场景中
        self.graphicsView.scene.addWidget(self.F)
        self.graphicsView.show()





    # 定义槽函数
    def conect_com(self):
        COM_No=self.comboBox.currentText()
        
        #实例化串口号、波特率、等待时间
        #timeout=None 永远等待，直到有数据传过来（阻塞）  
        #timeout=0 不等待，收不到数据直接退出读取（非阻塞）
        try:
            self.thread.ser=serial.Serial(COM_No,19200,timeout=1,bytesize=8,stopbits=1,parity=serial.PARITY_NONE)
        except ValueError as e:
            print('串口连接错误:', e)
        
        #判断串口是否打开
        if self.thread.ser.isOpen():
            self.label_3.setText("串口已连接OK")
            self.pushButton_2.setEnabled(False)
            self.pushButton.setEnabled(True)
        else:
            self.label_3.setText("串口未连接")



if __name__ == "__main__":
    # 创建了一个PyQt封装的QApplication对象,创建的时候,把系统参数传进去了.顾名思义,这一句创建了一个应用程序对象
    app = QtWidgets.QApplication(sys.argv)
    # #创建一个我们生成的那个窗口，注意把类名修改为MainWindow
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
