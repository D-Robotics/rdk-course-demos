# RDK Community and Ecosystem

RDK resources extend beyond board manuals. They also include source repositories, model examples, robotics documentation, development tools, application cases, and technical communities.

This lesson does not run a demo or teach a specific hardware or algorithm workflow. It focuses on one goal: building a clear map of the RDK ecosystem so that you know where to look first when a development need arises.

## 1. What Problem Does This Lesson Solve?

When people first use RDK, the main difficulty is often not entering commands, but choosing the correct starting point:

- Which manual should you use for board interfaces, system configuration, or getting-started instructions?
- Should you use GitHub or Model Zoo when looking for source code or BPU models?
- Where can you find the TROS manual and related source code for robotics development?
- What information should you prepare before reporting a problem?

This lesson follows the shortest path through these four tasks: find the manual, find source code and models, find TROS resources, and find the correct feedback channel.

## 2. What You Will Be Able to Do

After completing this lesson, you will be able to:

1. Find the correct RDK X Series or RDK S Series manual and, using RDK X5 as an example, locate the video codec APIs;
2. Identify official repositories in D-Robotics GitHub and RDK Model Zoo, select the branch for your board, and find the target README before taking action;
3. Find the official TogetheROS.Bot (TROS) manual and source-code entry points, and understand their different roles;
4. Find the forum and its new-topic entry point, then prepare a problem description that other developers can reproduce.

### 2.1 Eight Terms to Know First

Before opening the individual sites, establish the following eight concepts. At this stage, you only need to understand the role of each term; implementation details come later.

| Term | Meaning |
|---|---|
| RDK | Robotics Development Kit, a platform for robotics and intelligent-application development. |
| BPU | Brain Processing Unit, the on-board AI inference accelerator in an RDK device. |
| RDK OS | The Linux system image for RDK boards, including platform drivers and the runtime environment. |
| miniboot | The RDK boot program; its version matters when diagnosing boot and some low-level issues. |
| TROS | TogetheROS.Bot, a robotics application platform compatible with ROS 2 interfaces. |
| Model Zoo | A collection of model examples and tools for RDK and its BPU. |
| RDK Studio | An AI-native development workspace for RDK devices. |
| NodeHub | An additional application-case entry for learning about existing solutions and usage scenarios. |

## 3. Before You Start

You do not need to connect an RDK board for this lesson. You only need a computer with Internet access and a browser.

It is useful to confirm your board model in advance, such as RDK X3, RDK X5, RDK S100, or RDK S600. The board series affects which manual, Model Zoo branch, and example code you should use.

The bilingual handbooks, original page content, and supporting demos for this course are stored in the `rdk-course-demos` repository and published through GitHub Pages:

- [English course handbooks](https://d-robotics.github.io/rdk-course-demos/)
- [Chinese course handbooks](https://d-robotics.github.io/rdk-course-demos/zh/)
- [Handbook and demo source files](https://github.com/D-Robotics/rdk-course-demos)

## 4. Start with the Resource Map

Choose an entry point according to the problem you need to solve:

| Your need | Start here | What to look for |
|---|---|---|
| Board interfaces, system installation, configuration, or common issues | RDK Resource Center and the manual for your board | Quick Start, System Configuration, Basic Application Development, FAQs |
| Open-source projects and implementation details | D-Robotics GitHub | Repositories, README files, source code, Issues |
| BPU model deployment examples | RDK Model Zoo | Board branches, model directories, README files |
| ROS 2 / TROS robotics development | TROS manual and GitHub | Usage paths, packages, source code, Issues |
| A development workspace for RDK devices | RDK Studio | Device-development entry point; covered in the RDK Studio course |
| Existing solutions and application scenarios | NodeHub | Additional application-case entry point |
| Questions, problem reports, and experience sharing | D-Robotics Forum | Technical discussions, support questions, and shared experience |

Remember one simple rule: **start with the manual for your board, move to source code or models according to the task, and report problems with complete information.**

## 5. Task 1: Find the Official Manual for Your Board

### 5.1 Choose the Board Series in the Resource Center

Open the [D-Robotics Resource Center](https://d-robotics.github.io/rdk_doc_center/en/). In the RDK User Manual section, you will find two main entries:

- **RDK X3/X5 User Manual**: for products such as RDK X3, RDK X5, and RDK X5 Module;
- **RDK S Series User Manual**: for products such as RDK S100, RDK S100P, and RDK S600.

Do not begin by searching for a command. First identify the board series, then enter the matching manual.

### 5.2 Use RDK X5 to Find the Codec APIs

Suppose you need the Python video encoding or decoding APIs for RDK X5. You can find them either through the navigation tree or through search.

**Using the navigation tree:**

1. Open the **RDK X3/X5 User Manual** from the Resource Center;
2. Confirm that the current product is **RDK X5**;
3. Navigate to **3 Basic Application Development → 3.6 API Reference → RDK X5 → Python Interface**;
4. Open the **[Encoder Object](https://d-robotics.github.io/rdk_x_doc/en/Basic_Application/multi_media_sp_dev_api/RDK_X3/pydev_multimedia_api_x3/object_encoder?v=3.5.0&p=RDK+X5)** or **[Decoder Object](https://d-robotics.github.io/rdk_x_doc/en/Basic_Application/multi_media_sp_dev_api/RDK_X3/pydev_multimedia_api_x3/object_decoder?v=3.5.0&p=RDK+X5)** page;
5. Use the **API Reference** section to review the encoding or decoding interfaces.

**Using search:**

1. Select the search box in the upper-right corner of the manual;
2. Search for `Encoder`, `Decoder`, `encoding`, `decoding`, or a specific interface name;
3. Open the Encoder or Decoder Object page under the **RDK X5 Python Interface**;
4. Confirm that the selected product is RDK X5, then review the **API Reference**.

The goal is not to memorize one API. It is to learn a repeatable path:

> Confirm the board series and product → use 3.6 Python Interface or search → find Encoder / Decoder Object → review the API Reference

You can reuse the same approach for system flashing, remote login, display output, network configuration, or 40-pin interfaces. When search returns several results, confirm the manual, board model, and section before using an interface description.

### 5.3 Completion Check

Task 1 is complete when you can:

- Explain whether your board belongs to the RDK X Series or RDK S Series documentation;
- Use either the navigation tree or upper-right search to find the Encoder or Decoder Object and its API Reference under the RDK X5 Python Interface.

## 6. Task 2: Find Source Code and Models

### 6.1 What D-Robotics GitHub Is For

[D-Robotics GitHub](https://github.com/D-Robotics) is the official entry point for open-source repositories. It includes RDK documentation sources, TROS-related packages, system projects, model examples, and other open-source components.

When you enter a repository, confirm three things first:

1. The repository name and purpose match your task;
2. The selected branch supports your board;
3. The README explains the dependencies, directory structure, and intended workflow.

### 6.2 What Model Zoo Is For

[RDK Model Zoo](https://github.com/D-Robotics/rdk_model_zoo) is D-Robotics' collection of BPU model examples and tools for model deployment and intelligent application development.

Model Zoo maintains hardware-specific branches. Select the branch for your board before reading or using an example:

| Target hardware | Branch | Example entry point |
|---|---|---|
| RDK X5 | `rdk_x5` | `samples/vision/<sample>/README.md` |
| RDK X5 legacy examples | `rdk_x5_legacy` | README in the target example directory |
| RDK X3 | `rdk_x3` | `demos/<task>/<demo>/README.md` |
| RDK S Series | `rdk_s` | `samples/<domain>/<sample>/README.md` |

For this lesson, remember only three steps:

1. Open the official repository;
2. Select the branch for your board;
3. Enter the target example directory and read its README first.

Do not copy commands from another hardware branch. Directory structures, system requirements, and inference interfaces can differ. The README in the target directory is the direct guide for that example.

### 6.3 Completion Check

Task 2 is complete when you can select the branch for your board in Model Zoo and locate a README in a target example directory. You do not need to download code or run a model in this lesson.

## 7. Task 3: Find the TROS Manual and Source Code

TogetheROS.Bot, or TROS, is a robot operating system provided by D-Robotics for robotics application development. It is compatible with ROS 2 interfaces and provides capabilities for sensor access, model inference, image processing, data communication, and visualization on RDK platforms.

TROS resources have two main entry points:

- [TROS User Manual](https://d-robotics.github.io/tros_doc/en/tros/): concepts, installation and usage paths, feature descriptions, and application examples;
- [D-Robotics GitHub](https://github.com/D-Robotics): specific packages, source code, README files, and Issues.

When you need a specific package, start from its page in the TROS manual, follow the official repository link, and then read that repository's README and Issues.

Use this simple distinction:

- To understand what something is and how it is used, start with the manual;
- To inspect how it is implemented or review known problems, use the GitHub repository, README, and Issues.

This lesson does not install TROS, run nodes, or teach package development.

## 8. Additional Entry Points: RDK Studio and NodeHub

### 8.1 RDK Studio

[RDK Studio](https://d-robotics.github.io/rdk_studio_doc/en/category/1-product-intro/) is an AI-native development workspace for RDK devices and can serve as an entry point for device development. The RDK Studio course covers how to use it.

### 8.2 NodeHub

[NodeHub](https://developer.d-robotics.cc/en/nodehub) is an additional entry point for application cases. You can use it to learn about existing solutions and usage scenarios; this lesson does not cover its search or execution workflow.

## 9. How to Report a Problem

### 9.1 Choose the Feedback Channel

There are two common feedback channels:

- [D-Robotics Forum](https://forum-en.d-robotics.cc/): general usage questions, environment problems, experience sharing, and application discussions;
- GitHub Issues: problems that you have already traced to a specific open-source repository and can describe with the relevant branch, version, and reproduction information.

For Chinese discussions, use the [Chinese D-Robotics Forum](https://forum.d-robotics.cc/).

### 9.2 Find the New-Topic Entry Point

Open the forum and sign in, then use the new-topic entry point on the forum page. Select the category and tags that most closely match the problem.

In this lesson, you only need to recognize this entry point. Do not search, fill out, or publish a post as part of the lesson.

### 9.3 What an Effective Problem Report Includes

Prepare at least these seven items before posting:

1. **Board model**: for example, RDK X5;
2. **System or software version**: RDK OS, TROS, package, or tool versions;
3. **Reproduction steps**: the starting state and the exact sequence of actions;
4. **Expected result**: what should happen under normal conditions;
5. **Actual result**: the observed behavior or error;
6. **Key logs**: include enough context instead of only the final error line;
7. **Troubleshooting already attempted**: manuals, versions, connections, configuration, or Issues already checked.

A useful title includes the board, task, and symptom, for example:

> RDK X5 video encoding API does not return an encoded stream

This is easier to diagnose than a title such as “Encoding does not work, please help.”

## 10. How to Know You Have Completed the Lesson

You have built a basic map of the RDK community and ecosystem when you can complete these four tasks:

- [ ] Open the correct user manual for a board series and find one specific topic;
- [ ] Select the correct Model Zoo branch and find the README for a target example;
- [ ] Find both the TROS user manual and a source-code entry point;
- [ ] Find the forum's new-topic entry point and list the seven items required for an effective problem report.

## 11. Frequently Asked Questions

### Q1: What should I do if the manual page does not match my board?

Return to the Resource Center and confirm whether you need the RDK X Series or RDK S Series manual. Then verify the selected product on the page. Do not apply steps for another series or board directly to your device.

### Q2: Why should I not copy commands directly from the default Model Zoo page?

Model Zoo uses hardware-specific branches, and directory structures and interfaces can differ. Select the branch for your board first, then read the README in the target directory.

### Q3: Should I read the TROS manual or GitHub first?

Start with the manual when learning a capability for the first time. Move to GitHub when you need source code, implementation details, customization, or issue tracking.

### Q4: What is the difference between NodeHub and Model Zoo?

NodeHub is an additional application-case entry point for learning about existing solutions and usage scenarios. Model Zoo focuses on BPU model examples and model deployment workflows.

### Q5: When should I use GitHub Issues?

Use GitHub Issues when a problem clearly belongs to a specific official repository and you can provide the repository, branch, version, reproduction steps, and logs. General usage questions can start in the forum.

## 12. Lesson Summary

The most important result of this lesson is not a list of URLs, but a lookup sequence:

1. **Find the manual by board**: distinguish the RDK X Series from the RDK S Series;
2. **Find source code and models by task**: GitHub for open-source projects, Model Zoo for BPU model examples;
3. **Use manuals and source code together**: the TROS manual explains the usage path, while GitHub provides packages, source code, and Issues;
4. **Use supplementary entries at the right depth**: RDK Studio is a device-development entry point, while NodeHub introduces application cases;
5. **Report problems with complete information**: board, version, steps, expected result, actual result, logs, and previous troubleshooting.

Continue with **RDK Product Overview** to learn the positioning of different RDK products and how to choose between them.

## 13. Further Practice

1. Open the user manual for your board from the Resource Center and find a topic related to your current task;
2. Open Model Zoo, select the branch for your board, and record one example directory and its README location;
3. Open the TROS manual, then follow a source link to one `hobot_*` package;
4. Use the appendix template to draft the title and details for a hypothetical problem report.

## 14. Appendix

### Appendix A: Problem Information Template

```text
Title: [Board model] + [Task] + [Symptom]

1. Board model

2. System and software versions

3. Manual, repository, branch, or README used

4. Reproduction steps

5. Expected result

6. Actual result

7. Key logs or screenshots

8. Troubleshooting already attempted and its result
```

### Appendix B: Core Resource Quick Reference

| Resource | URL | Purpose |
|---|---|---|
| D-Robotics Resource Center | <https://d-robotics.github.io/rdk_doc_center/en/> | Entry point for official manuals |
| RDK X3/X5 User Manual | <https://d-robotics.github.io/rdk_x_doc/en/RDK/> | Documentation for X3, X5, and related products |
| RDK S Series User Manual | <https://d-robotics.github.io/rdk_s_doc/en/RDK/> | Documentation for S100, S600, and related products |
| D-Robotics GitHub | <https://github.com/D-Robotics> | Official open-source repositories |
| RDK Model Zoo | <https://github.com/D-Robotics/rdk_model_zoo> | BPU model examples and tools |
| TROS User Manual | <https://d-robotics.github.io/tros_doc/en/tros/> | TROS concepts and usage paths |
| RDK Studio | <https://d-robotics.github.io/rdk_studio_doc/en/category/1-product-intro/> | Development workspace for RDK devices |
| NodeHub | <https://developer.d-robotics.cc/en/nodehub> | Additional application-case entry point |
| English Forum | <https://forum-en.d-robotics.cc/> | English technical discussions and feedback |
| Chinese Forum | <https://forum.d-robotics.cc/> | Chinese technical discussions and feedback |
