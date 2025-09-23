import json
import textwrap
from pathlib import Path

LANGS = ["en", "pl"]

config = json.load(open("site_config.json"))
site_title = config["site_title"]
site_subtitle = config.get("site_subtitle", {})
index_content = config["index_content"]
pages = config["pages"]
glossary_sections = config["glossary_sections"]

CODE_LABELS = {
    "en": "Coded as: ",
    "pl": "Kod w systemie: ",
}

COMMENT_LABELS = {
    "en": {"section": "SECTION", "definition": "DEFINITION"},
    "pl": {"section": "SEKCJA", "definition": "DEFINICJA"},
}

Path("pl").mkdir(exist_ok=True)

tag_script = r'''
<script>
document.addEventListener('DOMContentLoaded', function() {
  const tagMap = {};
  document.querySelectorAll('#glossary dl').forEach(dl => {
    const container = document.createElement('div');
    container.className = 'glossary-cards';
    dl.parentNode.insertBefore(container, dl);
    dl.querySelectorAll('dt').forEach(dt => {
      const dd = dt.nextElementSibling;
      const card = document.createElement('div');
      card.className = 'glossary-card';
      card.id = dt.id;

      const title = document.createElement('h4');
      title.textContent = dt.textContent;
      card.appendChild(title);

      const originalCodeSpan = dd.querySelector('.code');
      if (originalCodeSpan) {
        const codeDiv = document.createElement('div');
        codeDiv.className = 'code';
        codeDiv.textContent = originalCodeSpan.textContent.trim();
        card.appendChild(codeDiv);
      }

      const ddClone = dd.cloneNode(true);
      const tagSpan = ddClone.querySelector('.tags');
      if (tagSpan) tagSpan.remove();
      const codeSpan = ddClone.querySelector('.code');
      if (codeSpan) codeSpan.remove();
      ddClone.querySelectorAll('br').forEach(br => br.remove());
      const defP = document.createElement('p');
      defP.innerHTML = ddClone.innerHTML.trim();
      card.appendChild(defP);

      const originalTagSpan = dd.querySelector('.tags');
      if (originalTagSpan) {
        const tagDiv = document.createElement('div');
        tagDiv.className = 'tags';
        const tags = originalTagSpan.textContent.trim().split(/\s+/).map(t => t.replace('#',''));
        tags.forEach((tag, idx) => {
          const a = document.createElement('a');
          a.href = '#tag-' + tag;
          a.textContent = '#' + tag;
          a.className = 'tag';
          tagDiv.appendChild(a);
          if (idx < tags.length - 1) tagDiv.append(' ');
          if (!tagMap[tag]) tagMap[tag] = [];
          tagMap[tag].push(card.id);
        });
        card.appendChild(tagDiv);
      }

      container.appendChild(card);
    });
    dl.remove();
  });

  const tagIndex = document.getElementById('tag-index');
  if (tagIndex) {
    const ul = document.createElement('ul');
    Object.keys(tagMap).sort().forEach(tag => {
      const li = document.createElement('li');
      li.id = 'tag-' + tag;
      const strong = document.createElement('strong');
      strong.textContent = '#' + tag + ': ';
      li.appendChild(strong);
      tagMap[tag].forEach((id, idx) => {
        const link = document.createElement('a');
        link.href = '#' + id;
        link.textContent = id;
        li.appendChild(link);
        if (idx < tagMap[tag].length - 1) li.appendChild(document.createTextNode(', '));
      });
      ul.appendChild(li);
    });
    tagIndex.appendChild(ul);
  }
});
</script>
'''


def comment_box(text, symbol="#", indent=""):
    border = symbol * (len(text) + 10)
    middle = f"{symbol * 4} {text} {symbol * 4}"
    return [f"{indent}<!-- {border} -->", f"{indent}<!-- {middle} -->", f"{indent}<!-- {border} -->"]


def build_glossary_html(lang):
    lines = []
    labels = COMMENT_LABELS.get(lang, COMMENT_LABELS["en"])
    code_label = CODE_LABELS.get(lang, CODE_LABELS["en"])
    for section in glossary_sections:
        title = section["title"][lang]
        lines.append("")
        lines.extend(comment_box(f"{labels['section']}: {title}", "#"))
        lines.append(f"<div class='glossary-section' data-section='{section['slug']}'>")
        lines.append(f"  <h3>{title}</h3>")
        lines.append("  <dl>")
        for index, item in enumerate(section["items"], start=1):
            item_title = item["label"][lang]
            definition_label = f"{labels['definition']} {index:02d}: {item_title}"
            lines.extend([f"  {line}" for line in comment_box(definition_label, "-")])
            lines.append(f"  <dt id='{item['id']}'>{item_title}</dt>")
            description = item["description"][lang]
            tags = item.get("tags", [])
            tags_html = ""
            if tags:
                tags_html = " <span class='tags'>" + " ".join(f"#{tag}" for tag in tags) + "</span>"
            code_value = item.get("code", "").strip()
            code_html = ""
            if code_value:
                code_html = f"<br><span class='code'>{code_label}{code_value}</span>"
            lines.append(f"  <dd>{description}{tags_html}{code_html}</dd>")
            closing_label = f"END {labels['definition']} {index:02d}"
            lines.extend([f"  {line}" for line in comment_box(closing_label, "~")])
            lines.append("")
        lines.append("  </dl>")
        lines.append("</div>")
    return "\n".join(lines)


def build_lang_switch(lang):
    if lang == "en":
        return (
            "<details class=\"language\">\n"
            "  <summary>EN</summary>\n"
            "  <a href=\"index.html\">EN</a>\n"
            "  <a href=\"pl/index.html\">PL</a>\n"
            "</details>"
        )
    else:
        return (
            "<details class=\"language\">\n"
            "  <summary>PL</summary>\n"
            "  <a href=\"../index.html\">EN</a>\n"
            "  <a href=\"index.html\">PL</a>\n"
            "</details>"
        )


def normalize_fragment(fragment, indent="  "):
    stripped = fragment.strip()
    if not stripped:
        return []
    dedented = textwrap.dedent(stripped)
    return [f"{indent}{line.rstrip()}" for line in dedented.splitlines()]


def build_index(lang):
    path = "index.html" if lang == "en" else "pl/index.html"
    css_path = "styles/main.css" if lang == "en" else "../styles/main.css"
    footer_text = "Last updated: 2024" if lang == "en" else "Ostatnia aktualizacja: 2024"
    home_label = "Home" if lang == "en" else "Strona główna"
    menu_items = [f"<li><a href=\"#home\">{home_label}</a></li>"]
    sections = [
        "\n".join(
            [
                "<section id=\"home\">",
                f"  <h2>{site_title[lang]}</h2>",
                *normalize_fragment(index_content[lang]),
                "</section>",
            ]
        )
    ]
    for page in pages:
        menu_items.append(f"<li><a href=\"#{page['slug']}\">{page['title'][lang]}</a></li>")
        content_html = page["content"][lang]
        if page["slug"] == "glossary":
            content_html = content_html + "\n" + build_glossary_html(lang)
        section_lines = [
            f"<section id=\"{page['slug']}\">",
            f"  <h2>{page['title'][lang]}</h2>",
            *normalize_fragment(content_html),
            "</section>",
        ]
        sections.append("\n".join(section_lines))
    menu_html = "\n".join(f"  {item}" for item in menu_items)
    sections_html = "\n\n".join(sections)
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
<header class=\"top-bar\">
  <h1 class=\"site-title\"><a href=\"#home\">{site_title[lang]}</a></h1>
  <div class=\"controls\">
{switch}
    <label for=\"theme-toggle\" class=\"theme-switch\"></label>
  </div>
</header>
<div class=\"main\">
<nav class=\"sidebar\">
<ul>
{menu_html}
</ul>
</nav>
<main class=\"content\">
{sections_html}
<footer><p>{footer_text}</p></footer>
</main>
</div>
</div>
{tag_script}
</body>
</html>"""
    Path(path).write_text(html)


for lang in LANGS:
    build_index(lang)
