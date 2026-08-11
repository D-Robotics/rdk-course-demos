# Learning path

RDK Classroom is organized around the decisions a developer makes while bringing up a board and building an application.

1. **Orient yourself.** Find the correct board documentation, image, community channel, and course demo.
2. **Bring up the board.** Prepare the host, flash the system image, and verify that the board reaches a usable state.
3. **Debug with evidence.** Capture boot logs before changing variables. Use the first clear failure to choose the next check.
4. **Add interfaces.** Validate camera, audio, display, GPIO, UART, I2C, SPI, and CAN one subsystem at a time.
5. **Build applications.** Continue into ModelZoo and TROS when the base system and hardware interfaces are understood.

## A repeatable tutorial loop

Each lesson should answer four questions:

- What will I build or verify?
- What hardware, image, and host dependencies do I need?
- What output tells me the step worked?
- What should I capture when it does not work?

Use the course demo directory as the implementation companion for each lesson.
