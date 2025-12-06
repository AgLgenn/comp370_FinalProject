
# topic distribution and coverage by MOVIE (using final labels only)
import csv
from collections import Counter, defaultdict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

INPUT = "../data/clean_posts_Annotated_final.tsv"

# load topics

rows = []
with open(INPUT, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        rows.append(row)

df = pd.DataFrame(rows)

def normalize(topic):
    if not topic:
        return ""
    t = topic.strip().lower()
    if t in ["genre", "genre "]:
        return "Genre"
    if t in ["director/actors", "director/actor"]:
        return "Director/Actors"
    if t == "sales":
        return "Commercial Performance"
    if t == "unrelated":
        return "Unrelated"
    return topic.strip().title()

df["topic_norm"] = df["topic_final"].apply(normalize)

# drop empty topics
df = df[df["topic_norm"] != ""].copy()

#  stacked bar: topics by movie 

# ignore "Unrelated" for the topic distribution
df_topics = df[df["topic_norm"] != "Unrelated"].copy()

movies = sorted(df_topics["movie"].unique())
topics = sorted(df_topics["topic_norm"].unique())

# customize colors for each movie
movie_colors = {
    "Sinners": "#d45050",
    "The Amateur": "#5B9EAB",
    "A Minecraft Movie": "#213E8E",
    "The King of Kings": "#ffe600",
}

topic_colors = {
    t: c for t, c in zip(
        topics, 
        ["#003f5c", "#213E8E", "#765BAB", "#51a09b", "#d45087",
         "#fd8a93", "#734b3a", "#ffe600"][:len(topics)]
    )
}

# counts[movie][topic] = number of posts
counts = {m: Counter() for m in movies}
for _, row in df_topics.iterrows():
    counts[row["movie"]][row["topic_norm"]] += 1

# convert counts to proportions per movie
# === stacked bar: topics by movie (PERCENTAGES, COLORS, FONTS) ===

# counts[movie][topic] = number of posts
counts = {m: Counter() for m in movies}
for _, row in df_topics.iterrows():
    counts[row["movie"]][row["topic_norm"]] += 1

movie_indices = np.arange(len(movies))
bottom = np.zeros(len(movies))  # in PERCENT units

fig, ax = plt.subplots(figsize=(10, 6))

# precompute totals per movie
totals = np.array([sum(counts[m].values()) for m in movies], dtype=float)

for topic in topics:
    vals = np.array([counts[m][topic] for m in movies], dtype=float)

    # convert to percentage
    with np.errstate(divide="ignore", invalid="ignore"):
        perc = np.where(totals > 0, vals / totals * 100.0, 0.0)

    ax.bar(
        movie_indices,
        perc,
        bottom=bottom,
        label=topic,
        color=topic_colors.get(topic, "#cccccc"),
        edgecolor="white",
        linewidth=0.5,
    )
    bottom += perc  # keep stacking in percent

ax.set_xticks(movie_indices)
ax.set_xticklabels(movies, rotation=45, ha="right")
ax.set_ylabel("Percentage of posts (%)", fontsize=14, family="Times New Roman")
# ax.set_title(
#     "Distribution of Reddit Discussion Topics for Sinners and Three Other April 2025 Releases",
#     fontsize=12,
#     fontweight="bold",
#     family="Times New Roman",
# )

# italic Times New Roman for movie names
for label in ax.get_xticklabels():
    label.set_fontfamily("Times New Roman")
    label.set_fontstyle("italic")
    label.set_fontsize(16)

# Times New Roman for y-axis tick labels
for label in ax.get_yticklabels():
    label.set_fontfamily("Times New Roman")
    label.set_fontsize(16)

legend = ax.legend(
    title="Topic",
    bbox_to_anchor=(1.05, 1),
    loc="upper left",
)
plt.setp(legend.get_texts(), fontsize=9, family="Times New Roman")
plt.setp(legend.get_title(), fontsize=10, family="Times New Roman", fontweight="bold")

ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig("topic_by_movie_stacked_bar.png", dpi=300, bbox_inches="tight")
print("created topic_by_movie_stacked_bar.png")


#  coverage by movie 
movie_counts = Counter(df["movie"])
total_posts = len(df)

movies_sorted = [m for m, _ in movie_counts.most_common()]
counts_sorted = [movie_counts[m] for m in movies_sorted]
props_sorted = [c / total_posts * 100 for c in counts_sorted]

# horizontal bar chart
fig2, ax2 = plt.subplots(figsize=(8, 5))
ax2.barh(movies_sorted, props_sorted)

# get a color for each movie in the same order as movies_sorted
colors_bar = [movie_colors.get(m, "#cccccc") for m in movies_sorted]
bars = ax2.barh(movies_sorted, props_sorted, color=colors_bar)

for label in ax2.get_yticklabels():
    label.set_fontfamily("Times New Roman")  # or .set_family("Times New Roman")
    label.set_fontstyle("italic")
    label.set_fontsize(16)     

ax2.set_xlabel("Percentage of Posts (%)", fontsize=16, family="Times New Roman")
# ax2.set_title("Percentage of Reddit Posts Mentioning Sinners versus Three Other Movies Released in April 2025", 
#               fontsize=12, family="Times New Roman")
ax2.grid(axis="x", alpha=0.3)
 
plt.tight_layout()
plt.savefig("coverage_by_movie_bar.png", dpi=300, bbox_inches="tight")
print("created coverage_by_movie_bar.png")

# === print percentage of each topic within each movie ===

perc_rows = []
for m in movies:
    total_m = sum(counts[m].values())
    row = {"movie": m}
    for t in topics:
        if total_m > 0:
            row[t] = counts[m][t] / total_m * 100.0
        else:
            row[t] = 0.0
    perc_rows.append(row)

perc_df = pd.DataFrame(perc_rows)

# nice formatted print
print("Percent of posts in each topic by movie:")
print(perc_df.to_string(index=False, float_format=lambda x: f"{x:5.2f}"))

# pie chart  
fig3, ax3 = plt.subplots(figsize=(6, 6))
ax3.pie(counts_sorted, labels=movies_sorted, autopct="%1.1f%%")
ax3.set_title("Percentage of Reddit posts mentioning Sinners versus three other movies released in April 2025")

plt.tight_layout()
plt.savefig("coverage_by_movie_pie.png", dpi=300, bbox_inches="tight")
print("created coverage_by_movie_pie.png")

print("done.")