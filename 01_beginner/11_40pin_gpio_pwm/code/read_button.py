#!/usr/bin/env python3
"""读取连接在 RDK X5 物理 37 号引脚上的按键。"""

import time

import Hobot.GPIO as GPIO


button_pin = 37

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(button_pin, GPIO.IN)

last_state = None
print("按下 Ctrl+C 退出")

try:
    while True:
        state = GPIO.input(button_pin)

        if state != last_state:
            if state == GPIO.LOW:
                print("按键按下")
            else:
                print("按键松开")
            last_state = state

        time.sleep(0.05)
except KeyboardInterrupt:
    print("程序结束")
finally:
    GPIO.cleanup()
