# COMP 370 Project 2 - Movie Release
# Script that collects Reddit posts for several movies, cleans them,
# and creates the files we need before open coding:
# - clean_posts.tsv  (full dataset)
# - open_coding_sample.tsv  (200 posts to label)

import requests
import csv
import time
import random
import re

# movies we are studying
MOVIES = [
    "Sinners",
    "A Minecraft Movie",
    "The King of Kings",
    "The Amateur"
]

# subreddits to search
SUBREDDITS = ["movies", "film", "boxoffice"]

# how many posts we want per movie (approx)
TARGET_POSTS_PER_MOVIE = 220
MAX_POSTS_PER_SEARCH = 200

# output files
CLEAN_TSV = "clean_posts.tsv"
OPEN_TSV = "open_coding_sample.tsv"

random.seed(370)  # using course number as seed for reproducibility

# rough check for English posts
# this is pretty basic but seems to work ok
def is_english(text):
    if len(text) < 30:
        return False
    ascii_letters = sum(c.isascii() and c.isalpha() for c in text)
    return ascii_letters / max(len(text), 1) > 0.6

# simple cleaning
def clean(t):
    if not t:
        return ""
    t = t.lower()
    t = re.sub(r"http\S+", " ", t)
    t = re.sub(r"www\.\S+", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()

# reddit search without login
def reddit_search(subreddit, query, limit=100, after=None):
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {
        "q": query,
        "restrict_sr": 1,
        "sort": "new",
        "limit": limit,
        "after": after
    }
    headers = {"User-Agent": "comp370project/0.1"}
    r = requests.get(url, params=params, headers=headers)
    if r.status_code != 200:
        return {"data": {"children": [], "after": None}}
    return r.json()

# collect posts for one movie
def collect_for_movie(movie):
    rows = []
    q = f"\"{movie}\""

    for sub in SUBREDDITS:
        after = None
        count_for_sub = 0

        while len(rows) < TARGET_POSTS_PER_MOVIE and count_for_sub < MAX_POSTS_PER_SEARCH:
            data = reddit_search(sub, q, limit=100, after=after)
            posts = data.get("data", {}).get("children", [])
            after = data.get("data", {}).get("after")

            if not posts:
                break

            for p in posts:
                d = p.get("data", {})
                title = d.get("title", "")
                selftext = d.get("selftext", "")
                combined = (title + "\n" + selftext).strip()

                # make sure movie name is mentioned
                if movie.lower() not in combined.lower():
                    continue

                if not is_english(combined):
                    continue

                cleaned = clean(combined)
                if cleaned == "":
                    continue

                row = {
                    "id": d.get("id", ""),
                    "movie": movie,
                    "subreddit": sub,
                    "title": clean(title),
                    "selftext": clean(selftext),
                    "combined_text": cleaned,
                    "score": d.get("score", 0),
                    "created_utc": d.get("created_utc"),
                    "permalink": "https://www.reddit.com" + d.get("permalink", "")
                }

                rows.append(row)
                count_for_sub += 1

                if len(rows) >= TARGET_POSTS_PER_MOVIE:
                    break

            time.sleep(1)  # be nice to reddit api
            if not after:
                break

    print(f"{movie}: collected {len(rows)} posts")
    return rows

# save the full cleaned dataset
def write_clean(rows):
    fields = ["id", "movie", "subreddit", "title", "selftext", "combined_text", "score", "created_utc", "permalink"]
    with open(CLEAN_TSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print("saved", CLEAN_TSV)

# sample 200 posts for open coding
def write_open_sample(rows, n=200):
    if len(rows) <= n:
        sample = rows[:]
    else:
        sample = random.sample(rows, n)

    fields = ["id", "movie", "subreddit", "title", "selftext", "combined_text", "topic"]
    with open(OPEN_TSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        for r in sample:
            w.writerow({
                "id": r["id"],
                "movie": r["movie"],
                "subreddit": r["subreddit"],
                "title": r["title"],
                "selftext": r["selftext"],
                "combined_text": r["combined_text"],
                "topic": ""
            })
    print("saved", OPEN_TSV)

# main driver
def main():
    all_rows = []

    for movie in MOVIES:
        these = collect_for_movie(movie)
        all_rows.extend(these)

    print("total collected:", len(all_rows))

    write_clean(all_rows)
    write_open_sample(all_rows, 200)

if __name__ == "__main__":
    main()