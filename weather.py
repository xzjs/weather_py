# -*- coding:utf-8 -*-
import time
from selenium import webdriver
from pyquery import PyQuery as pq
from pymongo import MongoClient
import platform
import zmq


def spider(str):
    '''爬虫函数'''
    city = str
    conn = MongoClient('172.17.0.1', 27017)
    db = conn.weather
    sysstr = platform.system()
    print sysstr
    if sysstr == "Windows":
        driver = webdriver.PhantomJS(executable_path="phantomjs.exe")
    else:
        driver = webdriver.PhantomJS(executable_path="./phantomjs")

    try:
        '''今日天气'''
        driver.get("http://www.weather.com.cn/weather1d/" + city + ".shtml")
        doc = pq(driver.page_source)
        today = {}
        today['update_time'] = doc('.ctop .time').text()  # "07:30更新 | 数据来源 中央气象台"
        today['update_time'] = today['update_time'].split('|')[0]  # 07:30更新
        weather_element = doc('.wea')
        today['weather'] = weather_element.eq(0).text() + u'转' + weather_element.eq(1).text()  # "晴间多云转晴转多云"
        tem_element = doc('.tem span')
        today['tempmax'] = tem_element.eq(1).text()  # 33
        today['tempmin'] = tem_element.eq(2).text()  # 20
        today['wind'] = doc('.w').text()
        today['pollute'] = doc('.pol').text()
        # today['warning'] = doc('.wea-three03').find('span').text()
        today['city'] = str
        today['time'] = time.time()
        my_set = db.today
        my_set.insert(today)

        # 未来15天天气
        driver.get("http://e.weather.com.cn/d/15days/" + city + ".shtml")
        doc = pq(driver.page_source)
        lis = doc('.days-list').find('li')
        for li in lis.items():
            future = {}
            future['date'] = li.find(".days-list-top").find('time').text()  # 08/25 星期五
            future['pollute'] = li.find(".days-list-top").find('p').text()  # 优
            future['temp'] = li.find(".days-list-foot").find(".days-item-tem").find(".days-tem-day").text()  # 33°
            future['weather'] = li.find(".days-list-foot").find(".days-item-weather").find(
                ".days-weather-right").text()  # 晴
            future['city'] = str
            future['time'] = time.time()
            my_set = db.future
            my_set.insert(future)

        '''穿衣建议'''
        driver.get("http://e.weather.com.cn/d/mcy/" + city + ".shtml")
        doc = pq(driver.page_source)
        today = doc(".weather-bar-title").text()
        advice = {}
        advice['today'] = today.split(' ')[0]  # 炎热
        advice['advice'] = doc("#datebox").text()  # 天气炎热，建议着短衫、短裙、短裤、薄型T恤衫等清凉夏季服装。
        advice['city'] = str
        advice['time'] = time.time()
        my_set = db.advice
        my_set.insert(advice)

        # driver.get("http://e.weather.com.cn/d/air/" + city + ".shtml")
        # doc = pq(driver.page_source)
        # dls = doc('dl')
        # l = []
        # for dl in dls.items():
        #     l.append(dl.find('dt').text())
        # sql = "INSERT INTO `spider`.`aqi`(`pm10`,`pm2_5`,`no2`,`so2`,`co`,`o3`,`time`,`city`)VALUES('%s','%s','%s','%s','%s','%s','%s','%s')" % (
        #     l[0], l[1], l[2], l[3], l[4], l[5], time.time(), city)
        # cursor.execute(sql)
        # db.commit()
        # db.close()
        print "true"
        return True
    except Exception, e:
        print Exception, ":", e
        print False


def search(city,info):
    pass


if __name__ == '__main__':
    spider('101010100')
