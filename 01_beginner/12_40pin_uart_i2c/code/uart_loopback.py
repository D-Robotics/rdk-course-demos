#!/usr/bin/env python3

import time

import serial


ser = serial.Serial("/dev/ttyS1", 115200, timeout=1)

try:
    while True:
        ser.write(b"AA55")
        data = ser.read(4)

        print("发送", "AA55")
        print("接收", data.decode())

        time.sleep(1)
except KeyboardInterrupt:
    ser.close()
    print("串口已关闭")
