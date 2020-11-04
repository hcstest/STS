# -*- coding:utf-8 -*-
# Author:clare

import requests
from lxml import etree
import urllib
import re
import config
import os
import pymysql
import threading
import time
from functools import wraps

def fn_timer(function):
    #函数运行时间装饰器
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("运行耗时 %s: %s seconds" %(function.__name__, str(t1-t0)))
        return result
    return function_timer

CURRENT_PATH=os.getcwd()
DATA_PATH=os.path.join(CURRENT_PATH,f"../data/")

class StockUrl(object):
    def get_html(url=""):
        #获取网页内容的方法
        if url =="":
            url=config.STOCK_URL
        html = urllib.request.urlopen(url).read()
        html = html.decode('gbk')
        with open(os.path.join(DATA_PATH,"stock.txt"), "w") as f:
            f.seek(0)
            f.truncate()
            f.close()
        with open(os.path.join(DATA_PATH,"stock.txt"), "a",encoding="utf-8") as f:
            f.write(html)
            f.close()
        return html
    #
    # def get_htmls(url=""):
        #获取全部股票ID 和股票名字的一种方法。 当前练习不需要这个方法。
    #     pages_conents=""
    #     p=1
    #     with open(os.path.join(DATA_PATH,"stock.txt"), "w") as f:
    #         f.seek(0)
    #         f.truncate()
    #         f.close()
    #     while p<10:
    #         url=f"https://quote.stockstar.com/BillBoard/stockstatistic_1_1_1_{p}.html"
    #         print(url)
    #         html = urllib.request.urlopen(url).read()
    #         html = html.decode('gbk')
    #         pages_conents=pages_conents+html
    #         with open(os.path.join(DATA_PATH,"stock.txt"), "a") as f:
    #             f.write(html)
    #             f.close()
    #         p += 1
    #     return pages_conents

    # def get_stack_code_list(html):
    #     s=r'<a href="//stock.quote.stockstar.com/([0-9]{6}).shtml">([0-9]{6})</a>'
    #     pat=re.compile(s)
    #     code=pat.findall(html)
    #     result = [i[0] for i in code]
    #     print(result)
    #     return result
    #
    # def getStackID(name):
    #     pass

    def get_stock_detail_url(id):
        # 仅用于辅助 get_stack_name 方法。
        url = f'http://data.eastmoney.com/zjlx/{id}.html'
        return url

    def get_txt_by_xpath(url,x):
        # 仅用于辅助 get_stack_name 方法。
        print(url)
        # x is xpath address
        r = requests.get(url)
        content = etree.HTML(r.content)
        xpathText=x+r"/text()"
        output=content.xpath(xpathText)[0]
        # print(repr(output))
        #output=output.replace('\n', '').replace('\r', '').replace(' ','') #去除回车和空格
        return output

    def get_stack_name(id):
        # 从网络根据ID 获取股票名字的一种方法， 主要练习xpath使用。
        url=StockUrl.get_stock_detail_url(id)
        name=StockUrl.get_txt_by_xpath(url,'/html/body/div[2]/div[2]/div[2]/div[2]/div/div[1]/div[1]/div[1]/a').replace('\n', '').replace('\r', '').replace(' ','') #去除回车和空格
        return name

    def get_stock_csv(id):
        # 从网络获取历史价格的方法一, csv 文件下载和信息提取
        print("准备下载股票id",id,"的csv")
        url = f'http://quotes.money.163.com/service/chddata.html?code=0{id}&end=20201029&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP'
        stockFile = os.path.join(DATA_PATH, f'{id}.csv')
        try:
            urllib.request.urlretrieve(url, os.path.join(DATA_PATH, f'{id}.csv'))
            print("文件", stockFile, "下载成功")
        except PermissionError:
            print("csv文件已被打开，本次未重新下载, 如有需要请关闭文件后重新执行")
        return stockFile

    @fn_timer  #装饰器计算函数运行时间
    def get_stocks_csv_multi_thread(ids):
        #从网络获取历史价格的方法拓展: 多线程同时下载多个csv
        threads = []
        for id in ids:
            threads.append(threading.Thread(target=StockUrl.get_stock_csv,args = (id,)))
        for t in threads:
            t.setDaemon(True)  #将线程搞成 守护线程, 主线程退出时， 子线程也退出
            t.start()
        for t in threads:
            t.join()   #主线程一直等待全部的子线程结束之后，主线程自身才结束，程序退出

    def get_stock_price_history_online(id):
        # 从网络获取历史价格的方法二, API 直接get 有效网页header 来获取信息。
        url=f'http://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?lmt=0&klt=101&secid=0.{id}&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65&ut=b2884a393a59ad64002292a3e90d46a5&cb=jQuery183006391378028092931_1604385820004&_=1604385822616'
        output=requests.get(url)
        contents=output.text
        print(contents)
        pattern = re.compile(r'\[(.*)+\]')
        #str = u'contents'
        result=pattern.search(contents)
        print(result.group())
        return result.group()
        '''output is like ["2020-06-03,-57970261.0,40105996.0,17864264.0,-29893664.0,-28076597.0,-15.21,10.53,4.69,-7.85,-7.37,23.99,-1.40,0.00,0.00","2020-06-04,-100245508.0,65301052.0,34944457.0,-43919942.0,-56325566.0,-25.57,16.66,8.91,-11.20,-14.37,23.25,-3.08,0.00,0.00"...]
        #usage example:  
        list[i].split(',') to get  one date info, like  ['2020-06-03', '-57970261.0', '40105996.0', '17864264.0', '-29893664.0', '-28076597.0', '-15.21', '10.53', '4.69', '-7.85', '-7.37', '23.99', '-1.40', '0.00', '0.00']
        list[i].split(',')[0] for date, list[i].split(',')[11] for price, list[i].split(',')[12] for price changed percent.  
        '''

    def create_db():
        # 存储和提取股票信息的方法二： 数据库处理。 方法一是直接存储在列表里。
        # 打开数据库连接，不需要指定数据库，因为需要创建数据库
        myDB = pymysql.connect(host=config.DB_ADDR, user=config.USER_NAME, password=config.USER_PASSWORD)
        # 获取游标
        myCursor = myDB.cursor()
        # 创建pythonBD数据库
        sql = 'CREATE DATABASE IF NOT EXISTS %s' % config.DB_NAME
        myCursor.execute(sql)
        myCursor.close()  # 先关闭游标
        myDB.close()  # 再关闭数据库连接
        print('创建',config.DB_NAME,'数据库成功')

    def create_dbtable(tbname):
        # 连接本地数据库
        StockUrl.create_db()
        myDB = pymysql.connect(host=config.DB_ADDR, user=config.USER_NAME, password=config.USER_PASSWORD, database=config.DB_NAME)
        # 获取游标
        myCursor = myDB.cursor()
        # 如果存在stock表，则删除
        sql1="DROP TABLE IF EXISTS %s" % pymysql.escape_string(tbname) #pymysql.escape_string 去掉引号  table 名字不能是纯数字
        print(repr(sql1))
        try:
            myCursor.execute(sql1)
        except Exception as e:
            print("创建数据库失败：case%s" % e)
        # 创建表
        sql = """
                create table %s(
                id char(20) not null,
                name char(20),
                price FLOAT ,
                priceChangedPercent FLOAT ,
                date char(20))
            """ % pymysql.escape_string(tbname)
        print(repr(sql))
        try:
            # 执行SQL语句
            myCursor.execute(sql)
            print("创建Table",pymysql.escape_string(tbname),"成功")
        except Exception as e:
            print("创建table失败：case%s" % e)
        finally:
            # 关闭游标连接
            myCursor.close()
            # 关闭数据库连接
            myDB.close()


#使用举例
if __name__ == "__main__":
#     StockUrl.get_stock_csv("000034")
#     StockUrl.get_html("http://data.eastmoney.com/zjlx/000034.html")
# #     # StockUrl.getStackCode(html)
#     StockUrl.get_stack_name('000034')
#     name_xpath=f'/html/body/div[2]/div[2]/div[2]/div[2]/div/div[1]/div[1]/div[1]/a'
#     day_xpath = f'/html/body/div[2]/div[2]/div[2]/div[2]/div/div[7]/div[2]/table/tbody/tr[1]/td[1]'
#     price_xpath = f'/html/body/div[2]/div[2]/div[2]/div[2]/div/div[7]/div[2]/table/tbody/tr[1]/td[2]/span'
#     price = StockUrl.get_txt_by_xpath(StockUrl.get_stock_detail_url('000034'), price_xpath)
#     days = StockUrl.get_txt_by_xpath(StockUrl.get_stock_detail_url('000034'), day_xpath)
#     name=StockUrl.get_txt_by_xpath(StockUrl.get_stock_detail_url('000034'), name_xpath)
#    StockUrl.getNumberbyXpath('000034')
#     StockUrl.get_stock_price_history_online("000034")
    StockUrl.get_stocks_csv_multi_thread(["000034","000035","000036"])