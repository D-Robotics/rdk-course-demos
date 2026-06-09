#!/usr/bin/env python3
"""Light up a 2.0-inch 240x320 SPI LCD on the RDK X5 40-pin header.

Default wiring:
  DIN -> BOARD 19 / SPI1_MOSI
  CLK -> BOARD 23 / SPI1_SCLK
  CS  -> BOARD 24 / SPI1_CSN1 (/dev/spidev1.1)
  DC  -> BOARD 22
  RST -> BOARD 31
  BL  -> BOARD 33
"""

from __future__ import annotations

import argparse
import math
import time
from typing import Iterable

import Hobot.GPIO as GPIO
import spidev
from PIL import Image, ImageDraw, ImageFont


RGB565_BLACK = b"\x00\x00"


class ST7789:
    def __init__(
        self,
        *,
        bus: int,
        device: int,
        width: int,
        height: int,
        dc_pin: int,
        rst_pin: int,
        bl_pin: int | None,
        x_offset: int,
        y_offset: int,
        speed_hz: int,
        rotation: int,
        bgr: bool,
    ) -> None:
        self.width = width
        self.height = height
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.dc_pin = dc_pin
        self.rst_pin = rst_pin
        self.bl_pin = bl_pin
        self.rotation = rotation % 360
        self.bgr = bgr

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.dc_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.rst_pin, GPIO.OUT, initial=GPIO.HIGH)
        if self.bl_pin is not None:
            GPIO.setup(self.bl_pin, GPIO.OUT, initial=GPIO.HIGH)

        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.mode = 0
        self.spi.bits_per_word = 8
        self.spi.max_speed_hz = speed_hz

    def close(self) -> None:
        self.spi.close()

    def hard_reset(self) -> None:
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.02)
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.05)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.12)

    def command(self, cmd: int, data: Iterable[int] | bytes = b"", delay: float = 0) -> None:
        GPIO.output(self.dc_pin, GPIO.LOW)
        self.spi.xfer2([cmd & 0xFF])
        if data:
            GPIO.output(self.dc_pin, GPIO.HIGH)
            payload = bytes(data)
            for start in range(0, len(payload), 4096):
                self.spi.writebytes2(payload[start : start + 4096])
        if delay:
            time.sleep(delay)

    def init(self) -> None:
        self.hard_reset()
        self.command(0x36, [self._madctl()])
        self.command(0x3A, [0x05])  # 16-bit RGB565 (Waveshare 2inch)
        self.command(0x21)  # Display inversion on
        self.command(0x2A, [0x00, 0x00, 0x01, 0x3F])
        self.command(0x2B, [0x00, 0x00, 0x00, 0xEF])
        self.command(0xB2, [0x0C, 0x0C, 0x00, 0x33, 0x33])
        self.command(0xB7, [0x35])
        self.command(0xBB, [0x1F])
        self.command(0xC0, [0x2C])
        self.command(0xC2, [0x01])
        self.command(0xC3, [0x12])
        self.command(0xC4, [0x20])
        self.command(0xC6, [0x0F])
        self.command(0xD0, [0xA4, 0xA1])
        self.command(0xE0, [0xD0, 0x08, 0x11, 0x08, 0x0C, 0x15, 0x39, 0x33, 0x50, 0x36, 0x13, 0x14, 0x29, 0x2D])
        self.command(0xE1, [0xD0, 0x08, 0x10, 0x08, 0x06, 0x06, 0x39, 0x44, 0x51, 0x0B, 0x16, 0x14, 0x2F, 0x31])
        self.command(0x11, delay=0.12)  # Sleep out
        self.command(0x29, delay=0.02)  # Display on
        self.clear()

    def _madctl(self) -> int:
        # MY MX MV ML BGR MH 0 0
        value = 0x08 if self.bgr else 0x00
        if self.rotation == 0:
            value |= 0x00
        elif self.rotation == 90:
            value |= 0x60
        elif self.rotation == 180:
            value |= 0xC0
        elif self.rotation == 270:
            value |= 0xA0
        else:
            raise ValueError("rotation must be one of 0, 90, 180, 270")
        return value

    def set_window(self, x0: int, y0: int, x1: int, y1: int) -> None:
        x0 += self.x_offset
        x1 += self.x_offset
        y0 += self.y_offset
        y1 += self.y_offset
        self.command(0x2A, [(x0 >> 8) & 0xFF, x0 & 0xFF, (x1 >> 8) & 0xFF, x1 & 0xFF])
        self.command(0x2B, [(y0 >> 8) & 0xFF, y0 & 0xFF, (y1 >> 8) & 0xFF, y1 & 0xFF])
        self.command(0x2C)

    def clear(self, color: bytes = RGB565_BLACK) -> None:
        self.set_window(0, 0, self.width - 1, self.height - 1)
        GPIO.output(self.dc_pin, GPIO.HIGH)
        line = color * self.width
        for _ in range(self.height):
            self.spi.writebytes2(line)

    def show(self, image: Image.Image) -> None:
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)
        payload = rgb888_to_rgb565(image.convert("RGB"))
        self.set_window(0, 0, self.width - 1, self.height - 1)
        GPIO.output(self.dc_pin, GPIO.HIGH)
        for start in range(0, len(payload), 4096):
            self.spi.writebytes2(payload[start : start + 4096])


def rgb888_to_rgb565(image: Image.Image) -> bytes:
    out = bytearray(image.width * image.height * 2)
    i = 0
    for r, g, b in image.getdata():
        value = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        out[i] = (value >> 8) & 0xFF
        out[i + 1] = value & 0xFF
        i += 2
    return bytes(out)


def load_font(size: int) -> ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def make_test_image(width: int, height: int) -> Image.Image:
    image = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(image)

    for y in range(height):
        t = y / max(1, height - 1)
        for x in range(width):
            s = x / max(1, width - 1)
            r = int(255 * s)
            g = int(255 * (1 - t))
            b = int(160 + 95 * math.sin((s + t) * math.pi))
            image.putpixel((x, y), (r, g, max(0, min(255, b))))

    bar_h = max(22, height // 10)
    colors = ["red", "lime", "blue", "white", "yellow", "cyan", "magenta", "black"]
    bar_w = width // len(colors)
    for i, color in enumerate(colors):
        draw.rectangle((i * bar_w, 0, (i + 1) * bar_w - 1, bar_h), fill=color)

    draw.rounded_rectangle((14, bar_h + 18, width - 14, height - 20), radius=10, fill=(8, 12, 18), outline=(255, 255, 255), width=2)
    title_font = load_font(30)
    body_font = load_font(18)
    small_font = load_font(14)
    draw.text((28, bar_h + 36), "RDK X5", font=title_font, fill=(255, 255, 255))
    draw.text((28, bar_h + 76), "2.0 SPI LCD", font=body_font, fill=(82, 210, 255))
    draw.text((28, bar_h + 106), "ST7789 RGB565", font=body_font, fill=(255, 210, 96))
    draw.text((28, height - 52), time.strftime("%H:%M:%S"), font=small_font, fill=(210, 235, 255))
    return image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RDK X5 2.0-inch 240x320 SPI LCD ST7789 bring-up")
    parser.add_argument("--bus", type=int, default=1)
    parser.add_argument("--device", type=int, default=1, help="CS index. BOARD pin 24 / SPI1_CSN1 is device 1.")
    parser.add_argument("--width", type=int, default=240)
    parser.add_argument("--height", type=int, default=320)
    parser.add_argument("--dc", type=int, default=22)
    parser.add_argument("--rst", type=int, default=31)
    parser.add_argument("--bl", type=int, default=33)
    parser.add_argument("--no-bl", action="store_true", help="Use this if BL is tied directly to 3.3V.")
    parser.add_argument("--x-offset", type=int, default=0)
    parser.add_argument("--y-offset", type=int, default=0, help="Set offsets if the panel has a shifted GRAM window.")
    parser.add_argument("--speed", type=int, default=24_000_000)
    parser.add_argument("--rotation", type=int, default=0, choices=(0, 90, 180, 270))
    parser.add_argument("--rgb", action="store_true", help="Clear BGR bit if red/blue appear swapped.")
    parser.add_argument("--solid", choices=("red", "green", "blue", "white", "black"), help="Fill one solid color instead of the demo image.")
    parser.add_argument("--hold", action="store_true", help="Keep the process alive after drawing.")
    return parser.parse_args()


def color565(name: str) -> bytes:
    values = {
        "black": 0x0000,
        "white": 0xFFFF,
        "red": 0xF800,
        "green": 0x07E0,
        "blue": 0x001F,
    }
    value = values[name]
    return bytes([(value >> 8) & 0xFF, value & 0xFF])


def main() -> None:
    args = parse_args()
    lcd = ST7789(
        bus=args.bus,
        device=args.device,
        width=args.width,
        height=args.height,
        dc_pin=args.dc,
        rst_pin=args.rst,
        bl_pin=None if args.no_bl else args.bl,
        x_offset=args.x_offset,
        y_offset=args.y_offset,
        speed_hz=args.speed,
        rotation=args.rotation,
        bgr=not args.rgb,
    )
    try:
        lcd.init()
        if args.solid:
            lcd.clear(color565(args.solid))
        else:
            lcd.show(make_test_image(args.width, args.height))
        print("LCD draw complete.")
        if args.hold:
            print("Holding. Press Ctrl+C to exit.")
            while True:
                time.sleep(1)
    finally:
        lcd.close()


if __name__ == "__main__":
    main()
