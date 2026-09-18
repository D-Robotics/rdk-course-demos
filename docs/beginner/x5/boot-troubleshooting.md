# Boot troubleshooting on RDK X5

**Goal:** Find where the RDK X5 boot path stops after flashing and collect a useful debug log.  
**Estimated time:** 5 minutes

Flashing an image successfully does not prove that the X5 can boot it. If the board has no display or network connection, capture its debug serial output before changing the image again.

## Connect the X5 debug console

RDK X5 uses the Micro USB debug serial port on interface 4.

| Setting | Value |
| --- | --- |
| Physical interface | Micro USB, interface 4 |
| Baud rate | 115200 |
| Data format | 8 data bits, 1 stop bit, parity None |
| Flow control | None |

1. Connect a data-capable Micro USB cable from interface 4 to the host.
2. Confirm that a new serial port appears on the host.
3. Open it with `115200`, `8-N-1`, and flow control disabled.
4. Enable terminal logging before powering on or resetting the X5.

If no serial device appears, check the cable, USB port, and CH340 driver. On Linux, also check whether `brltty` has claimed the CH340 device.

## Interpret the log

- **No output:** check the Micro USB interface, cable, driver, serial port, and baud rate.
- **Early boot stops:** check the boot media, flash result, and the first clear error.
- **Kernel or filesystem error:** preserve the first error and the surrounding lines.
- **Login prompt appears:** the X5 has booted; continue with display, network, or application debugging.

For repeated resets, save at least one complete reset cycle. Change only one condition at a time.

## Share useful evidence

Include the board revision, image version, flashing result, power setup, LED state, serial settings, full text log, and exact reproduction steps.

## Resources

- [Course code and materials](https://github.com/D-Robotics/rdk-course-demos/tree/main/01_beginner/05_boot_troubleshooting)
- [RDK X5 hardware documentation](https://developer.d-robotics.cc/rdk_doc/Quick_start/hardware_introduction/rdk_x5/)
- [RDK FAQ](https://developer.d-robotics.cc/rdk_doc/FAQ)
