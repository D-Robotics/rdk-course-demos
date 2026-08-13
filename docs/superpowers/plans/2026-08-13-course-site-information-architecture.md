# RDK 小课堂信息架构实施计划

> **供执行本计划的智能体使用：** 必须使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` 子技能，逐项实施本计划。每个步骤使用复选框（`- [ ]`）跟踪进度。

**目标：** 将已确认的课程介绍合并到首页，移除公开页面中的课程序号，并把“基础入门”组织为通用基础、RDK X5 和 RDK S100 三条学习路径。

**架构：** 中英文首页成为课程介绍的唯一内容来源。通用基础课程保持共用，其余动手实践类基础主题分别进入 X5 与 S100 路径；后续课程体系暂时保持通用。通过一组精简的 `unittest` 回归测试，在每次 MkDocs 严格构建前检查源文件结构。

**技术栈：** MkDocs Material、`mkdocs-static-i18n`、Markdown、YAML、Python 3 标准库 `unittest`。

## 全局约束

- 仅使用 `docs/index.md` 和 `docs/index.zh.md` 作为公开课程介绍的内容来源。
- “社区与生态”“产品介绍”和“RDK Studio”属于通用基础主题。
- “社区与生态”保持为独立课程，不按开发板拆分。
- 其余基础入门主题分别列在 RDK X5 和 RDK S100 路径下。
- ModelZoo 与 RoboGo、TROS、系统与驱动、大模型与具身智能、开发者案例暂时保持通用。
- 公开内容不得使用 `第 N 课`、`Lesson N` 或 `01 ·` 之类的序号前缀。
- 仓库内部带序号的目录不得重命名或移动。
- 只有已经确认且实际存在的讲义才能成为可点击页面；尚未发布的主题只保留规划项，不虚构技术内容。
- 中英文导航与课程目录的结构必须一致。
- 尚未对外分享的 `/course-overview/` 页面可以直接删除，无需设置重定向。

---

## 文件清单

- `tests/test_course_site_structure.py`：检查首页归属、公开命名、开发板路径分类和双语一致性的回归测试。
- `tests/__init__.py`：使 `unittest` 可以导入回归测试目录。
- `docs/index.md`：完整的英文课程介绍与课程目录。
- `docs/index.zh.md`：完整的中文课程介绍与课程目录。
- `docs/course-overview.md`：内容复制到首页后删除。
- `docs/course-overview.zh.md`：内容复制到首页后删除。
- `docs/beginner/index.md`：精简的英文通用/X5/S100 路径选择页。
- `docs/beginner/index.zh.md`：精简的中文通用/X5/S100 路径选择页。
- `docs/beginner/01-community-ecosystem.md`：移除课程序号后的英文公开标题与跨课程表述。
- `docs/beginner/01-community-ecosystem.zh.md`：移除课程序号后的中文公开标题与跨课程表述。
- `docs/beginner/03-rdk-studio.md`：移除课程序号后的英文公开标题。
- `docs/beginner/03-rdk-studio.zh.md`：移除课程序号后的中文公开标题。
- `mkdocs.yml`：按主题组织的双语导航，不包含序号标签或单独的“课程介绍”入口。

---

### 任务 1：让首页成为唯一的课程介绍页面

**文件：**
- 新建：`tests/__init__.py`
- 新建：`tests/test_course_site_structure.py`
- 修改：`docs/index.md`
- 修改：`docs/index.zh.md`
- 删除：`docs/course-overview.md`
- 删除：`docs/course-overview.zh.md`
- 修改：`mkdocs.yml`

**接口关系：**
- 输入：当前 `docs/course-overview.md` 与 `docs/course-overview.zh.md` 中已经评审通过的完整内容。
- 输出：`docs/index.md` 与 `docs/index.zh.md` 成为唯一的公开课程介绍文件；提供 `CourseSiteStructureTests.project_root` 给后续回归测试使用。

- [ ] **步骤 1：添加一个当前必然失败的“首页唯一归属”回归测试**

创建空文件 `tests/__init__.py`，并创建 `tests/test_course_site_structure.py`，内容如下：

```python
from pathlib import Path
import unittest


class CourseSiteStructureTests(unittest.TestCase):
    project_root = Path(__file__).resolve().parents[1]

    def read(self, relative_path: str) -> str:
        return (self.project_root / relative_path).read_text(encoding="utf-8")

    def test_home_is_the_single_course_overview(self) -> None:
        self.assertFalse((self.project_root / "docs/course-overview.md").exists())
        self.assertFalse((self.project_root / "docs/course-overview.zh.md").exists())

        english = self.read("docs/index.md")
        chinese = self.read("docs/index.zh.md")
        config = self.read("mkdocs.yml")

        for heading in (
            "# RDK Course Overview",
            "# Who This Course Is For",
            "# Recommended Learning Approach",
            "# Course Resources",
            "# Recommended Learning Path",
            "# Curriculum",
        ):
            self.assertIn(heading, english)

        for heading in (
            "# RDK 小课堂课程介绍",
            "# 课程适合谁",
            "# 推荐学习方式",
            "# 课程资源说明",
            "# 学习路径建议",
            "# 课程目录",
        ):
            self.assertIn(heading, chinese)

        self.assertNotIn("course-overview.md", config)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **步骤 2：运行新测试，确认当前双页面结构会失败**

运行：

```powershell
python -m unittest tests.test_course_site_structure.CourseSiteStructureTests.test_home_is_the_single_course_overview -v
```

预期：`FAIL`。原因是 `docs/course-overview.md` 和 `docs/course-overview.zh.md` 仍然存在，而且当前首页尚未包含完整的已评审课程介绍。

- [ ] **步骤 3：将已评审的课程介绍内容迁移到首页**

删除原页面之前，先完整复制当前内容：

```powershell
Copy-Item -LiteralPath docs/course-overview.md -Destination docs/index.md
Copy-Item -LiteralPath docs/course-overview.zh.md -Destination docs/index.zh.md
```

然后删除：

```text
docs/course-overview.md
docs/course-overview.zh.md
```

在 `mkdocs.yml` 中删除以下导航项：

```yaml
- Course introduction: course-overview.md
```

此时不要修改复制过来的事实性介绍；任务 2 和任务 3 只处理公开命名与课程目录组织。

- [ ] **步骤 4：运行该项回归测试**

运行：

```powershell
python -m unittest tests.test_course_site_structure.CourseSiteStructureTests.test_home_is_the_single_course_overview -v
```

预期：`PASS`。

- [ ] **步骤 5：严格构建网站**

运行：

```powershell
python -m mkdocs build --strict
```

预期：退出码为 `0`；英文站点生成在根目录，中文站点生成在 `site/zh` 下。

- [ ] **步骤 6：提交首页单一内容源改动**

```powershell
git add tests docs/index.md docs/index.zh.md docs/course-overview.md docs/course-overview.zh.md mkdocs.yml
git commit -m "docs: merge course introduction into home"
```

---

### 任务 2：移除公开课程页面与导航中的序号标签

**文件：**
- 修改：`tests/test_course_site_structure.py`
- 修改：`docs/beginner/01-community-ecosystem.md`
- 修改：`docs/beginner/01-community-ecosystem.zh.md`
- 修改：`docs/beginner/03-rdk-studio.md`
- 修改：`docs/beginner/03-rdk-studio.zh.md`
- 修改：`mkdocs.yml`

**接口关系：**
- 输入：任务 1 建立的首页唯一归属关系。
- 输出：只按主题命名的公开标题与导航分组标签；提供 `public_markdown_files()`，供任务 3 最终检查全站公开命名。

- [ ] **步骤 1：为通用课程标题与导航标签添加当前必然失败的测试**

在 `CourseSiteStructureTests` 中加入以下导入与方法：

```python
import re

    def public_markdown_files(self) -> list[Path]:
        return [
            path
            for path in (self.project_root / "docs").rglob("*.md")
            if "superpowers" not in path.parts
        ]

    def test_common_course_titles_are_topic_based(self) -> None:
        expected_titles = {
            "docs/beginner/01-community-ecosystem.md": "# RDK Community and Ecosystem",
            "docs/beginner/01-community-ecosystem.zh.md": "# RDK 社区与生态",
            "docs/beginner/03-rdk-studio.md": "# Getting Started with RDK Studio",
            "docs/beginner/03-rdk-studio.zh.md": "# RDK Studio 入门",
        }
        for relative_path, expected_title in expected_titles.items():
            first_line = self.read(relative_path).splitlines()[0]
            self.assertEqual(expected_title, first_line)

    def test_navigation_uses_topic_groups(self) -> None:
        config = self.read("mkdocs.yml")
        for forbidden in (
            "01 · Fundamentals",
            "02 · ModelZoo & RoboGo",
            "03 · TROS",
            "04 · System & drivers",
            "05 · LLMs & embodied AI",
        ):
            self.assertNotIn(forbidden, config)
        for required in (
            "- Fundamentals:",
            "- ModelZoo & RoboGo:",
            "- TROS:",
            "- System & drivers:",
            "- LLMs & embodied AI:",
        ):
            self.assertIn(required, config)
```

- [ ] **步骤 2：运行两项新测试，确认当前标题与导航会失败**

运行：

```powershell
python -m unittest tests.test_course_site_structure.CourseSiteStructureTests.test_common_course_titles_are_topic_based tests.test_course_site_structure.CourseSiteStructureTests.test_navigation_uses_topic_groups -v
```

预期：`FAIL`。原因是“社区与生态”页面标题仍包含 `Lesson 1` / `第一课`，Studio 英文标题仍包含 `Lesson 03`，导航分组也仍使用序号前缀。

- [ ] **步骤 3：替换四个公开页面标题及带序号的跨课程引用**

严格执行以下标题变更：

```text
# RDK Lesson 1: Community and Ecosystem Introduction
→ # RDK Community and Ecosystem

# RDK 第一课：RDK 社区与生态入门
→ # RDK 社区与生态

# RDK Lesson 03: Getting Started with RDK Studio
→ # Getting Started with RDK Studio

# RDK 第三课：RDK Studio 入门
→ # RDK Studio 入门
```

在“社区与生态”中英文讲义中，将 `covered in Lesson 3` / `第三课将专门介绍` 等表述替换为 `covered in the RDK Studio course` / `RDK Studio 课程将专门介绍`。将结尾的 `next lesson` / `下一课` 改成不带序号、引导继续阅读“产品介绍”的表述。

- [ ] **步骤 4：替换带序号的导航分组名称**

英文导航与 `nav_translations` 使用以下公开分组名称：

```yaml
Fundamentals
ModelZoo & RoboGo
TROS
System & drivers
LLMs & embodied AI
```

使用以下中文翻译：

```yaml
Fundamentals: 基础入门
ModelZoo & RoboGo: ModelZoo 与 RoboGo
TROS: TROS
System & drivers: 系统与驱动
LLMs & embodied AI: 大模型与具身智能
```

保持所有内部文件和目录路径不变。

- [ ] **步骤 5：运行标题与导航测试**

运行：

```powershell
python -m unittest tests.test_course_site_structure.CourseSiteStructureTests.test_common_course_titles_are_topic_based tests.test_course_site_structure.CourseSiteStructureTests.test_navigation_uses_topic_groups -v
```

预期：两项测试均为 `PASS`。

- [ ] **步骤 6：构建并提交命名改动**

运行：

```powershell
python -m mkdocs build --strict
git add tests docs/beginner/01-community-ecosystem.md docs/beginner/01-community-ecosystem.zh.md docs/beginner/03-rdk-studio.md docs/beginner/03-rdk-studio.zh.md mkdocs.yml
git commit -m "docs: use topic-based course names"
```

预期：严格构建成功，提交中不包含任何目录重命名。

---

### 任务 3：建立通用、X5 与 S100 三类基础入门路径

**文件：**
- 修改：`tests/test_course_site_structure.py`
- 修改：`docs/index.md`
- 修改：`docs/index.zh.md`
- 修改：`docs/beginner/index.md`
- 修改：`docs/beginner/index.zh.md`
- 修改：`mkdocs.yml`

**接口关系：**
- 输入：任务 2 产出的纯主题通用页面名称与导航分组。
- 输出：首页、路径选择页和侧边栏中最终确定的基础入门分类。

- [ ] **步骤 1：添加当前必然失败的路径分类与公开序号测试**

在 `CourseSiteStructureTests` 中添加以下方法：

```python
    def test_fundamentals_have_common_x5_and_s100_groups(self) -> None:
        english_files = [self.read("docs/index.md"), self.read("docs/beginner/index.md")]
        chinese_files = [self.read("docs/index.zh.md"), self.read("docs/beginner/index.zh.md")]

        for text in english_files:
            for heading in ("Common foundation", "RDK X5", "RDK S100"):
                self.assertIn(heading, text)
            for topic in ("Community and Ecosystem", "Product Overview", "RDK Studio"):
                self.assertIn(topic, text)

        for text in chinese_files:
            for heading in ("通用基础", "RDK X5", "RDK S100"):
                self.assertIn(heading, text)
            for topic in ("社区与生态", "产品介绍", "RDK Studio"):
                self.assertIn(topic, text)

        board_topics_en = (
            "System Flashing",
            "Boot and Troubleshooting",
            "Remote Connection",
            "Camera",
            "Audio",
            "Display",
            "Video Codec",
            "GPIO and PWM",
            "UART and I2C",
            "SPI",
            "CAN",
        )
        board_topics_zh = (
            "系统烧录",
            "启动与问题排查",
            "远程连接",
            "Camera",
            "Audio",
            "显示",
            "编解码",
            "GPIO 与 PWM",
            "UART 与 I2C",
            "SPI",
            "CAN",
        )

        for text in english_files:
            for topic in board_topics_en:
                self.assertGreaterEqual(text.count(topic), 2, topic)
        for text in chinese_files:
            for topic in board_topics_zh:
                self.assertGreaterEqual(text.count(topic), 2, topic)

    def test_public_docs_do_not_expose_lesson_ordinals(self) -> None:
        forbidden_patterns = (
            re.compile(r"Lesson\s+\d+", re.IGNORECASE),
            re.compile(r"第\s*\d+\s*课"),
            re.compile(r"^#{1,6}\s+(?:\d+|[IVX]+)[.、·]\s+", re.MULTILINE),
            re.compile(r"^\|\s*(?:\d+|Lesson\s+\d+|第\s*\d+\s*课)\s*\|", re.MULTILINE | re.IGNORECASE),
        )
        for path in self.public_markdown_files():
            text = path.read_text(encoding="utf-8")
            for pattern in forbidden_patterns:
                self.assertIsNone(pattern.search(text), f"{path}: {pattern.pattern}")
```

- [ ] **步骤 2：运行新路径测试，确认当前课程目录会失败**

运行：

```powershell
python -m unittest tests.test_course_site_structure.CourseSiteStructureTests.test_fundamentals_have_common_x5_and_s100_groups tests.test_course_site_structure.CourseSiteStructureTests.test_public_docs_do_not_expose_lesson_ordinals -v
```

预期：`FAIL`。原因是复制后的课程介绍仍然使用带序号的表格，而且基础入门概览尚未分别在两块开发板路径下列出全部主题。

- [ ] **步骤 3：重写中英文首页中的基础入门课程目录**

保留复制过来的全部已确认说明。将单个带序号的基础入门表格替换为以下三个不带序号的中英文分组：

```text
Common foundation / 通用基础
  Community and Ecosystem / 社区与生态
  Product Overview / 产品介绍
  RDK Studio

RDK X5
  System Flashing / 系统烧录
  Boot and Troubleshooting / 启动与问题排查
  Remote Connection / 远程连接
  Camera
  Audio
  Display / 显示
  Video Codec / 编解码
  GPIO and PWM / GPIO 与 PWM
  UART and I2C / UART 与 I2C
  SPI
  CAN

RDK S100
  System Flashing / 系统烧录
  Boot and Troubleshooting / 启动与问题排查
  Remote Connection / 远程连接
  Camera
  Audio
  Display / 显示
  Video Codec / 编解码
  GPIO and PWM / GPIO 与 PWM
  UART and I2C / UART 与 I2C
  SPI
  CAN
```

使用三列表格：英文为 `Topic | Focus | Materials`，中文为 `主题 | 内容重点 | 配套资料`。仅链接以下已经存在并通过确认的页面：

- 社区与生态；
- RDK Studio；
- X5 与 S100 系统烧录；
- X5 与 S100 启动和问题排查；
- X5 SPI 示例。

“产品介绍”与尚未发布的开发板主题保持为纯文本，并保留现有的已确认内容说明；适用时同时保留对应的仓库目录地址。

- [ ] **步骤 4：移除后续通用课程体系中的序号**

对于 ModelZoo 与 RoboGo，删除 `No.` / `序号` 列，按当前顺序完整保留所有既有主题、说明和资料类型。移除所有模块标题中的罗马数字或中文序号前缀：

```text
Advanced: ModelZoo and RoboGo Development Guide
Advanced: TROS Development Guide
Advanced: System and Driver Development Guide
Large Language Models and Embodied Intelligence
Developer Cases
```

```text
ModelZoo 与 RoboGo 开发指南
TROS 开发指南
系统驱动开发指南
大语言模型与具身智能
开发者案例
```

这些后续课程体系暂不按开发板拆分。

- [ ] **步骤 5：重写精简的基础入门路径选择页**

重写 `docs/beginner/index.md` 和 `docs/beginner/index.zh.md`，内容包括：

- 一段简短的基础入门介绍；
- 一个通用基础表格，包含“社区与生态”“产品介绍”和 RDK Studio；
- 一个 RDK X5 表格，包含全部 11 个开发板专属主题；
- 一个 RDK S100 表格，包含全部 11 个开发板专属主题；
- 不设置课程序号列；
- 只有已发布页面提供可点击的讲义链接；
- 尚无讲义的规划主题提供 GitHub 仓库目录链接。

该页面只负责引导用户选择路径，不重复首页中的适用人群、课程资源或内容生产关系等章节。

- [ ] **步骤 6：让侧边栏与已发布路径保持一致**

在 `mkdocs.yml` 中使用以下结构：

```yaml
- Fundamentals:
    - Course routes: beginner/index.md
    - Common foundation:
        - Community & ecosystem: beginner/01-community-ecosystem.md
        - RDK Studio: beginner/03-rdk-studio.md
    - RDK X5:
        - System flashing: beginner/04-flash-system-x5.md
        - Boot & troubleshooting: beginner/05-boot-troubleshooting-x5.md
        - SPI display: hardware/spi-display.md
    - RDK S100:
        - System flashing: beginner/04-flash-system-s100.md
        - Boot & troubleshooting: beginner/05-boot-troubleshooting-s100.md
```

在公开讲义存在之前，不要把“产品介绍”或其他规划主题加入侧边栏。为每个已显示标签添加对应的中文 `nav_translations`。

- [ ] **步骤 7：运行路径与公开序号测试**

运行：

```powershell
python -m unittest tests.test_course_site_structure.CourseSiteStructureTests.test_fundamentals_have_common_x5_and_s100_groups tests.test_course_site_structure.CourseSiteStructureTests.test_public_docs_do_not_expose_lesson_ordinals -v
```

预期：两项测试均为 `PASS`。

- [ ] **步骤 8：运行完整回归测试与严格构建**

运行：

```powershell
python -m unittest tests.test_course_site_structure -v
python -m mkdocs build --strict
```

预期：所有测试通过，MkDocs 退出码为 `0`。

- [ ] **步骤 9：提交路径信息架构改动**

```powershell
git add tests docs/index.md docs/index.zh.md docs/beginner/index.md docs/beginner/index.zh.md mkdocs.yml
git commit -m "docs: split fundamentals by board path"
```

---

### 任务 4：验证双语输出与发布准备状态

**文件：**
- 如验证发现缺陷则修改：`tests/test_course_site_structure.py`
- 如验证发现缺陷则修改：不符合设计的具体 Markdown 或 YAML 源文件

**接口关系：**
- 输入：任务 1～3 形成的最终源文件结构。
- 输出：一个工作区干净、回归测试全部通过且可严格构建双语 MkDocs 站点的分支。

- [ ] **步骤 1：添加双语结构一致性测试**

在 `CourseSiteStructureTests` 中添加以下方法：

```python
    def test_bilingual_route_structure_matches(self) -> None:
        english_home = self.read("docs/index.md")
        chinese_home = self.read("docs/index.zh.md")
        english_routes = self.read("docs/beginner/index.md")
        chinese_routes = self.read("docs/beginner/index.zh.md")

        pairs = (
            ("Common foundation", "通用基础"),
            ("RDK X5", "RDK X5"),
            ("RDK S100", "RDK S100"),
            ("ModelZoo and RoboGo", "ModelZoo 与 RoboGo"),
            ("TROS Development Guide", "TROS 开发指南"),
            ("System and Driver Development Guide", "系统驱动开发指南"),
            ("Developer Cases", "开发者案例"),
        )
        for english_label, chinese_label in pairs:
            self.assertIn(english_label, english_home)
            self.assertIn(chinese_label, chinese_home)

        for english_label, chinese_label in pairs[:3]:
            self.assertIn(english_label, english_routes)
            self.assertIn(chinese_label, chinese_routes)
```

- [ ] **步骤 2：运行全部源文件结构测试**

```powershell
python -m unittest tests.test_course_site_structure -v
```

预期：所有测试均为 `PASS`。

- [ ] **步骤 3：扫描公开源文件中的禁用序号与已删除链接**

运行：

```powershell
$publicDocs = Get-ChildItem docs -Recurse -File -Filter *.md |
  Where-Object { $_.FullName -notmatch '[\\/]superpowers[\\/]' }

$forbidden = $publicDocs | Select-String -Pattern 'Lesson\s+\d+|第\s*\d+\s*课|^#{1,6}\s+(\d+|[IVX]+)[\.、·]\s+' -CaseSensitive:$false
if ($forbidden) { $forbidden; exit 1 }

$overviewRefs = Get-ChildItem docs,mkdocs.yml -Recurse -File |
  Select-String -SimpleMatch 'course-overview.md'
if ($overviewRefs) { $overviewRefs; exit 1 }
```

预期：无输出，退出码为 `0`。

- [ ] **步骤 4：运行与正式发布等价的严格构建**

```powershell
python -m mkdocs build --strict
```

预期：英文输出位于 `site/`，中文输出位于 `site/zh/`，退出码为 `0`。

- [ ] **步骤 5：检查生成后的导航与关键页面**

运行：

```powershell
rg -n "Common foundation|RDK X5|RDK S100|Community and Ecosystem" site/index.html site/beginner/index.html
rg -n "通用基础|RDK X5|RDK S100|社区与生态" site/zh/index.html site/zh/beginner/index.html
```

预期：中英文站点都显示三个基础入门分组以及独立的“社区与生态”课程；导航中不再出现单独的“课程介绍”入口。

- [ ] **步骤 6：检查当前分支的完整差异**

```powershell
git diff develop...HEAD --check
git diff develop...HEAD --stat
git status -sb
```

预期：没有空白字符错误；变更范围仅包括设计/计划文档、测试、首页、基础入门源文件、通用讲义标题和 `mkdocs.yml`；工作区保持干净。

- [ ] **步骤 7：如本任务产生文件改动，提交最终一致性测试或修复**

如果步骤 1 或验证修复产生了文件改动：

```powershell
git add tests docs mkdocs.yml
git commit -m "test: verify bilingual course routes"
```

如果任务 3 完成后没有新增文件改动，则不要创建空提交。
