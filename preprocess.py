import os
import re
import yaml
import shutil


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


def write_pages(directory, title=None, nav=None):
    pages = {}
    if title:
        pages['title'] = title
    if nav:
        pages['nav'] = nav
    with open(os.path.join(directory, '.pages'), 'w', encoding='utf-8') as f:
        yaml.dump(pages, f, allow_unicode=True, default_flow_style=False)


docs_src = 'test'
docs_build = 'docs_build'

# Clean and recreate docs_build
shutil.rmtree(docs_build, ignore_errors=True)
os.makedirs(docs_build)

# Read root catalog title from .doc-root.yaml
doc_root_fm = {}
if os.path.exists('.doc-root.yaml'):
    with open('.doc-root.yaml', 'r', encoding='utf-8') as f:
        doc_root_fm = yaml.safe_load(f) or {}
site_title = doc_root_fm.get('title', 'AgencyWiki')

# Create root index.md
with open(os.path.join(docs_build, 'index.md'), 'w', encoding='utf-8') as f:
    f.write(f"---\ntitle: {site_title}\n---\n\n# {site_title}\n")

# Walk test/ and replicate structure into docs_build/test/
top_sections = []

for root, dirs, files in os.walk(docs_src):
    dirs.sort()

    rel = os.path.relpath(root, docs_src)
    if rel == '.':
        build_dir = os.path.join(docs_build, docs_src)
    else:
        build_dir = os.path.join(docs_build, docs_src, rel)
    os.makedirs(build_dir, exist_ok=True)

    # Handle _index.md -> index.md
    index_src_path = os.path.join(root, '_index.md')
    index_fm = {}
    if os.path.exists(index_src_path):
        index_fm, _ = read_frontmatter(index_src_path)
        title = index_fm.get('title', os.path.basename(root))
        with open(os.path.join(build_dir, 'index.md'), 'w', encoding='utf-8') as f:
            f.write(f"---\ntitle: {title}\n---\n\n# {title}\n")

    # Copy .md files, sort by order:
    md_files = []
    for fname in files:
        if fname.endswith('.md') and fname != '_index.md':
            src_path = os.path.join(root, fname)
            fm, _ = read_frontmatter(src_path)
            md_files.append((fm.get('order', 999), fname))
            shutil.copy2(src_path, os.path.join(build_dir, fname))

    md_files.sort(key=lambda x: x[0])

    # Build nav for this directory
    nav = []
    if os.path.exists(index_src_path):
        nav.append('index.md')
    nav.extend(fname for _, fname in md_files)
    nav.extend(sorted(dirs))

    write_pages(build_dir, title=index_fm.get('title'), nav=nav)

    if rel == '.':
        top_sections.append(docs_src)

# Root .pages: home + all top-level sections
write_pages(docs_build, nav=['index.md'] + top_sections)

print("Preprocessing done.")
