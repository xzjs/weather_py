#!/usr/bin/python
# -*- coding:utf-8 -*-
import time

import pymongo
from selenium import webdriver
from pyquery import PyQuery as pq
import platform
import zmq
import re

sysstr = platform.system()
conn_host = '127.0.0.1'
conn = pymongo.MongoClient(conn_host, 27017)
db = conn.weather


def spider(city):
    '''爬虫函数'''
    sysstr = platform.system()
    print sysstr
    if sysstr == "Windows":
        driver = webdriver.phantomjs(executable_path="phantomjs.exe")
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
        weather1 = weather_element.eq(0).text()
        weather2 = weather_element.eq(1).text()
        if weather1 == weather2:
            today['weather'] = weather1
        else:
            today['weather'] = weather1 + u'转' + weather2  # "晴间多云转晴转多云"

        tem_str = doc('#hidden_title').val()
        search_obj = re.search(r'-?\d{1,2}/-?\d{1,2}', tem_str)
        if search_obj:
            tem_str = search_obj.group()
            tem = tem_str.split('/')
            today['tempmax'] = tem[0]
            today['tempmin'] = tem[1]

        today['wind'] = doc('.w').text()
        today['pollute'] = doc('.pol').text()
        # today['warning'] = doc('.wea-three03').find('span').text()
        today['city'] = city
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
            future['city'] = city
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
        advice['city'] = city
        advice['time'] = time.time()
        my_set = db.advice
        my_set.insert(advice)
        print "true"
        return True
    except Exception, e:
        print Exception, ":", e
        print False


def search(city, info, num=15):
    '''搜索函数'''
    advices = db.advice.find({"city": city}).sort([("time", -1)])
    if advices.count() == 0 or (time.time() - advices[0]['time'] > 3600):
        spider(city)
    result = {}
    for i in info:
        if i == 'advice':
            advice = db.advice.find({"city": city}, {"_id": 0}).sort('time', pymongo.ASCENDING).limit(1)
            for _advice in advice:
                result['advice'] = _advice
        if i == 'aqi':
            pass
        if i == 'today':
            today = db.today.find({"city": city}, {"_id": 0}).sort('time', -1).limit(1)
            print city
            for _today in today:
                result['today'] = _today
        if i == 'future':
            future = db.future.find({"city": city}, {"_id": 0}).sort('time', pymongo.ASCENDING).limit(num)
            array = []
            for _future in future:
                array.append(_future)
            result['future'] = array
    return result


if __name__ == '__main__':
    # zmq
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5556")
    # spider('101010100')
    # print search('101010100', ['advice', 'aqi', 'today', 'future'], 15)
    try:
        print 'start,listen 5556'
        while True:
            message = socket.recv_json()
            print message
            num = 15
            if message.has_key('num'):
                num = message['num']
            result = search(message['city'], message['info'], num)
            print result
            socket.send_json(result)
    except Exception, ex:
        print Exception, ":", ex
