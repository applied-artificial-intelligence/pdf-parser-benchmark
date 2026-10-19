"""Render the publication copy from the guide and evidence appendix with Pandoc."""

import re
import subprocess
from pathlib import Path

folder = Path(__file__).resolve().parent
for source, name in [
    (folder.parent / "benchmark-design-guide.md", "guide"),
    (folder / "evidence.md", "evidence"),
]:
    title = source.read_text().splitlines()[0].removeprefix("# ")
    body = subprocess.run(
        ["pandoc", "--from", "markdown+raw_html-smart", "--to", "html5", "--wrap=none"],
        input=source.read_text(),
        text=True,
        capture_output=True,
        check=True,
    ).stdout
    body = body.replace('href="publication/', 'href="').replace('src="publication/', 'src="')
    body = re.sub(
        r"<table(?:\s[^>]*)?>",
        lambda match: (
            '<div class="table-scroll" role="region" '
            'aria-label="Scrollable data table" tabindex="0">' + match[0]
        ),
        body,
    )
    body = body.replace("</table>", "</table></div>")
    document = (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>{title}</title>\n<link rel="stylesheet" href="article.css">\n'
        "</head>\n<body>\n<main>\n<article>\n" + body + "\n</article>\n</main>\n</body>\n</html>\n"
    )
    (folder / f"{name}.html").write_text(document)
