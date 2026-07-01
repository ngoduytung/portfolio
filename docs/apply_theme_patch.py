#!/usr/bin/env python3
"""
Adds dark/light theme toggle support to an existing static site's HTML files,
without touching any filled-in content (text, links, names, etc).

Run this from inside your site's root folder (e.g. `src/`), where
index.html, about.html, contact.html live at the top level and film
pages live in films/.

Usage:
    python3 apply_theme.py
"""

import re
import os

ROOT = "."  # run this script from inside your site root (e.g. src/)

INLINE_SCRIPT = '''  <script>
    (function () {
      try {
        var stored = localStorage.getItem('theme');
        var theme = stored || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        document.documentElement.setAttribute('data-theme', theme);
      } catch (e) {}
    })();
  </script>
'''

TOGGLE_BUTTON = '''        <button class="theme-toggle" id="theme-toggle" type="button" aria-label="Toggle color theme">
          <span class="theme-toggle__icon theme-toggle__icon--sun" aria-hidden="true">&#9728;</span>
          <span class="theme-toggle__icon theme-toggle__icon--moon" aria-hidden="true">&#9789;</span>
        </button>
'''

def process(path, js_prefix):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # Skip if already patched (safe to re-run)
    if 'id="theme-toggle"' in content:
        print(f"SKIP (already patched): {path}")
        return

    # 1. Insert inline blocking script right after <meta charset ...> line
    content, n1 = re.subn(
        r'(<meta charset="UTF-8">\n)',
        r'\1' + INLINE_SCRIPT,
        content,
        count=1
    )

    # 2. Wrap the <nav class="main-nav" ...>...</nav> block in a header-right div with the toggle button
    nav_pattern = re.compile(r'( *)(<nav class="main-nav".*?</nav>)\n', re.DOTALL)
    def nav_repl(m):
        indent, nav_block = m.group(1), m.group(2)
        nav_lines = nav_block.split("\n")
        nav_reindented = "\n".join(("  " + line if line.strip() else line) for line in nav_lines)
        return f'{indent}<div class="header-right">\n  {indent}{nav_reindented}\n{TOGGLE_BUTTON}{indent}</div>\n'
    content, n2 = nav_pattern.subn(nav_repl, content)

    # 3. Insert theme.js script tag before </body>
    script_tag = f'  <script src="{js_prefix}js/theme.js" defer></script>\n'
    content = content.replace("</body>", script_tag + "</body>", 1)

    if n1 != 1 or n2 != 1:
        print(f"WARNING: {path} — charset matches={n1}, nav matches={n2}. Check manually.")
        return

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Patched: {path}")

# Root-level pages
for fname in ["index.html", "about.html", "contact.html"]:
    p = os.path.join(ROOT, fname)
    if os.path.exists(p):
        process(p, "")
    else:
        print(f"Not found, skipping: {p}")

# films/ pages
films_dir = os.path.join(ROOT, "films")
if os.path.isdir(films_dir):
    for fname in sorted(os.listdir(films_dir)):
        if fname.endswith(".html"):
            process(os.path.join(films_dir, fname), "../")
