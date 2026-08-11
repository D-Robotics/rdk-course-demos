# Flash a system image on RDK X5

This tutorial covers the RDK X5 flashing workflow. Use the X5 image package and the flashing method documented for your software release.

## Before flashing

1. Confirm that the board is an RDK X5 and record its hardware revision.
2. Download an image that explicitly supports RDK X5.
3. Read the current RDK X5 flashing guide for the selected image release.
4. Prepare a known-good data cable and the required power adapter.
5. Install the host drivers or command-line dependencies required by the flashing tool.

## After flashing

Power-cycle the X5 and check its indicators. A successful write only confirms that the image reached the storage device; it does not prove that the board completed its first boot.

If the X5 has no display or network connection, do not immediately flash it again. Open the [RDK X5 boot troubleshooting](05-boot-troubleshooting-x5.md) tutorial and capture the early boot log first.

!!! note
    Flashing tools, image layouts, and device modes can change between releases. Treat the current official RDK X5 documentation as the source of truth for button sequences and tool options.

## Resources

- [Course code and materials](https://github.com/D-Robotics/rdk-course-demos/tree/main/01_beginner/04_flash_system)
- [Official RDK X5 documentation](https://developer.d-robotics.cc/rdk_doc/Quick_start/)
