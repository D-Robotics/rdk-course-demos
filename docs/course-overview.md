# RDK Course Overview

Welcome to the RDK development course.

This video course series is designed for RDK developers. Through **instructional videos + companion handbooks + GitHub demos**, it provides a systematic path through basic board operation, peripheral validation, model deployment, TROS development, system and driver debugging, and embodied-intelligence application development.

The resources have the following roles:

- **Instructional videos** are the core of the course and explain concepts, operating procedures, demonstrations, and common issues;
- **GitHub Pages handbooks** organize commands, steps, screenshots, troubleshooting methods, and reference links;
- **GitHub demos** provide scripts, example projects, and reproducible experiments;
- **Official documentation** provides extended details about products, systems, interfaces, and software stacks.

We recommend watching the instructional video first, then using the handbook and demo to complete the hands-on work on an RDK board.

---

# Who This Course Is For

This course is suitable for:

- Beginners with no prior experience;
- Developers using an RDK board for the first time who want to get started quickly;
- Developers with Linux experience who want to learn RDK peripherals, systems, and toolchains;
- Developers with AI, ROS, or robotics experience who want to deploy models or build applications on RDK;
- Developers building Camera, Audio, CAN, 40pin, codec, TROS, or embodied-intelligence projects with RDK;
- Learners who need a systematic view of the RDK curriculum, demo examples, and development-resource entry points.

---

# Recommended Learning Approach

Follow this sequence for each lesson:

1. Watch the instructional video to understand the lesson goal, experiment flow, and key precautions;
2. Open the GitHub Pages handbook and follow the commands, steps, and screenshots shown in the video;
3. If the lesson provides a GitHub demo, download or clone it and run it on the RDK board;
4. Use the success criteria and troubleshooting section in the handbook to verify the result;
5. Complete the extension exercises by changing parameters, replacing devices, or combining other capabilities.

Each lesson generally includes:

- A course video;
- A companion handbook;
- A GitHub demo;
- Official reference documentation;
- Experiment environment information;
- Operating procedures;
- Success criteria;
- Troubleshooting guidance;
- Extension exercises.

---

# Course Resources

## Instructional Videos

Instructional videos are the core content of this course.

Each video focuses on:

- The problem addressed by the lesson;
- Why the capability matters;
- The environment required before the experiment;
- The purpose of each command or operation;
- The expected result;
- How to identify and troubleshoot common errors;
- How the capability is used in real projects.

## GitHub Pages Handbooks

Entry points: [Chinese Course Handbooks](https://d-robotics.github.io/rdk-course-demos/zh/) | [English Course Handbooks](https://d-robotics.github.io/rdk-course-demos/)

The GitHub Pages handbooks are companion resources for the video course.

They are used to:

- Store course commands;
- Organize experiment steps;
- Provide screenshots and result descriptions;
- Record common issues;
- Collect reference links;
- Make it easy to copy commands and reproduce experiments.

The handbooks are not standalone tutorials and are best used together with the instructional videos.

## GitHub Demos

Entry point: [rdk-course-demos](https://github.com/D-Robotics/rdk-course-demos)

GitHub demos provide the code and example projects used by the course.

A demo may include:

- One-click inspection scripts;
- Example run scripts;
- C / C++ examples;
- Python examples;
- ROS / TROS examples;
- Model-inference demos;
- Configuration files;
- Example input and output data.

The original handbook Markdown and the source content for the GitHub Pages HTML interface are also stored in the `rdk-course-demos` repository.

## Official Documentation

Entry point: [RDK Documentation](https://d-robotics.github.io/rdk_doc_center/en/)

Official documentation provides complete information beyond the course, including product manuals, system documentation, interface descriptions, Model Zoo documentation, and TROS documentation.

---

# Recommended Learning Path

If you are using RDK for the first time, follow this sequence:

```text
Beginner: RDK Basics
↓
Advanced: ModelZoo Development Guide
↓
Advanced: TROS Development Guide
↓
Advanced: System and Driver Development Guide
↓
Expert: Large Language Models and Embodied Intelligence
↓
Developer Cases
```

If you already know Linux, ROS, or AI model deployment, you can go directly to the module that matches your current development goal.

---

# Curriculum

## I. Beginner: RDK Basics

This module is designed for new RDK users and focuses on how to boot the board, connect to it, verify peripherals, and run basic functions.

After completing this module, you should be able to use an RDK board independently, validate common peripherals, and troubleshoot basic issues.

| No. | Lesson | Main Video Topics | Materials |
|---|---|---|---|
| Lesson 1 | RDK Community and Ecosystem Introduction | RDK community, documentation entry points, NodeHub as an additional application-case entry, and forum guidelines | Video / Handbook |
| Lesson 2 | RDK Product Overview | Product families, hardware capabilities, roadmap, and typical use cases | Video / Handbook |
| Lesson 3 | Getting Started with RDK Studio | Meet the AI-native development workspace for RDK devices; use Moss for a read-only X5 health check and BPU YOLO real-time detection, and discover the terminal, files, code-server, remote desktop, system flashing, and on-device agents | Video / Handbook |
| Lesson 4 | RDK Lesson 4: System Flashing | System image flashing, MiniBoot updates, and post-flash checks | Video / Handbook |
| Lesson 5 | RDK Boot Process and Troubleshooting | Boot process, indicator status, boot logs, and typical boot issues | Video / Handbook |
| Lesson 6 | Remote Connection to RDK | Serial connection, SSH, networking, VNC, and remote development | Video / Handbook |
| Lesson 7 | Using Cameras with RDK | USB cameras, MIPI cameras, C/Python access, and quick TROS use | Video / Handbook / Demo |
| Lesson 8 | RDK Lesson 8: Audio | Onboard earphone interface, audio boards, and USB audio-device validation | Video / Handbook / Demo |
| Lesson 9 | Using Display Modules with RDK | HDMI and DSI display modules, display configuration, and result validation | Video / Handbook / Demo |
| Lesson 10 | RDK Lesson 10: Codec Usage | Encoding, decoding, BSP interfaces, RTSP streaming, and decoding | Video / Handbook / Demo |
| Lesson 11 | RDK 40pin Usage (1) | GPIO and PWM basics, LED control, and servo-control demos | Video / Handbook / Demo |
| Lesson 12 | RDK 40pin Usage (2) | UART basics, UART send/receive demos, I2C basics, and an I2C temperature-and-humidity sensor demo | Video / Handbook / Demo |
| Lesson 13 | RDK 40pin Usage (3) | SPI basics and an SPI display-driving demo | Video / Handbook / Demo |
| Lesson 14 | Using the RDK CAN Interface | CAN FD basics, can-utils, CAN loopback testing, CAN motor-control demos, and a CAN logic-analyzer demo | Video / Handbook / Demo |

---

## II. Advanced: ModelZoo && Robogo Development Guide

This module is designed for developers who want to run AI models on RDK. It covers model preparation, conversion, deployment, and representative vision-task demos, together with model training and conversion on the Robogo cloud platform.

After completing this module, you should understand the basic structure of RDK Model Zoo, be able to run model-inference experiments from existing demos, and use the Robogo cloud platform for cloud-based model training and conversion.

| No. | Lesson | Problem Addressed | Materials |
|---|---|---|---|
| Lesson 1 | ModelZoo Usage Guide | Understand the official Model Zoo repository, supported models, branch information, and how to run an existing sample quickly | Video / Handbook / GitHub Code |
| Lesson 2 | ModelZoo Sample Structure | Understand the purpose of directories such as conversion, model, runtime, evaluator, and test_data in a typical sample | Video / Handbook |
| Lesson 3 | Algorithm Toolchain and Quantization Environment | Use the local toolchain, Docker environment, and RoboGo cloud desktop, cloud host, or online quantization environment | Video / Handbook |
| Lesson 4 | ResNet Classification Training and Quantization | Train, export, quantize, validate, and run on-device inference for a ResNet classification model using cloud and local environments | Video / Handbook / GitHub Code |
| Lesson 5 | YOLO Detection Training and Quantization | Train a YOLO model, export ONNX, quantize, validate, and verify on-device inference using cloud and local environments | Video / Handbook / GitHub Code |
| Lesson 6 | Featuremap Model Quantization | Configure Featuremap-based models and understand their use cases and common issues in cloud and local environments | Video / Handbook |
| Lesson 7 | On-device Python Runtime Inference | Load a model with hbm_runtime, construct inputs, run inference, parse outputs, and visualize results | Video / Handbook / GitHub Code |
| Lesson 8 | On-device C/C++ Runtime Inference | Use C/C++ inference interfaces, model loading, preprocessing, BPU inference, post-processing, compilation, and execution | Video / Handbook / GitHub Code |
| Lesson 9 | YOLO Post-processing and Demo Adaptation | Parse detection boxes, configure thresholds and NMS, map classes, and adapt a YOLO Runtime demo to a custom model | Video / Handbook / GitHub Code |
| Lesson 10 | ModelZoo Collaborative Development | Follow the directory, naming, README, test-data, run-script, and submission requirements for a new sample | Video / Handbook |

---

## III. Advanced: TROS Development Guide

This module is designed for ROS / TROS developers and focuses on the robotics application-development workflow on RDK.

After completing it, you should be able to run TROS examples, understand the basic use of nodes, topics, services, and parameters, and complete basic Camera, perception, and control experiments.

---

## IV. Advanced: System and Driver Development Guide

This module is designed for developers working on peripheral adaptation, low-level debugging, and system integration.

After completing it, you should understand how common RDK interfaces are used at the system layer and be able to perform basic driver debugging and log analysis.

---

## V. Expert: Large Language Models and Embodied Intelligence

This module is designed for developers building agents, voice interaction, robot perception, and robot-control applications on RDK.

After completing it, you should understand the role of RDK in embodied-intelligence applications and be able to combine speech, vision, ROS/TROS, and large-model capabilities in a basic project.

---

## VI. Developer Cases

This module collects real projects, community work, and representative application solutions.

---

# Development Notes

The course is under continuous development. Lesson names, sequence, video content, handbook content, and demo examples will evolve with RDK product capabilities, official documentation, and developer feedback.

Course content is produced in the sequence “handbook first, HTML second, recording materials last.” The handbook records the approved course facts, HTML provides the online presentation, and recording materials are based on the approved handbook and page.

The original handbook Markdown and the source content for the HTML interface are stored in the `rdk-course-demos` repository.
