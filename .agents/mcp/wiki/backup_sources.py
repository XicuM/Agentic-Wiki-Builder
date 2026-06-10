#!/usr/bin/env python3
import os
import json
import re

def get_source_url(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('source_url:'):
                    return line.split('source_url:', 1)[1].strip()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return None

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    sources_dir = os.path.join(base_dir, 'sources')
    user_dir = os.path.join(base_dir, 'user')
    backup_file = os.path.join(user_dir, 'sources_backup.json')
    
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    database = []
    
    for root, dirs, files in os.walk(sources_dir):
        if '_index.md' in files:
            index_path = os.path.join(root, '_index.md')
            with open(index_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    match = re.search(r'- \[(.*?)\]\((.*?)\)', line)
                    if match:
                        title = match.group(1)
                        rel_path = match.group(2)
                        
                        if rel_path.endswith('_index.md'):
                            continue
                            
                        if title.startswith(' ]') or title.startswith('x]'):
                            continue
                            
                        target_file = os.path.join(root, rel_path)
                        source_url = get_source_url(target_file)
                        
                        database.append({
                            'title': title,
                            'local_path': os.path.relpath(target_file, base_dir),
                            'source_url': source_url
                        })
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2)
    
    print(f"Sources database backed up to {backup_file} ({len(database)} entries)")

if __name__ == "__main__":
    main()
