# Lesson 12 Video Script: RDK X5 40-pin Header, UART and I2C

> This script is written for an eight-to-ten-minute lesson with live demonstrations. The narration is ready to read aloud. To keep the video under eight minutes, remove the brief `srpi-config` note and the second UART run with the jumper removed.

## Before filming

- Run the complete UART loopback and OLED demonstrations once before recording.
- Confirm whether the OLED address is `0x3C` or `0x3D`, and update the code if necessary.
- Increase the terminal font size and use a high-contrast theme. Keep only the terminal and course notes in the screen recording.
- Have the jumper cap, jumper wires, and OLED ready. Make sure the camera can show the 40-pin connections clearly.

## Timing overview

| Time | Segment | Content |
| --- | --- | --- |
| 0:00–0:40 | Introduction | Why GPIO alone is not enough, and where UART and I2C fit in |
| 0:40–2:20 | UART | Crossed TX/RX wiring, matching settings, and `/dev/ttyS1` |
| 2:20–4:20 | Demo 1 | UART loopback test and matching Send/Recv output |
| 4:20–6:20 | I2C | Clock and data lines, device addresses, bus numbers, and `i2cdetect` |
| 6:20–8:50 | Demo 2 | Scan for the OLED, run the program, and light the display |
| 8:50–9:30 | Wrap-up | Key takeaways, course notes, and the next lesson |

## 1. Introduction, 0:00–0:40

**Visual:** Presenter on camera or a close-up of the board, with the lesson title on screen.

**Narration:**

Hi everyone, and welcome back to the RDK X5 series. In earlier lessons, we used GPIO pins to control an LED and read a button. But GPIO alone only gets us so far. As soon as we want to connect another device, or even a small display, we need a better way to communicate. That brings us to today’s two topics: UART and I2C. By the end of this lesson, we will have the UART port working and an I2C OLED display up and running.

## 2. UART, 0:40–2:20

**Visual:** Full-screen 40-pin diagram with Pin 8 TX and Pin 10 RX highlighted.

**Narration:**

UART does not have a clock line. Both devices have to agree on the timing before they start, a bit like two musicians playing together without a conductor. They can stay in sync only if they agree on the tempo first. In UART, that tempo is the baud rate.

UART sends data one bit at a time. For every byte, the hardware builds a frame. A start bit comes first, followed by eight data bits, and then a stop bit. The UART hardware takes care of packing and unpacking those frames, so our program only needs to read and write bytes.

Settings such as `115200, 8N1` must match at both ends. If the baud rate, number of data bits, parity setting, or number of stop bits is different, the receiver samples the signal at the wrong time and the result is usually garbage. Mismatched settings are the most common cause of unreadable serial output.

There are two wiring rules to remember. First, cross TX and RX. My transmit pin connects to your receive pin. Second, connect the grounds so both devices use the same voltage reference.

On the RDK X5, this port is UART1. Pin 8 is TX, Pin 10 is RX, and Linux exposes the port as `/dev/ttyS1`. Leave `/dev/ttyS0` alone because the system uses it as the debug console.

One final warning. Every signal on the 40-pin header uses 3.3-volt logic, and the maximum input voltage is 3.46 volts. Do not connect a 5-volt UART device directly. It can permanently damage the board.

## 3. Demo 1: UART loopback test, 2:20–4:20

**Visual:** Close-up of the jumper across Pins 8 and 10, followed by the terminal. Remove the jumper and run the test again for comparison.

**Action:** Power the board off. Short Pins 8 and 10 with a jumper cap. Power the board on, run `uart_loopback.py`, and show that Send and Recv match. Remove the jumper and run the program again to show an empty Recv result.

**Narration:**

Let’s begin with the smallest useful test: a loopback. With the power off, I am shorting Pins 8 and 10 with a jumper cap. That sends everything the UART transmits straight back into its own receiver.

Now I will run the test program. It sends `AA55` once every second. Here, Send and Recv match exactly, so we know that both transmit and receive are working.

Now I will remove the jumper and run it again. Recv is empty. That missing physical connection is the loop in “loopback.” Run this test before connecting an external serial device and you can eliminate many basic hardware and configuration problems immediately.

## 4. I2C, 4:20–6:20

**Visual:** Close-up of the OLED pins with GND, VCC, SCL, and SDA labeled.

**Narration:**

I2C works differently because it has a clock line. SCL provides the timing and SDA carries the data. Both sides follow the same clock, which makes I2C a synchronous protocol. The devices do not need to agree on a separate baud rate ahead of time.

Think of it like taking attendance in a classroom. Several devices share the same two wires. The controller calls one address, such as `0x3C` for this display. Only the device with that address responds. It acknowledges the call with an ACK, and then the data transfer begins.

That is also what `i2cdetect` does. It tries each address in turn and reports which devices acknowledge it.

The RDK X5 exposes two I2C buses on the 40-pin header. Pins 3 and 5 carry I2C5, while Pins 27 and 28 carry I2C0. Today, the OLED is connected to Pins 3 and 5, so the Linux bus number is 5.

The display needs four connections. VCC goes to Pin 1 for 3.3 volts. GND goes to Pin 39. SDA goes to Pin 3, and SCL goes to Pin 5.

Before writing any code, run `i2cdetect -y 5`. If `3c` appears in the table, the device is online. That result is our green light for everything that follows.

If the pin function does not work, open the bus settings in `sudo srpi-config` and make sure I2C is enabled. Restart the board after changing the setting.

## 5. Demo 2: OLED display, 6:20–8:50

**Visual:** Close-up of the four wires, a close-up of the `i2cdetect` result, and then the OLED lighting up. Hold the final shot for two extra seconds.

**Action:** Connect the OLED using the wiring table. Run `i2cdetect -y 5` and confirm address `3c`. Run `i2c_display.py`, then show the three lines of text and the clock updating.

**Narration:**

Now let’s bring the display to life. I have connected the four wires exactly as shown in the course notes. Before running the Python program, I will scan the bus. There is `3c`, so the OLED is present and responding.

Next, I will run `i2c_display.py`. The program uses the `luma.oled` library. The port is set to bus 5, and the device address is `0x3C`.

And there it is. The display shows “RDK X5,” “I2C OLED Demo,” and the current time, which updates once a second. To display your own text, edit the `draw.text` calls in the program.

If the screen stays blank, troubleshoot it in this order. First, run `i2cdetect` and confirm that the address appears. Next, verify the bus number and device address. Finally, check whether the controller is an SSD1306 or an SH1106. They require different drivers.

## 6. Wrap-up, 8:50–9:30

**Visual:** Presenter on camera or a close-up of the working OLED, with a link to the course notes on screen.

**Narration:**

That is everything for this lesson. For UART, remember two things: the settings must match, and TX connects to RX. For I2C, make sure you have the right Linux bus number and the right device address.

The complete wiring tables, commands, code, and practice exercises are all included in the course notes linked in the video description. In the next lesson, we will put live sensor data on this display. See you then.

## Filming notes

Always show these terms as on-screen text so viewers can pause and copy them: `/dev/ttyS1`, `115200 8N1`, `i2cdetect -y 5`, `0x3C`, and `port=5`.

Suggested B-roll includes a close-up of the jumper across Pins 8 and 10, a magnified box around `3c` in the `i2cdetect` output, and the moment the OLED lights up.

