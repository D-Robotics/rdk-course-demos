# Boot troubleshooting on RDK S100

**Goal:** Find where the RDK S100 boot path stops after flashing and collect a useful debug log.  
**Estimated time:** 5 minutes

Flashing an image successfully does not prove that the S100 can boot it. Check the boot mode first, then capture the Main-domain debug output before changing the image again.

## Check the boot mode

A continuously lit red `DOWNLOAD` indicator means that the board is still in DFU flashing mode. Return `SW2` to the normal boot position and power-cycle the board. When `DOWNLOAD` is off but the orange `SYSTEM` indicator does not blink normally, continue with the debug console.

## Connect the S100 debug console

RDK S100 uses the USB Type-C `J16` interface. J16 exposes flashing, Main-domain debug, and MCU-domain debug channels. Select the Main-domain channel for Linux boot output.

| Setting | Value |
| --- | --- |
| Physical interface | USB Type-C, J16 |
| Debug channel | Main domain |
| Baud rate | 921600 |
| Data format | 8 data bits, 1 stop bit, parity None |
| Flow control | None |

1. Confirm that `SW2` is in the normal boot position and `DOWNLOAD` is off.
2. Connect a data-capable Type-C cable from `J16` to the host.
3. Identify the serial devices exposed by J16 and select the Main-domain channel.
4. Open it with `921600`, `8-N-1`, and flow control disabled.
5. Enable terminal logging before powering on or resetting the S100.

Multiple serial devices are normal because J16 exposes both Main and MCU debug channels. If no device appears, check the cable and the CH341 or CH340 driver.

## Interpret the log

- **`DOWNLOAD` stays on:** correct the `SW2` position and reboot.
- **No output:** confirm the Main-domain channel and `921600` baud rate.
- **Early boot stops:** check `SW2`, the boot media, flash result, and the first clear error.
- **Kernel or filesystem error:** preserve the first error and the surrounding lines.
- **Login prompt appears:** the S100 has booted; continue with display, network, or application debugging.

## Share useful evidence

Include the board revision, image version, flashing result, power setup, LED state, selected J16 channel, serial settings, full text log, and exact reproduction steps.

## Resources

- [Course code and materials](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/05_boot_troubleshooting)
- [RDK S100 hardware documentation](https://developer.d-robotics.cc/rdk_doc/rdk_s/Quick_start/hardware_introduction/rdk_s100/)
- [RDK FAQ](https://developer.d-robotics.cc/rdk_doc/FAQ)
