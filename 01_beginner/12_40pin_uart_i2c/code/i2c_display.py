#!/usr/bin/env python3

import argparse
import time

from PIL import Image, ImageDraw, ImageFont
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306


def parse_args():
    parser = argparse.ArgumentParser(description="RDK X5 I2C OLED demo")
    parser.add_argument("--port", type=int, default=5, help="I2C bus number")
    parser.add_argument(
        "--address",
        type=lambda value: int(value, 0),
        default=0x3C,
        help="OLED address, for example 0x3C or 0x3D",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    serial = i2c(port=args.port, address=args.address)
    device = ssd1306(serial)
    font = ImageFont.load_default()

    print(
        f"OLED started on /dev/i2c-{args.port}, address 0x{args.address:02X}. "
        "Press CTRL+C to exit."
    )

    try:
        while True:
            image = Image.new("1", (device.width, device.height))
            draw = ImageDraw.Draw(image)
            draw.text((0, 0), "RDK X5", font=font, fill=255)
            draw.text((0, 18), "I2C OLED Demo", font=font, fill=255)
            draw.text((0, 36), time.strftime("%H:%M:%S"), font=font, fill=255)
            device.display(image)
            time.sleep(1)
    except KeyboardInterrupt:
        device.clear()
        print("\nOLED cleared")


if __name__ == "__main__":
    main()
