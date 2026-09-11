# RDK S100 40-pin SPI courseware

This directory keeps the existing RDK X5 lesson unchanged and adds a minimal RDK S100 SPI0 loopback variant used for the course video.

- [中文课件](./lesson-13-s100-zh.html)
- [English courseware](./lesson-13-s100.html)

The demonstration connects physical Pin 19 (MOSI) to Pin 21 (MISO), opens `/dev/spidev0.0` at 12 MHz, and verifies that `0x55 0xAA` is returned continuously. Both HTML files are self-contained and can be opened directly in a browser.

