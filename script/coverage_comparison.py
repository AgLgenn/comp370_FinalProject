# coverage_comparison.py
# compares annotation coverage between coders
# calculates agreement and coverage statistics

import csv
from collections import Counter, defaultdict

INPUT = "clean_posts_Annotated_final.tsv"

# load the data
coder1_topics = []
coder2_topics = []
final_topics = []
total_posts = 0

with open(INPUT, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        total_posts += 1
        coder1_topics.append(row.get("topic_coder1", "").strip())
        coder2_topics.append(row.get("topic_coder2", "").strip())
        final_topics.append(row.get("topic_final", "").strip())

# calculate agreement between coders
agreement_count = 0
for i in range(len(coder1_topics)):
    if coder1_topics[i] == coder2_topics[i] and coder1_topics[i] != "":
        agreement_count += 1

agreement_rate = (agreement_count / total_posts) * 100 if total_posts > 0 else 0

# count topics per coder
coder1_counts = Counter(coder1_topics)
coder2_counts = Counter(coder2_topics)
final_counts = Counter(final_topics)

# calculate coverage (how many posts each coder labeled)
coder1_labeled = sum(1 for t in coder1_topics if t != "")
coder2_labeled = sum(1 for t in coder2_topics if t != "")
final_labeled = sum(1 for t in final_topics if t != "")

# write results
with open("coverage_comparison.txt", "w", encoding="utf-8") as f:
    f.write("=== Coverage Comparison ===\n\n")
    f.write(f"Total posts: {total_posts}\n\n")
    
    f.write("Labeling Coverage:\n")
    f.write(f"  Coder 1 labeled: {coder1_labeled} ({coder1_labeled/total_posts*100:.1f}%)\n")
    f.write(f"  Coder 2 labeled: {coder2_labeled} ({coder2_labeled/total_posts*100:.1f}%)\n")
    f.write(f"  Final labels: {final_labeled} ({final_labeled/total_posts*100:.1f}%)\n\n")
    
    f.write(f"Inter-coder Agreement: {agreement_count}/{total_posts} ({agreement_rate:.1f}%)\n\n")
    
    f.write("=== Topic Distribution: Coder 1 ===\n")
    for topic, count in sorted(coder1_counts.items(), key=lambda x: -x[1]):
        if topic:
            f.write(f"  {topic}: {count}\n")
    
    f.write("\n=== Topic Distribution: Coder 2 ===\n")
    for topic, count in sorted(coder2_counts.items(), key=lambda x: -x[1]):
        if topic:
            f.write(f"  {topic}: {count}\n")
    
    f.write("\n=== Topic Distribution: Final ===\n")
    for topic, count in sorted(final_counts.items(), key=lambda x: -x[1]):
        if topic:
            f.write(f"  {topic}: {count}\n")

print("done. created coverage_comparison.txt")

