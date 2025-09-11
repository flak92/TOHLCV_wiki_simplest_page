import json
from pathlib import Path

LANGS = ["en", "pl"]

config = json.load(open("site_config.json"))
site_title = config["site_title"]
index_content = config["index_content"]
pages = config["pages"]

Path("pl").mkdir(exist_ok=True)


def build_lang_switch(lang):
    if lang == "en":
        return (
            "  <details class=\"language\">\n"
            "    <summary>EN</summary>\n"
            "    <a href=\"index.html\">EN</a>\n"
            "    <a href=\"pl/index.html\">PL</a>\n"
            "  </details>"
        )
    else:
        return (
            "  <details class=\"language\">\n"
            "    <summary>PL</summary>\n"
            "    <a href=\"../index.html\">EN</a>\n"
            "    <a href=\"index.html\">PL</a>\n"
            "  </details>"
        )


def build_index(lang):
    path = "index.html" if lang == "en" else "pl/index.html"
    css_path = "styles/main.css" if lang == "en" else "../styles/main.css"
    footer_text = "Last updated: 2024" if lang == "en" else "Ostatnia aktualizacja: 2024"
    menu_items = [
        (
            "<li><a href=\"#home\">Home</a></li>" if lang == "en" else
            "<li><a href=\"#home\">Strona główna</a></li>"
        )
    ]
    sections = [
        f"<section id=\"home\"><h2>{site_title[lang]}</h2>{index_content[lang]}</section>"
    ]
    for page in pages:
        menu_items.append(f"<li><a href=\"#{page['slug']}\">{page['title'][lang]}</a></li>")
        sections.append(
            f"<section id=\"{page['slug']}\"><h2>{page['title'][lang]}</h2>{page['content'][lang]}</section>"
        )
    menu_html = "\n".join(menu_items)
    sections_html = "\n".join(sections)
    switch = build_lang_switch(lang)
    html = f"""<!DOCTYPE html>
<html lang=\"{lang}\">
<head>
<meta charset=\"UTF-8\">
<title>{site_title[lang]}</title>
<link rel=\"stylesheet\" href=\"{css_path}\">
</head>
<body>
<input type=\"checkbox\" id=\"theme-toggle\">
<div class=\"wrapper\">
<nav class=\"sidebar\">
<div class=\"top-bar\">
{switch}
  <label for=\"theme-toggle\" class=\"theme-switch\"></label>
</div>
<ul>
{menu_html}
</ul>
</nav>
<main class=\"content\">
{sections_html}
<footer><p>{footer_text}</p></footer>
</main>
</div>
</body>
</html>"""
    Path(path).write_text(html)


for lang in LANGS:
    build_index(lang)
