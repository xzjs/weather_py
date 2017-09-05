# -*- coding:utf-8 -*-
import time

import pymongo
from selenium import webdriver
from pyquery import PyQuery as pq
import platform
import zmq

sysstr = platform.system()
conn_host = '127.0.0.1' if sysstr == "Windows" else "172.17.0.1"
conn = pymongo.MongoClient(conn_host, 27017)
db = conn.weather


def spider(str):
    '''爬虫函数'''
    city = str
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


def search(city, info, num=15):
    advices = db.advice.find({"city": city}).sort([("time", -1)])
    if advices.count() == 0 or (time.time() - advices[0]['time'] > 3600):
        spider(city)
    result = {}
    for i in info:
        if i == 'advice':
            advice = db.advice.find({"city": city}).sort('time', pymongo.ASCENDING).limit(1)
            for _advice in advice:
                result['advice'] = _advice
        if i == 'aqi':
            pass
        if i == 'today':
            today = db.today.find({"city": city}).sort('time', pymongo.ASCENDING).limit(1)
            for _today in today:
                result['today'] = _today
        if i == 'future':
            future = db.future.find({"city": city}).sort('time', pymongo.ASCENDING).limit(num)
            array = []
            for _future in future:
                array.append(_future)
            result['future'] = array
    return result


if __name__ == '__main__':
    # spider('101010100')
    print search('101010100', ['advice', 'aqi', 'today', 'future'], 15)
