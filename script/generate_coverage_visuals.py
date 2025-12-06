# generate_coverage_visuals.py
# creates visualizations for coverage comparison

import csv
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter

INPUT = "clean_posts_Annotated_final.tsv"

# load the data
data = []
with open(INPUT, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        data.append({
            "coder1": row.get("topic_coder1", "").strip(),
            "coder2": row.get("topic_coder2", "").strip(),
            "final": row.get("topic_final", "").strip()
        })

df = pd.DataFrame(data)

# normalize topic names (same as in tfidf script)
def normalize(topic):
    if not topic:
        return topic
    t = topic.strip().lower()
    if t == "genre" or t == "genre ":
        return "Genre"
    if t == "director/actors" or t == "director/actor":
        return "Director/Actors"
    if t == "sales":
        return "Commercial Performance"
    if t == "unrelated":
        return "Unrelated"
    return topic.strip().title()

df['coder1_norm'] = df['coder1'].apply(normalize)
df['coder2_norm'] = df['coder2'].apply(normalize)
df['final_norm'] = df['final'].apply(normalize)

# count topics
final_counts = Counter(df['final_norm'].dropna())
coder1_counts = Counter(df['coder1_norm'].dropna())
coder2_counts = Counter(df['coder2_norm'].dropna())

# get all topics (excluding unrelated)
all_topics = sorted([t for t in final_counts.keys() if t and t != "Unrelated"])

# create comparison chart
fig, ax = plt.subplots(figsize=(12, 6))

topics_ordered = sorted(all_topics, key=lambda x: final_counts.get(x, 0), reverse=True)
coder1_vals = [coder1_counts.get(t, 0) for t in topics_ordered]
coder2_vals = [coder2_counts.get(t, 0) for t in topics_ordered]
final_vals = [final_counts.get(t, 0) for t in topics_ordered]

x = range(len(topics_ordered))
width = 0.25
ax.bar([i - width for i in x], coder1_vals, width, label='Coder 1', alpha=0.8)
ax.bar(x, coder2_vals, width, label='Coder 2', alpha=0.8)
ax.bar([i + width for i in x], final_vals, width, label='Final', alpha=0.8)

ax.set_xlabel('Topic')
ax.set_ylabel('Number of Posts')
ax.set_title('Topic Distribution: Coder 1 vs Coder 2 vs Final')
ax.set_xticks(x)
ax.set_xticklabels(topics_ordered, rotation=45, ha='right')
ax.legend()
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('coverage_visuals.png', dpi=300, bbox_inches='tight')
print("created coverage_visuals.png")

# also create final topic distribution chart
fig2, ax2 = plt.subplots(figsize=(10, 6))
final_sorted = sorted(final_counts.items(), key=lambda x: x[1], reverse=True)
topics_final = [t[0] for t in final_sorted if t[0] and t[0] != "Unrelated"]
counts_final = [t[1] for t in final_sorted if t[0] and t[0] != "Unrelated"]

ax2.bar(topics_final, counts_final, alpha=0.7, edgecolor='black')
ax2.set_xlabel('Topic')
ax2.set_ylabel('Number of Posts')
ax2.set_title('Final Topic Distribution')
ax2.set_xticks(range(len(topics_final)))
ax2.set_xticklabels(topics_final, rotation=45, ha='right')
ax2.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('topic_distribution.png', dpi=300, bbox_inches='tight')
print("created topic_distribution.png")
