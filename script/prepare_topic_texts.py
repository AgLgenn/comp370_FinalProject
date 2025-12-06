import pandas as pd
import os
import re

# load the annotated data
df = pd.read_csv("clean_posts_Annotated_final.tsv", sep="\t")

# official final taxonomy
topics = [
    "Narrative Content",
    "Genre",
    "Reception and Recognition",
    "Commercial Performance",
    "Marketing",
    "Film Production",
    "Director/Actors",
    "Distribution",
    "Unrelated"
]

# folder to store results
os.makedirs("topic_texts", exist_ok=True)

def sanitize(name):
    """replace anything not a letter/number with underscore"""
    name = re.sub(r"[^A-Za-z0-9]+", "_", name)
    return name.strip("_")

for topic in topics:
    safe_name = sanitize(topic)
    filename = f"topic_texts/{safe_name}.txt"

    subset = df[df["topic_final"] == topic]

    # combine text from each post (double newline to separate posts)
    combined = "\n\n".join(subset["combined_text"].fillna("").tolist())

    with open(filename, "w", encoding="utf-8") as f:
        f.write(combined)

    print(f"created {filename} with {len(subset)} posts")

print("\nAll topic_texts/*.txt files created.")