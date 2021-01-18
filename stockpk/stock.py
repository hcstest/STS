# -*- coding:utf-8 -*-
# Author:clare

import sys
import os
sys.path.append("..")
import config
import stockpk.url_helper
import random
import matplotlib.pyplot as plt
import csv
import numpy
import pymysql

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

# MY_FONT=font_manager.FontProperties(fname="C:/Windows/Fonts/simsunb.ttf")


class Stock(object):

    def __init__(self, name = 'test',id=0):
        self.id = id
        self.name = name
        self.day=0
        self.daysList=[]
        self.method = self.get_method()
        self.priceChanged = self.get_changed_price()
        self.priceInit = self.get_init_price()
        self.price = 0
        self.priceList=[]
        if self.daysList!=[]:
            del (self.daysList[0])

    def get_method(self):
        # 股票有两种获取方式， 模拟和online获取。 每只股票定义的时候， 需要选一种获取方式。
        str0="对于股票"
        str1="""
        输入1或2来选择股票价格获取方式: 
            1: 随机数模拟股票变动
            2: 网络爬取历史股票信息
        """
        print(str0, self.name, str1)
        str2 = input("请选择方式: ")
        return str(str2)

    def get_stock_name(self):
        # 用于通过股票ID 获取股票名字, 主要针对online获取股票方法。
        if self.method == "1":
            return self.name
        else:
            if self.id==0:
                print("当前只支持按照股票代码搜索")
                exit(1)
            id=self.id
            name=stockpk.url_helper.StockUrl.get_stack_name(id)
            return name

    def get_stock_id(self):
        # 用于通过股票名字，获取股票ID， 主要针对模拟股票方法。
        if self.method == "1":
            print('未定以股票ID，以股票名字代替')
            return self.name
        else:
            return self.id

    def get_init_price(self):
        #获取初始股价, 仅用于method 1 模拟股票
        if self.method == "1":
            initPrice = config.STOCK_INIT_S
            return initPrice
        else:
            print("网络获取股票价格没有初始估价")
            return

    def _get_random_number(self):
        # 只用于method 1  随机数变动的股价方式
        # 变动数据为 config文件中的 RANDOM_PRICE_RANGE=10  #股票价格变动区间：+/- 10%   百分比
        # 为了提高精度， 要精确到小数后2位， 所以先加100倍产生随机数再除100 来产生小数
        rangeMin = ~config.RANDOM_PRICE_RANGE + 1
        rangeMax = config.RANDOM_PRICE_RANGE
        randomNum = random.randint(rangeMin *100, rangeMax*100)  # 随机函数返回数字 N ，N 为 a 到 b 之间的数字（a <= N <= b），包含 a 和 b
        return randomNum/100

    def get_changed_price(self):
        #获取股价变动额， 仅用于method 1 模拟股票
        if self.method == "1":
            changedNum = self.get_init_price() * self._get_random_number() / 100
#            print('changed num', changedNum)
            self.daysList.append(f"{self.day}日")
            print(self.name, self.day, '日股价变化为', changedNum)
            print('当前股价变化时间列表为',self.daysList)
            self.day+=1
            return round(changedNum,2)
        else:
            print("网络获取股票价格不需要单独计算变动额")
            return

    def get_changed_price_percent(self):
        # 获取股价随机变动百分比， 仅用于method 1 模拟股票
        if self.method == "1":
            # 只用于method 1  随机数变动的股价方式, _get_random_number()获取的随机变动数就是变动百分比
            # 每次使用_get_random_number()，数值都会变动， 所以 method 1 中的 self.get_changed_price_percent(self)的值不一定等于self.get_changed_price(self)/self.get_init_price(self) *100的值
            changePercent = self._get_random_number()
            print(self.name, '股价变化百分比为',changePercent,'%' )
            return changePercent
        else:
            print("网络获取股票价格不需要单独计算变动百分比， 因为可以直接获取")
            return

    def get_price_after_changed(self):
        #获取变动后的价格, 仅用于method 1 模拟股票
        if self.method == "1":
           price=self.get_init_price()+self.get_changed_price()
           print(self.name,'当前股价是',price)
           #self.priceList.append(price)
#           print('股价变化列表为',self.priceList)
           return price
        else:
            print("网络获取股票价格不需要单独获取价格")

    def get_price_list(self):
        # 用于两种股票方法的, 来获取股价列表
        list=[]
        n=1
        if self.method == "1":
            while n >= 1 and n <= config.MAX_DAYS:
                list.append(self.get_price_after_changed())
                n += 1
        else:
            stockFile = os.path.join(stockpk.url_helper.DATA_PATH, f'{self.id}.csv')
            if os.path.exists(stockFile):
                print("股票id",self.id,"的csv文件已下载,此次直接使用")
            else:
                stockFile = stockpk.url_helper.StockUrl.get_stock_csv(self.id)
            with open(stockFile, 'r') as f:
                reader = csv.reader(f)
                for i in reader:
                    n += 1
                    if n > 2 and n <= config.MAX_DAYS+1:
                        price0 = i[3]
                        price1 = float(price0)
                        if price1>1000:
                            price1=price1/100
                        price = round(price1, 2)
                        list.append(price)
        print(list)
        return list

    def get_price_changed_percent_list(self):
        # 用于两种股票方法的, 来获取股价变化百分比列表
        # 对于method1, 此方法和get_price_list() 因为都用到_get_random_number, 每次随机值不一样，所以方法二选一。
        percentList=[]
        priceList=self.get_price_list()
        i=0
        while i<len(priceList)-1:
            change=round((priceList[i+1]-priceList[i]),2)
            change_persent=round(change/priceList[i] *100,2) #百分比num
            # print(i,change,priceList[i],change_persent)
            percentList.append(change_persent)
            i+=1
        # print(percentList)
        return percentList

    def get_days_list(self):
        # 用于两种股票方法的, 来获取股价变化日期的列表
        list = []
        n=1
        if self.method == "1":
            while n >= 1 and n <= config.MAX_DAYS:
                day=f'第{n}天'
                list.append(day)
                n += 1
        else:
            stockFile = os.path.join(stockpk.url_helper.DATA_PATH, f'{self.id}.csv')
            if os.path.exists(stockFile):
                print("股票id",self.id,"的csv文件已下载,此次直接使用")
            else:
                stockFile = stockpk.url_helper.StockUrl.get_stock_csv(self.id)
            with open(stockFile, 'r') as f:
                reader = csv.reader(f)
                for i in reader:
                    n+=1
                    if n > 2 and n <= config.MAX_DAYS+1:
                        day=i[0]
                        list.append(day)
        print(list)
        return list

    def get_graphic_trend(self):
        #用于两种股票方法的,获取股票价格变化趋势图, X横坐标为股票变化次数/变化时间， 纵坐标为股票价格
        name=self.get_stock_name()
        print(name)
        plt.title=f"股票{name}的价格变化趋势图"  #设置表格标题
        x=self.get_days_list()[::-1]
        y=self.get_price_list()[::-1]
        yMax=int(max(y))+1 #纵坐标最大值取股票最大值加1
        yMin=int(min(y)) #纵坐标最小值去股票最小值-1
        plt.figure(figsize=(16,4),dpi=80) #figure 函数创建图标 # pyplot .figure(figsize(横坐标，纵坐标),dpi) 设 置图片大小和分辨率(dpi)
        # plt.figure(figsize=(days, size))
        plt.plot(x,y,label=name) #绘制折线图 plt.plot(x,y,lable), 横纵坐标的list 和 名称
        # plt.xlabel(u'股票价格变化日期', fontproperties=myfont)  # 这一段
        plt.xlabel(u'股票价格变化日期')
        # plt.ylabel(u'股票价格', fontproperties=myfont)  # 这一段
        plt.ylabel(u'股票价格')
#        plt.plot(x,y)
        plt.xticks(x, x) #设置了x轴上的刻度list(x)和字符串(lables) 横坐标值的显示名字, 两者元素个数应一致
        l = len(range(yMin, yMax))
        print(name,'price len',l)
        if l>10 and l <1000 :
            plt.yticks(numpy.arange(yMin, yMax, (yMax - yMin) // 10))
        elif l>1000:
            plt.yticks(numpy.arange(yMin, yMax, (yMax - yMin) // 30))
        elif l<= 2:
            plt.yticks(numpy.arange(min(y) - 0.01, max(y) + 0.01, 0.05))
        else:
            plt.yticks(range(yMin, yMax))
        # 绘制网格, alpha 设置网格透明度
        plt.grid(alpha=0.1)
        # 添加图例的放置位置
        #plt.legend(prop=MY_FONT, loc='upper left')
        plt.legend(loc='upper left')
        # 展示
        plt.show()

    def get_downloaded_csv_stock_id(self):
        #用于两种股票方法的, 获取已下载的股票csv文件的所有股票ID 列表, 此方法仅用于save_all_stocks_in_db（）
        tablenames=[]
        if self.method == "1":
            pass
        else:
            contents=os.walk(stockpk.url_helper.DATA_PATH)
            for root, dirs, files in contents:
                for name in files:
                    if name.endswith('csv'):
                        stockid=name.split('.')[0]
                        tablenames.append(stockid)
        return tablenames

    def save_all_stocks_in_db(self):
        # 用于把所有股票信息存储到数据库。 目前仅提供此方法接口， 本次练习可能不需要
        if self.method == "1":
            pass
        else:
            for tbname0 in self.get_downloaded_csv_stock_id():
                tbname='t'+ tbname0  #DB TABLE 名字不能是纯数字
                stockpk.url_helper.StockUrl.create_dbtable(tbname)
                # 连接本地数据库
                myDB = pymysql.connect(host=config.DB_ADDR, user=config.USER_NAME, password=config.USER_PASSWORD,database=config.DB_NAME)
                # 获取游标
                myCursor = myDB.cursor()
                stockFile=os.path.join(stockpk.url_helper.DATA_PATH, f'{tbname0}.csv')
                print(stockFile)
                with open(stockFile, 'r') as f:
                    reader = csv.reader(f)
                    n=0
                    for i in reader:
                        if n>=1 and n < config.MAX_DAYS:  #从CSV第二行还是插入数据
                            date = i[0]
                            id = i[1].replace('\'','')
                            name=i[2]
                            price=i[3]
                            price_changed_percent=i[8]
                            sql = "insert into %s values(\'%s\', \'%s\', %s, %s, \'%s\')" % (pymysql.escape_string(tbname), str(id), str(name), price, price_changed_percent, str(date))  #注意插入char要加''
                            # print(sql)
                            try:
                                myCursor.execute(sql)
                                #myCursor.execute("insert into t000034 values ('000034','上证工业',934.373,-5.546,'2005-01-06')")
                                myDB.commit()
                                # print('添加成功--------------------------------------------------')
                            except Exception as e:
                                print("插入失败：case%s" % e)
                                # exit(1)
                        n+=1
                myDB.close()
                f.close()

    def save_current_stock_in_db(self):
        # 用于把当前实例的股票信息存储到数据库。 目前仅提供此方法接口， 本次练习可能不需要
        if self.method == "1":
            pass
        else:
            tbname = 't' + self.id # DB TABLE 名字不能是纯数字
            stockpk.url_helper.StockUrl.create_dbtable(tbname)
            # 连接本地数据库
            myDB = pymysql.connect(host=config.DB_ADDR, user=config.USER_NAME, password=config.USER_PASSWORD,
                                   database=config.DB_NAME)
            # 获取游标
            myCursor = myDB.cursor()
            stockFile = os.path.join(stockpk.url_helper.DATA_PATH, f'{self.id}.csv')
            print(stockFile)
            with open(stockFile, 'r') as f:
                reader = csv.reader(f)
                n = 0
                for i in reader:
                    if n >= 1 and n < config.MAX_DAYS:  # 从CSV第二行还是插入数据
                        date = i[0]
                        id = i[1].replace('\'', '')
                        name = i[2]
                        price = i[3]
                        price_changed_percent = i[8]
                        sql = "insert into %s values(\'%s\', \'%s\', %s, %s, \'%s\')" % (
                        pymysql.escape_string(tbname), str(id), str(name), price, price_changed_percent,
                        str(date))  # 注意插入char要加''
                        # print(sql)
                        try:
                            myCursor.execute(sql)
                            # myCursor.execute("insert into t000034 values ('000034','上证工业',934.373,-5.546,'2005-01-06')")
                            myDB.commit()
                            # print('插入信息成功')
                        except Exception as e:
                            print("插入失败：case%s" % e)
                            # exit(1)
                    n += 1
                print('插入信息完成到table',tbname,'完成')
                myDB.close()
                f.close()


    def get_stock_info_from_db(self):
        # 用于从数据库读取当前实例的股票信息。 目前仅提供此方法接口， 本次练习可能不需要
        # 连接本地数据库
        myDB = pymysql.connect(host=config.DB_ADDR, user=config.USER_NAME, password=config.USER_PASSWORD, database=config.DB_NAME)
        # 获取游标
        myCursor = myDB.cursor()
        tbname='t'+ self.id
        sql="select * from %s" % tbname
        print(repr(sql))
        try:
            # 执行SQL语句
            myCursor.execute(sql)
            # 获取所有记录列表
            results = myCursor.fetchall()
            print(results)
            for row in results:
                date = row[0]
                id = row[1]
                name = row[2]
                price = row[3]
                price_changed_percent = row[4]
                # 打印结果
                print("date=%s,id=%s,name=%s,price=%s,price_changed_percent=%s" % (date, id, name, price, price_changed_percent))
            return results
        except Exception as e:
            print("查询出现问题")
            exit(1)
        myDB.close()


#使用举例
if __name__ == "__main__":
    stk = Stock(id='601857')
    # stk2 = Stock(id='000034')
    # stk.save_current_stock_in_db()
    # stk.get_stock_info_from_db()
    # stk.get_price_changed_percent_list()

    # name=stk.get_stock_name()
    # print(name)

#单个股票趋势图
#     stk = Stock("我的")
#     stk2= Stock("你的")
#     a=20
#     while a > 0:
#         stk_price=stk.get_price_after_changed()
#        stk2_price = stk2.get_price_after_changed()
#        print(stk.priceList)
        # n=stk2.get_changed_price()
        # print(m,n)

    # stk_price=stk.get_price_list()
    # stk_days=stk.get_days_list()
    stk.get_graphic_trend()
    # stk2.get_graphic_trend()

#online





