A tiny collection of old-school static HTML pages for documenting ML & Algotrading concepts.

## Structure

- `index.html` – English entry with a left-side menu and definitions shown on the right
- `pl/index.html` – Polish version
- `styles/` – shared CSS file with optional dark mode
- `site_config.json` – central list of definitions with translated titles/content
- `generate.py` – script that reads `site_config.json` and regenerates the index pages
- Glossary section – cross‑linked terms grouped by indicators, risk management, instruments, ML, trading styles and exchange specifics

All pages use plain HTML and CSS only. A dropdown in the menu lets you switch between English and Polish versions, a checkbox toggles dark or light mode, and glossary hashtags link to a tag index.

## Adding a definition

1. Edit `site_config.json` and add a new entry under `pages` with a slug, titles, and content for each language. To cross-link definitions, use `href="#slug"` in your HTML.
2. Run `python generate.py` to recreate the HTML files.
3. Commit the updated files.
