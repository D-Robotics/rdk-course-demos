from pathlib import Path
import re
import unittest


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


if __name__ == "__main__":
    unittest.main()
