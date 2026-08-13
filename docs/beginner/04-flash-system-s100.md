# Flash a system image on RDK S100

This tutorial covers the RDK S100 flashing workflow. Use the S100 image package and the flashing method documented for your software release.

## Before flashing

1. Confirm that the board is an RDK S100 and record its hardware revision.
2. Download an image that explicitly supports RDK S100.
3. Read the current RDK S100 flashing guide and identify the required `SW2` position.
4. Prepare a data-capable USB Type-C cable and the required power adapter.
5. Install the host drivers or command-line dependencies required by the flashing tool.

## After flashing

Return `SW2` to the normal boot position before power-cycling the board. If the red `DOWNLOAD` indicator remains on, the S100 is still in DFU flashing mode and will not perform a normal Linux boot.

If `DOWNLOAD` is off but the system does not start normally, open the [RDK S100 boot troubleshooting](05-boot-troubleshooting-s100.md) tutorial and capture the Main-domain boot log before flashing again.

!!! note
    Flashing tools, image layouts, and switch behavior can change between releases. Treat the current official RDK S100 documentation as the source of truth for the complete procedure.

## Resources

- [Course code and materials](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/04_flash_system)
- [Official RDK S100 documentation](https://developer.d-robotics.cc/rdk_doc/rdk_s/Quick_start/)
