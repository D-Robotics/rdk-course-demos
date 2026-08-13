# RDK Classroom Site Information Architecture Design

## Objective

Reorganize the public RDK Classroom site around course topics and board-specific learning paths instead of public lesson numbers.

The new structure must:

- make the homepage the single authoritative course introduction;
- use the reviewed bilingual course-overview handbooks as the homepage content source;
- keep Community and Ecosystem, Product Overview, and RDK Studio as common foundation courses;
- split the remaining Fundamentals topics into separate RDK X5 and RDK S100 paths;
- leave ModelZoo and RoboGo, TROS, System and Drivers, Large Models and Embodied AI, and Developer Cases as common course lines for now;
- remove public wording such as “Lesson 3” or “第 3 课” while preserving numbered repository directories for maintenance.

## Content Authority

The reviewed source handbooks remain the factual authority:

- Chinese course overview: `course/导学/RDK 小课堂课程介绍.md`
- English course overview: `course/导学/RDK Course Overview.md`

Within `rdk-course-demos`, the resulting homepage files are:

- `docs/index.zh.md`
- `docs/index.md`

The homepage may change headings, tables, and links to implement this information architecture, but it must preserve the approved course scope and descriptions. It must not invent unapproved topics or technical details.

## Public Information Architecture

### Homepage

The homepage replaces the separate Course Introduction page and contains:

1. course purpose and audience;
2. recommended learning method;
3. explanation of videos, GitHub Pages handbooks, GitHub demos, and official documentation;
4. recommended learning path;
5. the complete public curriculum;
6. direct links into common foundation courses and board-specific Fundamentals paths.

The separate `course-overview` navigation entry and Markdown pages are removed. No compatibility redirect is required because the URL has not been publicly shared.

### Fundamentals

Fundamentals is organized into three groups.

#### Common foundation

- Community and Ecosystem
- Product Overview
- RDK Studio

Community and Ecosystem remains a standalone common course. It is not merged into the homepage and is not split by board.

Product Overview and RDK Studio also remain common courses because their purpose is to establish product and development-workbench understanding before board-specific operations.

#### RDK X5 path

- System Flashing
- Boot and Troubleshooting
- Remote Connection
- Camera
- Audio
- Display
- Video Codec
- GPIO and PWM
- UART and I2C
- SPI
- CAN

#### RDK S100 path

- System Flashing
- Boot and Troubleshooting
- Remote Connection
- Camera
- Audio
- Display
- Video Codec
- GPIO and PWM
- UART and I2C
- SPI
- CAN

Only existing, approved handbooks become clickable content pages. Topics without a completed handbook remain visible as planned topics and repository destinations; the site must not generate placeholder technical instructions.

### Later course lines

The following remain common and are not split by board in this iteration:

- ModelZoo and RoboGo
- TROS
- System and Drivers
- Large Models and Embodied AI
- Developer Cases

Their public curriculum entries use topic titles without ordinal lesson labels.

## Public Naming Rules

Public navigation, headings, tables, cards, and link labels must not use:

- `第 N 课`;
- `Lesson N`;
- numbered prefixes such as `01 ·` when the number represents course order.

Public names use topics directly, for example:

- `System Flashing` / `系统烧录`;
- `RDK Studio`;
- `Community and Ecosystem` / `社区与生态`.

Internal repository paths such as `01_beginner/03_rdk_studio` remain unchanged. These numbers are maintenance identifiers and are not presented as the public course name.

## Navigation Design

The primary navigation is:

- Home
- Fundamentals
  - Common foundation
    - Community and Ecosystem
    - RDK Studio
  - RDK X5
    - board-specific topics with published handbooks
  - RDK S100
    - board-specific topics with published handbooks
- ModelZoo and RoboGo
- TROS
- System and Drivers
- Large Models and Embodied AI
- Developer Cases, when a public index exists

The Fundamentals overview page remains a compact route selector. It displays Product Overview as a planned common topic, but the sidebar does not link it until an approved public handbook exists. It must not duplicate the full homepage course introduction.

## Bilingual Behavior

English and Chinese sites must have matching:

- navigation hierarchy;
- topic order;
- common-course versus board-specific classification;
- link destinations;
- published-versus-planned status.

Text may be naturally localized rather than translated word for word. English official-document links use the GitHub IO English documentation entry where available.

## Repository Boundaries

This change updates the public documentation site and its navigation. It does not rename numbered code directories or move existing demo code.

The standalone HTML slide sources and Blueprints remain in their existing internal course directories. Removing lesson numbers from those presentation assets is outside this site-information-architecture change unless they are directly linked with a public numbered title.

## Implementation Rules

- Rebuild `docs/index.md` and `docs/index.zh.md` from the reviewed course-overview content.
- Remove `docs/course-overview.md` and `docs/course-overview.zh.md` after their content is incorporated into the homepage.
- Remove the Course Introduction navigation item.
- Rewrite the Fundamentals overview and navigation using common, X5, and S100 groups.
- Add Product Overview navigation only when a public handbook exists; until then it remains a planned topic on the homepage and Fundamentals overview.
- Do not duplicate common course content into X5 and S100 versions.
- Do not create technical placeholder pages for missing topics.
- Preserve existing published X5 and S100 flashing and boot-troubleshooting pages.

## Validation

The implementation is complete when:

1. `mkdocs build --strict` succeeds;
2. the homepage contains the full approved course introduction in both languages;
3. there is no separate Course Introduction navigation entry or Markdown page;
4. Community and Ecosystem remains an independent common course;
5. Product Overview and RDK Studio appear as common Fundamentals topics, while only published handbooks appear as sidebar links;
6. all other Fundamentals topics are listed under both RDK X5 and RDK S100;
7. later course lines remain common;
8. no public navigation label or curriculum row uses `第 N 课`, `Lesson N`, or an ordinal course prefix;
9. existing published links for flashing, boot troubleshooting, Community and Ecosystem, and RDK Studio remain valid;
10. no numbered repository directory is renamed or moved;
11. English and Chinese navigation and curriculum structures match.

## Out of Scope

- Writing missing Product Overview or board-specific technical handbooks;
- splitting ModelZoo, TROS, System and Drivers, large-model, or developer-case content by board;
- renaming internal numbered directories;
- changing course video titles, narration scripts, or standalone slide-deck titles;
- creating redirects for the unpublished `/course-overview/` URL.
