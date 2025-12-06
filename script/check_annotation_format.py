# quick script to check the annotated dataset
# just making sure everything is shaped correctly before running tf-idf
# better to catch errors early

import csv
from collections import Counter

FILENAME = "../data/clean_posts_Annotated_final.tsv"

# columns we expect to see in the file
EXPECTED = [
    "id","movie","subreddit","title","selftext",
    "combined_text","score","created_utc","permalink","topic_final","topic_coder1","topic_coder2"
]

with open(FILENAME, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    
    # make sure columns match the ones we expect
    cols = reader.fieldnames
    if cols != EXPECTED:
        print("column mismatch")
        print("expected:", EXPECTED)
        print("got:", cols)
        exit()

    topic_counter = Counter()
    movie_counter = Counter()
    row_count = 0

    for row in reader:
        row_count += 1

        # sanity check for empty topics
        if not row["topic_final"].strip():
            print("blank topic_final found at row:", row)
            exit()

        topic_counter[row["topic_final"]] += 1
        movie_counter[row["movie"]] += 1

print("all rows have topics ✓")
print(f"total rows: {row_count}")
print("\nposts per movie:")
for m, c in movie_counter.items():
    print(f"  {m}: {c}")

print("\ntopic counts:")
for t, c in topic_counter.items():
    print(f"  {t}: {c}")

if "Unrelated" in topic_counter:
    print(f"\nnotice: {topic_counter['Unrelated']} posts labeled 'Unrelated'")
    print("these will be ignored for tf-idf (normal)")