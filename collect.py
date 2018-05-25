#!/usr/bin/python
# -*- coding:utf-8 -*-

import weather

if __name__ == '__main__':
    cities = ['101010100', '101020100', '101280101', '101280601', '101120201']
    while True:
        for city in cities:
            weather.spider(city)
            time.sleep(30 * 60)
