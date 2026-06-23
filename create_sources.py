import json
import os
from datetime import datetime

STATE_FILE = "state.json"
INDEX_FILE = "sources/literature/physiology/_index.md"

leproult_md = """# Effect of 1 Week of Sleep Restriction on Testosterone Levels in Young Healthy Men
Authors: R. Leproult, E. van Cauter
Year: 2011

Abstract:
Daytime testosterone levels were decreased by 10% to 15% in this small convenience sample of young healthy men who underwent 1 week of sleep restriction to 5 hours per night, a condition experienced by at least 15% of the US working population. By comparison, normal aging is associated with a decrease of testosterone levels by 1% to 2% per year. This testosterone decline was associated with lower vigor scores but not with increased levels of cortisol, a stress-responsive hormone that can inhibit gonadal function. Symptoms and signs of androgen deficiency include low energy, reduced libido, poor concentration, and increased sleepiness, all of which may be produced by sleep deprivation in healthy individuals. Additional investigations of the links between sleep and testosterone are needed to determine whether sleep duration should be integrated in the evaluation of androgen deficiency.
"""

dote_montero_md = """# Acute effect of HIIT on testosterone and cortisol levels in healthy individuals: A systematic review and meta-analysis
Authors: M. Dote-Montero, et al.
Year: 2021

Abstract:
To determine the acute effect of a single high-intensity interval training (HIIT) session on testosterone and cortisol levels in healthy individuals, a systematic search of studies was conducted. The meta-analyses of 10 controlled studies (213 participants) and 50 pre-post intervention groups (677 participants) revealed a significant increase in testosterone immediately after a single HIIT session, which disappeared after 30 min, and returned to baseline values after 60 min. Significant increases of cortisol were found immediately after, after 30 min and 60 min. Testosterone and cortisol levels decreased significantly after 120 min and 180 min, and returned to baseline values after 24 h. In conclusion, testosterone and cortisol increase immediately after a single HIIT session, then drop below baseline levels, and finally return to baseline values after 24 h. Testosterone and cortisol may be used as sensitive biomarkers to monitor the anabolic and catabolic response to HIIT.
"""

def setup_source(paper_id, folder_name, md_content, title, year):
    os.makedirs(f"sources/literature/physiology/{folder_name}", exist_ok=True)
    with open(f"sources/literature/physiology/{folder_name}/raw.md", "w") as f:
        f.write(md_content)
    with open(f"sources/literature/physiology/{folder_name}/metadata.md", "w") as f:
        f.write(f"---\ntitle: {title}\nyear: {year}\n---\n")

setup_source("leproult_2011", "leproult_2011", leproult_md, "Effect of 1 Week of Sleep Restriction on Testosterone Levels in Young Healthy Men", 2011)
setup_source("dote_montero_2021", "dote_montero_2021", dote_montero_md, "Acute effect of HIIT on testosterone and cortisol levels in healthy individuals", 2021)

with open(INDEX_FILE, "a") as f:
    f.write(f"\n- [leproult_2011](leproult_2011/metadata.md): Sleep restriction to 5h/night decreases daytime testosterone by 10-15%.")
    f.write(f"\n- [dote_montero_2021](dote_montero_2021/metadata.md): Meta-analysis showing HIIT causes an acute but transient spike in testosterone followed by a drop.")

# We don't even need to enqueue in state.json because we are the synthesizer agent right now! We can just directly update the wiki.
print("Sources created successfully.")
