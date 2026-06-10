#!/usr/bin/env python3
"""Audit stub sources and find wiki pages that cite them."""
import os
import re
import json
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

def find_stub_sources():
    """Scan sources/ for raw.md files with status: stub."""
    stubs = set()
    sources_dir = os.path.join(PROJECT_ROOT, "sources")
    for root, dirs, files in os.walk(sources_dir):
        for f in files:
            if f == "raw.md":
                path = os.path.join(root, f)
                try:
                    with open(path) as fh:
                        content = fh.read()
                    # Match YAML frontmatter status: stub or the STUB callout pattern
                    if re.search(r'status:\s*stub', content) or "**STUB:**" in content:
                        rel = os.path.relpath(path, PROJECT_ROOT)
                        stubs.add(rel)
                except Exception:
                    pass
    return stubs

def extract_source_dir_from_path(path):
    """Given sources/literature/foo/bar/raw.md, return the directory name 'bar'."""
    parts = path.split(os.sep)
    if len(parts) >= 2:
        return parts[-2]
    return ""

def find_wiki_footnotes(stub_dirs):
    """Find wiki pages with footnotes referencing stub source directories."""
    wiki_dir = os.path.join(PROJECT_ROOT, "wiki")
    violating_pages = {}

    # Build set of stub directory names for matching
    stub_names = set()
    stub_paths_map = {}
    for p in sorted(stub_dirs):
        name = extract_source_dir_from_path(p)
        stub_names.add(name)
        if name not in stub_paths_map:
            stub_paths_map[name] = []
        stub_paths_map[name].append(p)

    for root, dirs, files in os.walk(wiki_dir):
        for f in files:
            if f.endswith(".md"):
                path = os.path.join(root, f)
                try:
                    with open(path) as fh:
                        content = fh.read()
                except Exception:
                    continue

                # Find all footnote definitions: [^1]: [text](sources/...)
                footnotes = re.findall(
                    r'\[\^(\d+)\]:\s.*?sources/(.+?\.md)',
                    content
                )

                for fn_num, source_path in footnotes:
                    # Extract the directory name from the source path
                    source_dir = os.path.basename(os.path.dirname(source_path))
                    if source_dir in stub_names:
                        rel = os.path.relpath(path, PROJECT_ROOT)
                        if rel not in violating_pages:
                            violating_pages[rel] = []
                        violating_pages[rel].append({
                            "footnote": fn_num,
                            "source_path": f"sources/{source_path}",
                            "source_dir": source_dir,
                            "stub_paths": stub_paths_map[source_dir]
                        })

    return violating_pages

def main():
    stubs = find_stub_sources()
    stub_dirs = set()
    for s in stubs:
        stub_dirs.add(s)

    violating = find_wiki_footnotes(stub_dirs)

    print(f"=== STUB AUDIT REPORT ===\n")
    print(f"Total stub source files: {len(stubs)}")
    print(f"Total stub source directories: {len(set(extract_source_dir_from_path(s) for s in stubs))}")
    print(f"Wiki pages citing stubs: {len(violating)}\n")

    if violating:
        print("### Wiki pages citing stubs:\n")
        for page, issues in sorted(violating.items()):
            print(f"  {page}")
            for issue in issues:
                print(f"    [^{issue['footnote']}] → {issue['source_dir']}")
            print()
    else:
        print("No wiki pages found citing stub sources.")

    # List all stubs for reference
    print("### All stub sources:\n")
    for s in sorted(stubs):
        print(f"  {s}")

    # JSON output
    report = {
        "total_stubs": len(stubs),
        "stub_sources": sorted(stubs),
        "wiki_pages_citing_stubs": {
            page: [{"footnote": i["footnote"], "source_dir": i["source_dir"]}
                   for i in issues]
            for page, issues in sorted(violating.items())
        }
    }
    print("\n" + json.dumps(report, indent=2))

    # Return non-zero if violations found
    return 1 if violating else 0


if __name__ == "__main__":
    sys.exit(main())
