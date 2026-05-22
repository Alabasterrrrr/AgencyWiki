import os
import re
import yaml


def read_frontmatter(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            return yaml.safe_load(match.group(1)) or {}, content
        return {}, content
    except Exception:
        return {}, ''


def clean_gramax_content(content):
    # Strip Gramax-specific shortcodes like [view:hierarchy=none::::List]
    return re.sub(r'\[view:[^\]]*\]', '', content).strip()


docs_dir = 'test'

for root, dirs, files in os.walk(docs_dir):
    dirs.sort()

    # Convert _index.md -> index.md (strip Gramax shortcodes)
    index_src = os.path.join(root, '_index.md')
    index_fm = {}
    if os.path.exists(index_src):
        index_fm, raw = read_frontmatter(index_src)
        title = index_fm.get('title', os.path.basename(root))
        with open(os.path.join(root, 'index.md'), 'w', encoding='utf-8') as f:
            f.write(f"---\ntitle: {title}\n---\n\n# {title}\n")

    # Collect pages sorted by order: field
    md_files = []
    for fname in files:
        if fname.endswith('.md') and fname not in ('_index.md', 'index.md'):
            fm, _ = read_frontmatter(os.path.join(root, fname))
            md_files.append((fm.get('order', 999), fname))
    md_files.sort(key=lambda x: x[0])

    # Build nav for awesome-pages .pages file
    nav = []
    if os.path.exists(index_src):
        nav.append('index.md')
    nav.extend(fname for _, fname in md_files)
    nav.extend(sorted(dirs))

    pages = {}
    if index_fm.get('title'):
        pages['title'] = index_fm['title']
    pages['nav'] = nav

    with open(os.path.join(root, '.pages'), 'w', encoding='utf-8') as f:
        yaml.dump(pages, f, allow_unicode=True, default_flow_style=False)

print("Preprocessing done.")
