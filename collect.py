#!/usr/bin/python
# -*- coding:utf-8 -*-

import time
import zmq

if __name__ == '__main__':
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5556")
    cities = ['101010100', '101020100', '101280101', '101280601', '101120201']
    while True:
        for city in cities:
            message = json.dumps({'city': city, 'info': ['today']})
            socket.send(message)
            response = socket.recv()
            print response
            time.sleep(30 * 60)
