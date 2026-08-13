# RDK Classroom Information Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge the approved course introduction into the homepage, remove public lesson numbering, and organize Fundamentals into common, RDK X5, and RDK S100 learning paths.

**Architecture:** The bilingual homepage becomes the single course-overview content source. Common foundation courses remain shared, while hands-on Fundamentals topics are represented in parallel X5 and S100 routes; later course lines remain common. A small `unittest` regression suite validates source structure before every strict MkDocs build.

**Tech Stack:** MkDocs Material, `mkdocs-static-i18n`, Markdown, YAML, Python 3 standard-library `unittest`.

## Global Constraints

- Use `docs/index.md` and `docs/index.zh.md` as the only public course-introduction source.
- Community and Ecosystem, Product Overview, and RDK Studio are common Fundamentals topics.
- Community and Ecosystem remains a standalone course and is not split by board.
- All other Fundamentals topics are listed separately under RDK X5 and RDK S100.
- ModelZoo and RoboGo, TROS, System and Drivers, Large Models and Embodied AI, and Developer Cases remain common.
- Public content must not use `第 N 课`, `Lesson N`, or ordinal course prefixes such as `01 ·`.
- Internal numbered repository directories must not be renamed or moved.
- Only approved, existing handbooks become clickable pages; missing topics remain planned entries without invented technical content.
- English and Chinese navigation and curriculum structures must match.
- The unpublished `/course-overview/` page may be removed without a redirect.

---

## File Map

- `tests/test_course_site_structure.py`: regression checks for homepage ownership, public naming, board-route classification, and bilingual parity.
- `tests/__init__.py`: makes the regression test directory importable by `unittest`.
- `docs/index.md`: complete English course introduction and curriculum.
- `docs/index.zh.md`: complete Chinese course introduction and curriculum.
- `docs/course-overview.md`: remove after its content is copied into the homepage.
- `docs/course-overview.zh.md`: remove after its content is copied into the homepage.
- `docs/beginner/index.md`: compact English common/X5/S100 route selector.
- `docs/beginner/index.zh.md`: compact Chinese common/X5/S100 route selector.
- `docs/beginner/01-community-ecosystem.md`: public English title and cross-course wording without lesson numbers.
- `docs/beginner/01-community-ecosystem.zh.md`: public Chinese title and cross-course wording without lesson numbers.
- `docs/beginner/03-rdk-studio.md`: public English title without lesson number.
- `docs/beginner/03-rdk-studio.zh.md`: public Chinese title without lesson number.
- `mkdocs.yml`: topic-based bilingual navigation without ordinal labels or a Course Introduction entry.

---

### Task 1: Make the homepage the single course introduction

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_course_site_structure.py`
- Modify: `docs/index.md`
- Modify: `docs/index.zh.md`
- Delete: `docs/course-overview.md`
- Delete: `docs/course-overview.zh.md`
- Modify: `mkdocs.yml`

**Interfaces:**
- Consumes: the complete reviewed content currently in `docs/course-overview.md` and `docs/course-overview.zh.md`.
- Produces: `docs/index.md` and `docs/index.zh.md` as the only public course-introduction files; `CourseSiteStructureTests.project_root` for later regression tests.

- [ ] **Step 1: Add a failing homepage-ownership regression test**

Create `tests/__init__.py` as an empty file. Create `tests/test_course_site_structure.py` with:

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

- [ ] **Step 2: Run the new test and verify that the current two-page structure fails**

Run:

```powershell
python -m unittest tests.test_course_site_structure.CourseSiteStructureTests.test_home_is_the_single_course_overview -v
```

Expected: `FAIL` because `docs/course-overview.md` and `docs/course-overview.zh.md` still exist and the current homepages do not contain the full reviewed introduction.

- [ ] **Step 3: Move the reviewed overview content into the homepages**

Copy the complete current contents before deleting the source pages:

```powershell
Copy-Item -LiteralPath docs/course-overview.md -Destination docs/index.md
Copy-Item -LiteralPath docs/course-overview.zh.md -Destination docs/index.zh.md
```

Then delete:

```text
docs/course-overview.md
docs/course-overview.zh.md
```

In `mkdocs.yml`, remove this navigation entry:

```yaml
- Course introduction: course-overview.md
```

Do not alter the copied factual descriptions yet; Tasks 2 and 3 change only public naming and curriculum organization.

- [ ] **Step 4: Run the focused regression test**

Run:

```powershell
python -m unittest tests.test_course_site_structure.CourseSiteStructureTests.test_home_is_the_single_course_overview -v
```

Expected: `PASS`.

- [ ] **Step 5: Run a strict site build**

Run:

```powershell
python -m mkdocs build --strict
```

Expected: exit code `0`; the English site builds at the root and the Chinese site under `site/zh`.

- [ ] **Step 6: Commit the single-source homepage change**

```powershell
git add tests docs/index.md docs/index.zh.md docs/course-overview.md docs/course-overview.zh.md mkdocs.yml
git commit -m "docs: merge course introduction into home"
```

---

### Task 2: Remove ordinal labels from published course pages and navigation

**Files:**
- Modify: `tests/test_course_site_structure.py`
- Modify: `docs/beginner/01-community-ecosystem.md`
- Modify: `docs/beginner/01-community-ecosystem.zh.md`
- Modify: `docs/beginner/03-rdk-studio.md`
- Modify: `docs/beginner/03-rdk-studio.zh.md`
- Modify: `mkdocs.yml`

**Interfaces:**
- Consumes: the homepage ownership established in Task 1.
- Produces: topic-only public titles and topic-only navigation group labels; `public_markdown_files()` for the final whole-site naming check in Task 3.

- [ ] **Step 1: Add failing tests for common-course titles and navigation labels**

Add these imports and methods to `CourseSiteStructureTests`:

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

- [ ] **Step 2: Run the two new tests and verify that current titles and navigation fail**

Run:

```powershell
python -m unittest tests.test_course_site_structure.CourseSiteStructureTests.test_common_course_titles_are_topic_based tests.test_course_site_structure.CourseSiteStructureTests.test_navigation_uses_topic_groups -v
```

Expected: `FAIL` because the Community page titles contain Lesson 1 / 第一课, the Studio English title contains Lesson 03, and navigation groups use ordinal prefixes.

- [ ] **Step 3: Replace the four public page titles and numbered cross-references**

Apply these exact title changes:

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

Within the Community handbooks, replace references such as `covered in Lesson 3` / `第三课将专门介绍` with `covered in the RDK Studio course` / `RDK Studio 课程将专门介绍`. Replace the closing `next lesson` / `下一课` language with an unnumbered invitation to continue to Product Overview.

- [ ] **Step 4: Replace ordinal navigation group names**

In the English navigation and `nav_translations`, use these public group names:

```yaml
Fundamentals
ModelZoo & RoboGo
TROS
System & drivers
LLMs & embodied AI
```

Use these Chinese translations:

```yaml
Fundamentals: 基础入门
ModelZoo & RoboGo: ModelZoo 与 RoboGo
TROS: TROS
System & drivers: 系统与驱动
LLMs & embodied AI: 大模型与具身智能
```

Keep all internal file and directory paths unchanged.

- [ ] **Step 5: Run the title and navigation tests**

Run:

```powershell
python -m unittest tests.test_course_site_structure.CourseSiteStructureTests.test_common_course_titles_are_topic_based tests.test_course_site_structure.CourseSiteStructureTests.test_navigation_uses_topic_groups -v
```

Expected: both tests `PASS`.

- [ ] **Step 6: Build and commit the naming change**

Run:

```powershell
python -m mkdocs build --strict
git add tests docs/beginner/01-community-ecosystem.md docs/beginner/01-community-ecosystem.zh.md docs/beginner/03-rdk-studio.md docs/beginner/03-rdk-studio.zh.md mkdocs.yml
git commit -m "docs: use topic-based course names"
```

Expected: strict build succeeds and the commit contains no directory rename.

---

### Task 3: Build common, X5, and S100 Fundamentals routes

**Files:**
- Modify: `tests/test_course_site_structure.py`
- Modify: `docs/index.md`
- Modify: `docs/index.zh.md`
- Modify: `docs/beginner/index.md`
- Modify: `docs/beginner/index.zh.md`
- Modify: `mkdocs.yml`

**Interfaces:**
- Consumes: topic-only common page names and navigation groups from Task 2.
- Produces: the final Fundamentals classification on the homepages, route selectors, and sidebar.

- [ ] **Step 1: Add failing route and public-numbering tests**

Add these methods to `CourseSiteStructureTests`:

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

- [ ] **Step 2: Run the new route tests and verify the current curriculum fails**

Run:

```powershell
python -m unittest tests.test_course_site_structure.CourseSiteStructureTests.test_fundamentals_have_common_x5_and_s100_groups tests.test_course_site_structure.CourseSiteStructureTests.test_public_docs_do_not_expose_lesson_ordinals -v
```

Expected: `FAIL` because the copied overview still uses numbered tables and the Fundamentals overview does not yet list all board topics twice.

- [ ] **Step 3: Rewrite the Fundamentals curriculum on both homepages**

Preserve all approved descriptions from the copied overview. Replace the single numbered Fundamentals table with these three unnumbered sections in both languages:

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

Use three-column tables: `Topic | Focus | Materials` and `主题 | 内容重点 | 配套资料`. Link only existing approved pages:

- Community and Ecosystem;
- RDK Studio;
- X5 and S100 System Flashing;
- X5 and S100 Boot and Troubleshooting;
- X5 SPI demo.

Product Overview and unpublished board topics remain plain text with their existing approved focus descriptions and repository destinations where applicable.

- [ ] **Step 4: Remove numbering from later common course lines**

For ModelZoo and RoboGo, remove the `No.` / `序号` column and retain every existing topic, description, and material type in the current order. Remove Roman or Chinese ordinal prefixes from all module headings:

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

Do not split these later course lines by board.

- [ ] **Step 5: Rewrite the compact Fundamentals route selectors**

Rewrite `docs/beginner/index.md` and `docs/beginner/index.zh.md` with:

- a short Fundamentals introduction;
- a Common foundation table containing Community and Ecosystem, Product Overview, and RDK Studio;
- an RDK X5 table containing all eleven board-specific topics;
- an RDK S100 table containing all eleven board-specific topics;
- no ordinal course column;
- clickable handbook links only for published pages;
- GitHub repository-directory links for planned topics without handbook links.

The page must route users; it must not repeat the homepage audience, resource, or production sections.

- [ ] **Step 6: Align the sidebar with published routes**

Use this structure in `mkdocs.yml`:

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

Do not add Product Overview or other planned topics to the sidebar until a public handbook exists. Add matching Chinese `nav_translations` for every displayed label.

- [ ] **Step 7: Run route and public-numbering tests**

Run:

```powershell
python -m unittest tests.test_course_site_structure.CourseSiteStructureTests.test_fundamentals_have_common_x5_and_s100_groups tests.test_course_site_structure.CourseSiteStructureTests.test_public_docs_do_not_expose_lesson_ordinals -v
```

Expected: both tests `PASS`.

- [ ] **Step 8: Run the complete regression suite and strict build**

Run:

```powershell
python -m unittest tests.test_course_site_structure -v
python -m mkdocs build --strict
```

Expected: all tests pass and MkDocs exits `0`.

- [ ] **Step 9: Commit the route architecture**

```powershell
git add tests docs/index.md docs/index.zh.md docs/beginner/index.md docs/beginner/index.zh.md mkdocs.yml
git commit -m "docs: split fundamentals by board path"
```

---

### Task 4: Verify bilingual output and publication readiness

**Files:**
- Modify if validation finds a defect: `tests/test_course_site_structure.py`
- Modify if validation finds a defect: the specific Markdown or YAML source that violates the design

**Interfaces:**
- Consumes: final source structure from Tasks 1–3.
- Produces: a clean branch with passing regression tests and a strict bilingual MkDocs build.

- [ ] **Step 1: Add a bilingual structure parity test**

Add this method to `CourseSiteStructureTests`:

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

- [ ] **Step 2: Run all source-structure tests**

```powershell
python -m unittest tests.test_course_site_structure -v
```

Expected: all tests `PASS`.

- [ ] **Step 3: Scan public sources for forbidden numbering and deleted links**

Run:

```powershell
$publicDocs = Get-ChildItem docs -Recurse -File -Filter *.md |
  Where-Object { $_.FullName -notmatch '[\\/]superpowers[\\/]' }

$forbidden = $publicDocs | Select-String -Pattern 'Lesson\s+\d+|第\s*\d+\s*课|^#{1,6}\s+(\d+|[IVX]+)[\.、·]\s+' -CaseSensitive:$false
if ($forbidden) { $forbidden; exit 1 }

$overviewRefs = Get-ChildItem docs,mkdocs.yml -Recurse -File |
  Select-String -SimpleMatch 'course-overview.md'
if ($overviewRefs) { $overviewRefs; exit 1 }
```

Expected: no output and exit code `0`.

- [ ] **Step 4: Run the production-equivalent strict build**

```powershell
python -m mkdocs build --strict
```

Expected: English output under `site/`, Chinese output under `site/zh/`, exit code `0`.

- [ ] **Step 5: Inspect generated navigation and key pages**

Run:

```powershell
rg -n "Common foundation|RDK X5|RDK S100|Community and Ecosystem" site/index.html site/beginner/index.html
rg -n "通用基础|RDK X5|RDK S100|社区与生态" site/zh/index.html site/zh/beginner/index.html
```

Expected: both languages expose the three Fundamentals groups and the standalone Community and Ecosystem course; no Course Introduction navigation item appears.

- [ ] **Step 6: Review the complete branch diff**

```powershell
git diff develop...HEAD --check
git diff develop...HEAD --stat
git status -sb
```

Expected: no whitespace errors, only the design/plan, tests, homepage, Fundamentals sources, common handbook titles, and `mkdocs.yml` are changed; the worktree is clean.

- [ ] **Step 7: Commit the final parity test or fixes if this task changed files**

If Step 1 or validation fixes changed files:

```powershell
git add tests docs mkdocs.yml
git commit -m "test: verify bilingual course routes"
```

If no files changed after Task 3, do not create an empty commit.
