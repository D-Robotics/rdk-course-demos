#!/usr/bin/env python3

import time

import serial


def main():
    ser = serial.Serial("/dev/ttyS1", 115200, timeout=1)
    try:
        print("Starting demo now! Press CTRL+C to exit")
        while True:
            ser.write(b"AA55")
            data = ser.read(4)
            print("Send: AA55")
            print("Recv:", data.decode("utf-8", errors="replace"))
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSerial port closed")
    finally:
        ser.close()


if __name__ == "__main__":
    main()
