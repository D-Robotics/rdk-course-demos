#!/usr/bin/env python3
"""使用 RDK X5 物理 33 号引脚输出 PWM，控制舵机。"""

import time

import Hobot.GPIO as GPIO


servo_pin = 33

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

pwm = GPIO.PWM(servo_pin, 50)
pwm.start(0)

try:
    for duty in (5.0, 7.5, 10.0, 7.5):
        print("当前占空比：", duty)
        pwm.ChangeDutyCycle(duty)
        time.sleep(1)
finally:
    pwm.stop()
    GPIO.cleanup()
