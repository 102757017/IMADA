# -*- coding: UTF-8 -*- 
import os
import sys
import matplotlib.pyplot as plt
import math
import numpy as np
#解决中文乱码问题
from matplotlib.font_manager import FontProperties 
font_set = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=10)


def gen_K(data):
     data=np.around(data, decimals=1)
     n1=0
     n2=0
     n3=0
     n4=0
     min1=min2=min3=max1=max2=max3=0
     flag=0
     for index, item in enumerate(data):
          if abs(item)>5:
               n1=index+11
               break
     if n1+1000<len(data):
          for index, item in enumerate(data[n1+1000:]):
               if abs(item)>80:
                    n4=index-17+n1+1000
                    break          
          n2=n1+int((n4-n1)/12)
          n3=n4-int((n4-n1)/12)
          if n1!=0 and n2!=0 and n3!=0 and n4!=0:
               y1_max=np.max(data[n1:n2])
               y1_min=np.min(data[n1:n2])
               y2_max=np.max(data[n2:n3])
               y2_min=np.min(data[n2:n3])
               y3_max=np.max(data[n3:n4])
               y3_min=np.min(data[n3:n4])

          
               x1_max=np.where(data[n1:n2]==y1_max)[0][0]+n1
               x1_min=np.where(data[n1:n2]==y1_min)[0][0]+n1
               x2_max=np.where(data[n2:n3]==y2_max)[0][0]+n2
               x2_min=np.where(data[n2:n3]==y2_min)[0][0]+n2
               x3_max=np.where(data[n3:n4]==y3_max)[0][0]+n3
               x3_min=np.where(data[n3:n4]==y3_min)[0][0]+n3


               max1=(x1_max,y1_max)
               max2=(x2_max,y2_max)
               max3=(x3_max,y3_max)
               min1=(x1_min,y1_min)
               min2=(x2_min,y2_min)
               min3=(x3_min,y3_min)
          
               print("起始20mm最大值：", y1_max)
               print("起始20mm最小值：", y1_min)
               print("中间200mm最大值：", y2_max)
               print("中间200mm最小值：", y2_min)
               print("结束20mm最大值：", y3_max)
               print("结束20mm最小值：", y3_min)
               flag=1
          else:
               print("未采集到全行程的拉力数据，请重新测量")
               flag=0
     else:
          print("未采集到全行程的拉力数据，请重新测量")
          flag=0
     return n1,n2,n3,n4,flag,min1,min2,min3,max1,max2,max3

if __name__=="__main__":
     f = open(r"2019-11-02 17_20_51data.txt",'r') # 读模式
     # 一次读取整个文件
     data=f.read()
     data=data[1:-1].split(',')
     n=len(data)
     force=np.zeros((n), dtype=float)
     for index, item in enumerate(data):
          force[index]=float(item)
     f.close()
     force=abs(force)

     
     n=gen_K(force)
     # 生成画布
     fig=plt.figure(figsize=(5, 4), dpi=100)
     axes0 = fig.add_subplot(111)
     #设置子图纵坐标范围
     axes0.set_ylim(0, 100)     
     axes0.plot(force,label="Force")
     if n[4]==1:
          #添加垂直直线
          axes0.axvline(x=n[0],ls="-",c="green")
          axes0.axvline(x=n[1],ls="-",c="green")
          axes0.axvline(x=n[2],ls="-",c="green")
          axes0.axvline(x=n[3],ls="-",c="green")
          #添加X坐标注释
          plt.annotate(str(n[0]), xy=(n[0], 0), xytext=(n[0], 80))
          plt.annotate(str(n[1]), xy=(n[1], 0), xytext=(n[1], 80))
          plt.annotate(str(n[2]), xy=(n[2], 0), xytext=(n[2], 80))
          plt.annotate(str(n[3]), xy=(n[3], 0), xytext=(n[3], 80))

          #arrowprops 箭头参数,参数类型为字典dict。shrink：总长度的一部分，从两端“收缩”facecolor：箭头颜色
          plt.annotate('min:'+str(n[5][1]), xy=n[5], xytext=(n[5][0],5),arrowprops=dict(facecolor='black', shrink=0.001))
          plt.annotate('min:'+str(n[6][1]), xy=n[6], xytext=(n[6][0],8.5),arrowprops=dict(facecolor='black', shrink=0.01))
          plt.annotate('min:'+str(n[7][1]), xy=n[7], xytext=(n[7][0],10),arrowprops=dict(facecolor='black', shrink=0.01))
          plt.annotate('max:'+str(n[8][1]), xy=n[8], xytext=(n[8][0],65),arrowprops=dict(facecolor='black', shrink=0.05))
          plt.annotate('max:'+str(n[9][1]), xy=n[9], xytext=(n[9][0],60),arrowprops=dict(facecolor='black', shrink=0.05))
          plt.annotate('max:'+str(n[10][1]), xy=n[10], xytext=(n[10][0],55),arrowprops=dict(facecolor='black', shrink=0.05))

          
     plt.show()
