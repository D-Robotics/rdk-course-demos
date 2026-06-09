#!/usr/bin/env python3
# ST7789 LCD animation demo without external image assets.
# Draws a bouncing ball and pulsing title on screen.

from __future__ import annotations

import argparse
import math
import time

from PIL import Image, ImageDraw

from rdk_x5_lcd_st7789 import ST7789, load_font


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RDK X5 ST7789 bouncing-ball animation")
    parser.add_argument("--fps", type=float, default=30.0)
    parser.add_argument("--bus", type=int, default=1)
    parser.add_argument("--device", type=int, default=1)
    parser.add_argument("--width", type=int, default=240)
    parser.add_argument("--height", type=int, default=320)
    parser.add_argument("--dc", type=int, default=22)
    parser.add_argument("--rst", type=int, default=31)
    parser.add_argument("--bl", type=int, default=33)
    parser.add_argument("--no-bl", action="store_true")
    parser.add_argument("--x-offset", type=int, default=0)
    parser.add_argument("--y-offset", type=int, default=0)
    parser.add_argument("--speed", type=int, default=24_000_000)
    parser.add_argument("--rotation", type=int, default=0, choices=(0, 90, 180, 270))
    parser.add_argument("--rgb", action="store_true", help="Clear BGR bit if red/blue appear swapped.")
    return parser.parse_args()


def make_frame(
    width: int,
    height: int,
    *,
    ball_x: float,
    ball_y: float,
    ball_r: int,
    hue: float,
    frame_idx: int,
) -> Image.Image:
    image = Image.new("RGB", (width, height), (12, 16, 24))
    draw = ImageDraw.Draw(image)

    for y in range(height):
        t = y / max(1, height - 1)
        shade = int(18 + 20 * t)
        draw.line([(0, y), (width - 1, y)], fill=(shade, shade + 4, shade + 10))

    ground_y = height - 36
    draw.rectangle((0, ground_y, width - 1, height - 1), fill=(28, 32, 40))
    draw.line((0, ground_y, width - 1, ground_y), fill=(70, 78, 92), width=1)

    title_font = load_font(22)
    small_font = load_font(14)
    pulse = 0.5 + 0.5 * math.sin(frame_idx * 0.12)
    title_color = (int(80 + 120 * pulse), int(180 + 60 * pulse), 255)
    draw.text((14, 12), "RDK X5 LCD", font=title_font, fill=title_color)
    draw.text((14, 40), "SPI Animation Demo", font=small_font, fill=(150, 170, 200))
    draw.text((14, height - 22), time.strftime("%H:%M:%S"), font=small_font, fill=(120, 140, 170))

    r = int(127 + 127 * math.sin(hue))
    g = int(127 + 127 * math.sin(hue + 2.1))
    b = int(127 + 127 * math.sin(hue + 4.2))
    shadow_w = int(ball_r * 1.6)
    shadow_h = max(6, ball_r // 3)
    shadow_x = int(ball_x - shadow_w / 2)
    shadow_y = ground_y - shadow_h // 2
    draw.ellipse(
        (shadow_x, shadow_y, shadow_x + shadow_w, shadow_y + shadow_h),
        fill=(10, 12, 16),
    )

    x0, y0 = int(ball_x - ball_r), int(ball_y - ball_r)
    x1, y1 = int(ball_x + ball_r), int(ball_y + ball_r)
    draw.ellipse((x0, y0, x1, y1), fill=(r, g, b), outline=(255, 255, 255), width=2)
    return image


def main() -> int:
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

    margin = 24
    ball_r = 18
    x = float(args.width // 2)
    y = float(margin + ball_r)
    vx = 2.6
    vy = 0.0
    gravity = 0.35
    ground = args.height - 36 - ball_r
    delay = 1.0 / max(1.0, args.fps)
    frame_idx = 0

    try:
        lcd.init()
        print("Animation running. Press Ctrl+C to stop.")
        while True:
            t0 = time.time()
            vy += gravity
            x += vx
            y += vy

            if x - ball_r < margin:
                x = margin + ball_r
                vx = abs(vx)
            elif x + ball_r > args.width - margin:
                x = args.width - margin - ball_r
                vx = -abs(vx)

            if y + ball_r >= ground:
                y = ground
                vy = -abs(vy) * 0.82
                if abs(vy) < 1.2:
                    vy = -6.0

            frame = make_frame(
                args.width,
                args.height,
                ball_x=x,
                ball_y=y,
                ball_r=ball_r,
                hue=frame_idx * 0.08,
                frame_idx=frame_idx,
            )
            lcd.show(frame)
            frame_idx += 1

            elapsed = time.time() - t0
            sleep_time = delay - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        lcd.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
