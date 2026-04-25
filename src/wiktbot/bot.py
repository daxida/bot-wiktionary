import difflib
import pywikibot
from pywikibot import pagegenerators
from wiktbot.main import repl


def run(max_pages: int) -> None:
    try:
        _run(max_pages)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")


def _run(max_pages: int) -> None:
    site = pywikibot.Site("ja", "wiktionary")
    cat = pywikibot.Category(site, "Category:日本語_名詞")
    gen = pagegenerators.CategorizedPageGenerator(cat)
    gen = pagegenerators.PreloadingGenerator(gen, groupsize=50)

    sections = []

    for idx, page in enumerate(gen, 1):
        if idx >= max_pages:
            break

        print(f"Scanning {page.title()} @ {page.full_url()}")
        text = page.text
        replaced = repl(text)
        if text != replaced:
            diff = difflib.unified_diff(
                text.splitlines(keepends=True),
                replaced.splitlines(keepends=True),
            )
            body = "".join(format_line(line) for line in diff)
            sections.append(section(page, body))

    title = f"diff/diff_{max_pages}.html"
    with open(title, "w", encoding="utf-8") as f:
        f.write(html(sections))

    print(f"Written to {title}")


def format_line(line: str) -> str:
    if line.startswith("+++") or line.startswith("---"):
        return f'<span class="hdr">{line}</span>'
    elif line.startswith("+"):
        return f'<span class="add">{line}</span>'
    elif line.startswith("-"):
        return f'<span class="rem">{line}</span>'
    return line


def section(page, body: str) -> str:
    return f"""
<section>
<h2><a href="{page.full_url()}">{page.title()}</a></h2>
<pre>{body}</pre>
</section>
"""


def html(sections: list[str]) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: monospace; background: #1e1e1e; color: #ccc; padding: 2rem; }}
  h2 {{ color: #fff; border-bottom: 1px solid #444; padding-bottom: 0.25rem; }}
  a {{ color: #7ab0f5; }}
  section {{ margin-bottom: 3rem; }}
  pre {{ background: #2b2b2b; padding: 1rem; border-radius: 4px; overflow-x: auto; }}
  .add {{ color: #6fcf6f; }}
  .rem {{ color: #f47f7f; }}
  .hdr {{ color: #7ab0f5; }}
</style>
</head>
<body>
{"".join(sections)}
</body>
</html>"""
