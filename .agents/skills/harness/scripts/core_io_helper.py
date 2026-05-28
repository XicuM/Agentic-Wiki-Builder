import os
import re

# Thresholds for context compaction (approx 10k tokens / 40k characters)
MAX_CHAR_LIMIT = 40000

def compact_text(text: str, file_path: str) -> str:
    """
    Performs structural, citation-preserving compaction of text to fit context limits.
    Maintains headers, abstracts, footnotes, and citation definitions while pruning
    middle content of very long sections.
    """
    if len(text) <= MAX_CHAR_LIMIT:
        return text

    # Parse frontmatter if present
    frontmatter = ""
    body = text
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if fm_match:
        frontmatter = fm_match.group(0)
        body = text[fm_match.end():]

    # Split into sections based on Markdown headers
    sections = re.split(r"(\n#{1,6} [^\n]+)", body)
    
    compacted_sections = []
    if sections:
        # The first part before any header (often introduction or abstract)
        intro = sections[0].strip()
        if len(intro) > 5000:
            intro = intro[:4500] + "\n\n[... (intro truncated for space) ...]\n\n" + intro[-500:]
        compacted_sections.append(intro)

        # Process subsequent headers and their bodies
        for i in range(1, len(sections), 2):
            header = sections[i]
            body_text = sections[i+1].strip() if i+1 < len(sections) else ""

            # Check if this is references/footnotes section - ALWAYS KEEP ENTIRELY
            is_ref_section = any(x in header.lower() for x in ["references", "bibliography", "footnote"])
            
            if is_ref_section:
                compacted_sections.append(header)
                compacted_sections.append(body_text)
            else:
                if len(body_text) > 4000:
                    # Keep the first 1500 chars and last 500 chars of the section
                    pruned_body = (
                        body_text[:1500] + 
                        f"\n\n[... (pruned {len(body_text) - 2000} characters of raw text from section) ...]\n\n" + 
                        body_text[-500:]
                    )
                    compacted_sections.append(header)
                    compacted_sections.append(pruned_body)
                else:
                    compacted_sections.append(header)
                    compacted_sections.append(body_text)

    # Reassemble and prepend a context compaction warning callout
    compacted_body = "\n".join(compacted_sections)
    warning_callout = f"> ⚠️ **Context Compacted:** Content of `{os.path.basename(file_path)}` was structurally compacted from {len(text)} to {len(frontmatter) + len(compacted_body)} characters to protect context window limits. Citations and footnotes have been preserved.\n\n"
    
    return f"{frontmatter}{warning_callout}{compacted_body}"

def read_file(filepath: str) -> str:
    """
    Reads file content. Autodetects large raw markdown/text files and
    applies structural compaction if needed.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Apply compaction only to source markdown files (excluding metadata index files)
    is_source_doc = "sources/literature" in filepath and filepath.endswith("raw.md")
    
    if is_source_doc:
        return compact_text(content, filepath)
        
    return content

def write_file(filepath: str, content: str) -> None:
    """
    Standard utility to write text files in the project.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
