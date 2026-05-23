import os
import re
import yaml
import shutil


def read_frontmatter(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if m:
            return yaml.safe_load(m.group(1)) or {}
    except Exception:
        pass
    return {}


def process_dir(src_dir, dst_dir):
    os.makedirs(dst_dir, exist_ok=True)

    # Section title from _index.md
    index_path = os.path.join(src_dir, '_index.md')
    fm = read_frontmatter(index_path) if os.path.exists(index_path) else {}
    title = fm.get('title', os.path.basename(src_dir))

    # Write clean index.md for this section
    with open(os.path.join(dst_dir, 'index.md'), 'w', encoding='utf-8') as f:
        f.write(f"---\ntitle: {title}\n---\n\n# {title}\n")

    # Collect .md pages sorted by order:
    pages = []
    subdirs = []
    for entry in sorted(os.listdir(src_dir)):
        path = os.path.join(src_dir, entry)
        if os.path.isdir(path):
            subdirs.append(entry)
        elif entry.endswith('.md') and entry not in ('_index.md', 'index.md'):
            pfm = read_frontmatter(path)
            pages.append((pfm.get('order', 999), entry))
            shutil.copy2(path, os.path.join(dst_dir, entry))

    pages.sort(key=lambda x: x[0])

    # Process subdirectories recursively
    for subdir in subdirs:
        process_dir(os.path.join(src_dir, subdir), os.path.join(dst_dir, subdir))

    # .pages file for awesome-pages: sets section title and page order
    nav = ['index.md'] + [f for _, f in pages] + subdirs
    with open(os.path.join(dst_dir, '.pages'), 'w', encoding='utf-8') as f:
        yaml.dump({'title': title, 'nav': nav}, f, allow_unicode=True, default_flow_style=False)


# Rebuild docs/ from scratch
shutil.rmtree('docs', ignore_errors=True)
os.makedirs('docs')

# Each top-level folder in test/ becomes a section
process_dir('test', 'docs/test')

# docs/.pages — list sections in root nav
with open('docs/.pages', 'w', encoding='utf-8') as f:
    yaml.dump({'nav': ['test']}, f, allow_unicode=True, default_flow_style=False)

print("Preprocessing done.")
