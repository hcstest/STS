# -*- coding:utf-8 -*-
# Author:clare

import stockpk.stock
import matplotlib.pyplot as plt
import numpy
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False

class StockUsage(object):

    def compare_graphic_trend(*args):
        # 此方法用于生成几个股票同时显示在一张曲线表里的对比图。
        # 每个参数都是一个stock 实例
        yList=[]  #每个stock的y坐标股价
        nameList=[]
        stockList=[]
        idList= []
        for i in args:
            print("here is class object",i)
 #           i = stockpk.stock.Stock()
            stockList.append(i)
            nameList.append(i.get_stock_name())
            idList.append(i.get_stock_id())
        stockpk.url_helper.StockUrl.get_stocks_csv_multi_thread(idList)
        for i in args:
            y = i.get_price_list()[::-1]  # 按时间和价格的列表倒叙， 之前的日期先显示。
            print("here is Pirce list", y)
            yList.append(y)
        plt.title = f"股票的价格变化对比趋势图"  # 设置表格标题
        x = stockList[0].get_days_list()[::-1]  # 按时间和价格的列表倒叙， 之前的日期先显示。
        print("here is days list",x)
        print("here is total price list",y)
        yMax = int(max(max(yList))) + 1  # 纵坐标最大值取股票最大值加1
        yMin = int(min(min(yList)))  # 纵坐标最小值去股票最小值-1
        plt.figure(figsize=(16, 10), dpi=80)  # figure 函数创建图标 # pyplot .figure(figsize(横坐标，纵坐标),dpi) 设 置图片大小和分辨率(dpi)\
        for j in range(len(yList)):
            plt.plot(x, yList[j], label=nameList[j])  # 绘制折线图 plt.plot(x,y,lable), 横纵坐标的list 和 名称
            # plt.xlabel(u'股票价格变化日期', fontproperties=myfont)  # 这一段
        plt.xlabel(u'股票价格变化日期')
            # plt.ylabel(u'股票价格', fontproperties=myfont)  # 这一段
        plt.ylabel(u'股票价格')
        plt.xticks(x, x)  # 设置了x轴上的刻度list(x)和字符串(lables) 横坐标值的显示名字, 两者元素个数应一致
        l = len(range(yMin,yMax))
        print(l)
        if l>10 and l <1000 :
            plt.yticks(range(yMin, yMax, (yMax - yMin) // 10))
        elif l>1000:
            plt.yticks(range(yMin, yMax, (yMax - yMin) // 30))
        elif l <= 2:
            plt.yticks(numpy.arange(min(y) - 0.01, max(y) + 0.01, 0.05))
        else:
            plt.yticks(range(yMin, yMax))
        # 绘制网格, alpha 设置网格透明度
        plt.grid(alpha=0.1)
        # 添加图例的放置位置
        plt.legend(loc='upper left')
        # 展示
        plt.show()


#使用举例
if __name__ == "__main__":
    #Method 1 示例
    # a = stockpk.stock.Stock()
    # b = stockpk.stock.Stock("股票2")
    # c = stockpk.stock.Stock("股票3")
    # n = 20
    # while n > 0:
    #     a_price = a.get_price_after_changed()
    #     b_price = b.get_price_after_changed()
    #     c_price = c.get_price_after_changed()
    #     print(a_price,b_price,c_price)
    #     n=n-1
    # StockUsage.compare_graphic_trend(a,b,c)
    #Method 2 示例
    a = stockpk.stock.Stock(id='000040')
    b = stockpk.stock.Stock(id='000039')
    c = stockpk.stock.Stock(id='000043')
    d = stockpk.stock.Stock(id='000035')
    e = stockpk.stock.Stock(id='000034')
    StockUsage.compare_graphic_trend(a,b,c,d, e)
