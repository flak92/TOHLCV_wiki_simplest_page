import json
import textwrap
from pathlib import Path

config = json.load(open("site_config.json"))
objects_config = json.load(open("site_objects.json"))

LANG = config.get("language", "pl")
site_title = config["site_title"]
index_content = config["index_content"]
pages = config["pages"]

labels = config["labels"]
code_label = labels["code"]
comment_labels = labels["comments"]
home_label = labels.get("navigation", {}).get("home", "Strona główna")
footer_text = labels.get("footer", "")

topics = {topic["id"]: topic for topic in objects_config["topics"]}
categories = {category["id"]: category for category in objects_config["categories"]}
definitions = {definition["id"]: definition for definition in objects_config["definitions"]}

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


def build_glossary_html(category_ids):
    lines = []
    labels = comment_labels
    for category_id in category_ids:
        section = categories[category_id]
        title = section["title"]
        lines.append("")
        lines.extend(comment_box(f"{labels['section']}: {title}", "#"))
        lines.append(f"<div class='glossary-section' data-section='{category_id}'>")
        lines.append(f"  <h3>{title}</h3>")
        lines.append("  <dl>")
        definition_ids = section.get("definition_ids", [])
        for index, definition_id in enumerate(definition_ids, start=1):
            item = definitions[definition_id]
            item_title = item["label"]
            definition_label = f"{labels['definition']} {index:02d}: {item_title}"
            lines.extend([f"  {line}" for line in comment_box(definition_label, "-")])
            lines.append(f"  <dt id='{item['id']}'>{item_title}</dt>")
            description = item["description"]
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


def normalize_fragment(fragment, indent="  "):
    stripped = fragment.strip()
    if not stripped:
        return []
    dedented = textwrap.dedent(stripped)
    return [f"{indent}{line.rstrip()}" for line in dedented.splitlines()]


def build_index():
    path = "index.html"
    css_path = "styles/main.css"
    menu_items = [f"<li><a href=\"#home\">{home_label}</a></li>"]
    localized_site_title = site_title
    localized_index_content = index_content
    sections = [
        "\n".join(
            [
                "<section id=\"home\">",
                f"  <h2>{localized_site_title}</h2>",
                *normalize_fragment(localized_index_content),
                "</section>",
            ]
        )
    ]
    for page in pages:
        slug = page.get("slug")
        topic_id = page.get("topic", slug)
        topic = topics.get(topic_id)
        if topic is None:
            raise KeyError(f"Topic '{topic_id}' referenced in pages is not defined in site_objects.json")
        title = topic["title"]
        menu_items.append(f"<li><a href=\"#{slug}\">{title}</a></li>")
        content_html = topic["content"]
        if topic.get("type") == "glossary":
            category_ids = topic.get("categories", [])
            content_html = content_html + "\n" + build_glossary_html(category_ids)
        section_lines = [
            f"<section id=\"{slug}\">",
            f"  <h2>{title}</h2>",
            *normalize_fragment(content_html),
            "</section>",
        ]
        sections.append("\n".join(section_lines))
    menu_html = "\n".join(f"  {item}" for item in menu_items)
    sections_html = "\n\n".join(sections)
    page_title = localized_site_title
    html = f"""<!DOCTYPE html>
<html lang=\"{LANG}\">
<head>
<meta charset=\"UTF-8\">
<title>{page_title}</title>
<link rel=\"stylesheet\" href=\"{css_path}\">
</head>
<body>
<input type=\"checkbox\" id=\"theme-toggle\">
<div class=\"wrapper\">
<header class=\"top-bar\">
  <h1 class=\"site-title\"><a href=\"#home\">{page_title}</a></h1>
  <div class=\"controls\">
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


build_index()
