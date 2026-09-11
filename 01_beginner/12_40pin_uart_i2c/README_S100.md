# RDK S100 40-pin UART / I2C courseware

This directory keeps the existing RDK X5 lesson unchanged and adds a minimal RDK S100 variant used for the course video.

- [中文课件](./lesson-12-s100-zh.html)
- [English courseware](./lesson-12-s100.html)

The UART2 demonstration loops physical Pin 8 back to Pin 10 and verifies `AA55` transmit/receive data. The I2C demonstration uses I2C4 on physical Pins 27 and 28 with a PCF8574T detected at `0x20`. Both HTML files are self-contained and can be opened directly in a browser.

