# Contributing tutorials

New tutorials should be easy to run, easy to review, and easy to maintain.

## Suggested page shape

1. State the learning outcome.
2. List the board, image, host, and hardware assumptions.
3. Show the smallest working command or code sample.
4. Describe the expected result.
5. Add a focused troubleshooting section.
6. Link the matching course-demo directory and official documentation.

## Local preview

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
mkdocs serve
```

Before opening a pull request, run:

```bash
mkdocs build --strict
```

The GitHub Actions workflow performs the same strict build before publishing to GitHub Pages.
