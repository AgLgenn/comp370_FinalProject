# tfidf_by_topic.py
# this script loads the annotated dataset and computes the top tf-idf words per topic.
# i added a small cleanup step because some topics in the file have slight differences
# (like spaces or capitalization). this groups them together correctly.
# using sklearn's tfidfvectorizer which makes this pretty straightforward

import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict

INPUT = "clean_posts_Annotated_final.tsv"
OUTPUT_CSV = "tfidf_results.csv"
OUTPUT_TXT = "tfidf_printout.txt"

# normalizing topic names so that small differences don't turn into separate categories
def normalize(topic):
    if not topic:
        return topic
    t = topic.strip().lower()
    # mapping known inconsistent names to the proper version
    if t == "genre" or t == "genre ":
        return "Genre"
    if t == "director/actors" or t == "director/actor":
        return "Director/Actors"
    if t == "sales":
        return "Commercial Performance"
    # unrelated stays unrelated
    if t == "unrelated":
        return "Unrelated"
    # capitalize first letters for nicer formatting
    return topic.strip().title()

docs_by_topic = defaultdict(list)

# load posts grouped by normalized topic name
with open(INPUT, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        topic = normalize(row["topic_final"])
        if topic == "Unrelated":
            continue  # we skip unrelated posts for tf-idf
        docs_by_topic[topic].append(row["combined_text"])

# additional stop words to filter out common/uninformative words
# these are too generic and don't help distinguish topics
custom_stop_words = [
    'movie', 'movies', 'film', 'films',  # too common in all topics
    'like', 'just', 'really', 'amp',     # filler words
    'watch', 'watched', 'watching',      # common verbs
    'think', 'thought', 'feels',         # opinion words
    'one', 'get', 'got', 'see', 'saw',   # very common words
    'would', 'could', 'should',          # modal verbs
    'also', 'even', 'still', 'well',     # filler words
    'much', 'many', 'more', 'most',      # quantifiers
    'time', 'times', 'year', 'years',    # temporal words
    'way', 'ways', 'thing', 'things',    # vague nouns
    'make', 'made', 'makes',             # common verbs
    'good', 'great', 'best', 'better',   # generic adjectives
    'new', 'old',                        # generic descriptors
]

# combine sklearn's english stop words with our custom ones
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
all_stop_words = list(ENGLISH_STOP_WORDS) + custom_stop_words

# vectorizer for tf-idf
# using english stop words plus custom ones to filter out common words
vectorizer = TfidfVectorizer(stop_words=all_stop_words)
results = []

with open(OUTPUT_TXT, "w", encoding="utf-8") as out_txt:

    for topic, docs in docs_by_topic.items():
        if not docs:
            continue

        # compute tf-idf for this topic
        tfidf = vectorizer.fit_transform(docs)
        scores = tfidf.sum(axis=0).A1
        vocab = vectorizer.get_feature_names_out()

        # get top words, filtering out artifacts
        top_idx = scores.argsort()[::-1]
        top_words = []
        for i in top_idx:
            word = vocab[i]
            # filter out: very short words, numbers, html artifacts
            if len(word) < 2:
                continue
            if word.isdigit():
                continue
            if word in ['ve', 'x200b', 'amp', 'quot']:  # common artifacts
                continue
            top_words.append((word, scores[i]))
            if len(top_words) >= 10:
                break

        # write readable text file output
        out_txt.write(f"=== {topic} ===\n")
        for w, s in top_words:
            out_txt.write(f"{w}\n")
        out_txt.write("\n")

        # store for csv
        for w, s in top_words:
            results.append([topic, w, s])

# write results to csv file
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["topic","word","score"])
    writer.writerows(results)

print("done. created tfidf_printout.txt and tfidf_results.csv")