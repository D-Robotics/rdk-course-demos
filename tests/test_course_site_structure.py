from pathlib import Path
import re
import unittest

import yaml


class CourseSiteStructureTests(unittest.TestCase):
    project_root = Path(__file__).resolve().parents[1]

    def read(self, relative_path: str) -> str:
        return (self.project_root / relative_path).read_text(encoding="utf-8")

    def public_markdown_files(self) -> list[Path]:
        return [
            path
            for path in (self.project_root / "docs").rglob("*.md")
            if "superpowers" not in path.parts
        ]

    def public_lesson_ordinal_patterns(self) -> tuple[re.Pattern[str], ...]:
        return (
            re.compile(r"Lesson\s+\d+", re.IGNORECASE),
            re.compile(r"第\s*\d+\s*课"),
            re.compile(r"^#{1,6}\s+\d+\s*·\s+", re.MULTILINE),
            re.compile(
                r"^#{1,6}\s+[IVX]+\.\s+(?:Beginner|Advanced|Expert|Developer)",
                re.MULTILINE | re.IGNORECASE,
            ),
            re.compile(
                r"^#{1,6}\s+[一二三四五六七八九十]+、(?:入门篇|进阶篇|高阶篇|开发者案例)(?:[：:]|$)",
                re.MULTILINE,
            ),
            re.compile(r"^\|\s*(?:\d+|Lesson\s+\d+|第\s*\d+\s*课)\s*\|", re.MULTILINE | re.IGNORECASE),
        )

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

    def test_public_docs_do_not_expose_lesson_ordinals(self) -> None:
        for path in self.public_markdown_files():
            text = path.read_text(encoding="utf-8")
            for pattern in self.public_lesson_ordinal_patterns():
                self.assertIsNone(pattern.search(text), f"{path}: {pattern.pattern}")

    def test_chinese_curriculum_ordinals_do_not_match_regular_sections(self) -> None:
        patterns = self.public_lesson_ordinal_patterns()
        forbidden_headings = (
            "## 二、进阶篇：TROS 开发指南",
            "## 六、开发者案例",
        )
        allowed_headings = (
            "## 1. 安装依赖",
            "## 一、普通章节",
        )

        for heading in forbidden_headings:
            self.assertTrue(any(pattern.search(heading) for pattern in patterns), heading)
        for heading in allowed_headings:
            self.assertFalse(any(pattern.search(heading) for pattern in patterns), heading)

    def test_course_repository_links_use_develop_branch(self) -> None:
        repository_tree_url = "https://github.com/D-Robotics/rdk-course-demos/tree/"
        public_sources = [self.project_root / "mkdocs.yml", *self.public_markdown_files()]
        course_links: list[tuple[Path, str]] = []

        for path in public_sources:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(f"{repository_tree_url}main", text, str(path))
            course_links.extend(
                (path, match.group(0))
                for match in re.finditer(rf"{re.escape(repository_tree_url)}[^/)\s]+", text)
            )

        self.assertTrue(course_links, "expected public course repository links")
        for path, link in course_links:
            self.assertEqual(f"{repository_tree_url}develop", link, str(path))

    def test_internal_superpowers_docs_are_excluded_from_build(self) -> None:
        config = yaml.safe_load(self.read("mkdocs.yml"))
        excluded_docs = config.get("exclude_docs", "")
        if isinstance(excluded_docs, str):
            excluded_patterns = excluded_docs.splitlines()
        else:
            excluded_patterns = excluded_docs

        self.assertIn("superpowers/**", excluded_patterns)


if __name__ == "__main__":
    unittest.main()
