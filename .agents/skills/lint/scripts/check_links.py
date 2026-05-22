import os
import re
import sys

def find_markdown_links(content):
    # Standard markdown links [text](link)
    # Ignores external links, mailto, and anchors
    links = re.findall(r'\[[^\]]+\]\(([^)]+)\)', content)
    # Footnote style links [^1]: [text](link)
    links += re.findall(r'\[\^[0-9]+\]: \[?[^\]]+\]?\(([^)]+)\)', content)
    return links

def check_footnotes(content):
    # Find all footnote references [^1]
    refs = re.findall(r'\[\^([a-zA-Z0-9]+)\](?!:)', content)
    # Find all footnote definitions [^1]:
    defs = re.findall(r'\[\^([a-zA-Z0-9]+)\]:', content)
    
    missing_defs = [r for r in refs if r not in defs]
    unused_defs = [d for d in defs if d not in refs]
    
    return missing_defs, unused_defs

def check_file(filepath):
    results = {
        "broken_links": [],
        "missing_footnotes": [],
        "unused_footnotes": []
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"error": str(e)}
    
    # Check Links
    links = find_markdown_links(content)
    for link in links:
        if link.startswith(('http://', 'https://', '#', 'mailto:')):
            continue
        
        # Strip query params or anchors
        clean_link = link.split('#')[0].split('?')[0]
        if not clean_link:
            continue
            
        dir_path = os.path.dirname(filepath)
        target_path = os.path.normpath(os.path.join(dir_path, clean_link))
        
        if not os.path.exists(target_path):
            results["broken_links"].append((link, target_path))
            
    # Check Footnotes
    missing, unused = check_footnotes(content)
    results["missing_footnotes"] = missing
    results["unused_footnotes"] = unused
            
    return results

def run_audit(root_dir):
    all_results = {}
    for root, dirs, files in os.walk(root_dir):
        if any(ignored in root for ignored in ['.git', '.venv', '.obsidian', '__pycache__']):
            continue
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                res = check_file(path)
                if any(res.values()):
                    all_results[path] = res
    return all_results

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    audit_results = run_audit(target)
    
    if not audit_results:
        print("Audit passed: No issues found.")
    else:
        for path, res in audit_results.items():
            print(f"\n--- {path} ---")
            if res.get("broken_links"):
                print("Broken Links:")
                for link, target in res["broken_links"]:
                    print(f"  - {link} -> {target}")
            if res.get("missing_footnotes"):
                print(f"Missing Footnote Definitions: {', '.join(res['missing_footnotes'])}")
            if res.get("unused_footnotes"):
                print(f"Unused Footnote Definitions: {', '.join(res['unused_footnotes'])}")
