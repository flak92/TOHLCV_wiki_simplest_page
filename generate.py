import json
from pathlib import Path

LANGS = ["en", "pl"]

config = json.load(open("site_config.json"))
site_title = config["site_title"]
index_content = config["index_content"]
pages = config["pages"]

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

      const originalCodeSpan = dd.querySelector('.code');
      if (originalCodeSpan) {
        const codeDiv = document.createElement('div');
        codeDiv.className = 'code';
        codeDiv.textContent = originalCodeSpan.textContent.trim();
        card.appendChild(codeDiv);
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
