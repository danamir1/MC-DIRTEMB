import spacy
nlp_model = spacy.load('en')
import gensim
import wikipedia
from DIRT import run_dirt
from data_reading import read_text_from_dir
from build_dicts import DIRT_counts, calculate_accumulated_stats, sim, mi, X, Y
import pickle
from itertools import combinations
import numpy as np
min_path_count = 10

def main():
    all_paths = []
    # wiki_files = []
    # for i in range(1000):
    #     file_name = wikipedia.random(1)
    #     text = wikipedia.page(file_name).content

    for text, file_name in read_text_from_dir("/Users/danamir/CS/MC/MC-Project/bbcsport/football"):
        print("analyzing file: %s" % file_name)
        analyzed_page = nlp_model(text)
        print("finished analyzing file: %s" % file_name)
        print("extracting paths for file: %s" % file_name)
        paths = run_dirt(analyzed_page)
        print("finished extracting paths for file: %s. \t found %d paths" % (file_name, len(paths)))
        all_paths.extend(paths)
        print("total paths: %d" % len(all_paths))
    frequencies, words = DIRT_counts(all_paths)
    # with open("frequencies.pkl", "rb") as ff:
    #     frequencies = pickle.load(ff)
    # with open("words.pkl", "rb") as wf:
    #     words = pickle.load(wf)
    accumulated_counts = calculate_accumulated_stats(frequencies)
    # new_frequencies = {}
    # new_words = {}
    # for path in frequencies:
    #     if (accumulated_counts.path_slot[(path, X)] + accumulated_counts.path_slot[(path,
    #                                                                                 Y)]) > min_path_count:
    #         new_frequencies[path] = frequencies[path]
    #         X_dict, Y_dict = frequencies[path]
    #         for word in X_dict:
    #             if word in new_words:
    #                 new_words[word].add(path)
    #             else:
    #                 new_words[word] = {path}
    #         for word in Y_dict:
    #             if word in new_words:
    #                 new_words[word].add(path)
    #             else:
    #                 new_words[word] = {path}
    # frequencies = new_frequencies
    # words = new_words
    # # accumulated_counts = calculate_accumulated_stats(new_frequencies)
    with open("frequencies.pkl", "wb") as ff:
        pickle.dump(frequencies, ff)
    with open("words.pkl", "wb") as wf:
        pickle.dump(words, wf)
    exit()
    unique_paths = frequencies.keys()
    pairs = combinations(unique_paths, 2)
    sims = []

    def local_sim(p1, p2, slot):
        return sim(p1, slot, p2, slot, frequencies, accumulated_counts)
    i = 0
    for p1, p2 in pairs:
        if i % 10000 == 0:
            print("finished computing simillarity for %d pairs" % i)
        total_sim = np.sqrt(local_sim(p1, p2, X) * local_sim(p1, p2, Y))
        if total_sim != 0:
            print(p1, p2, total_sim)
            sims.append(((p1,p2), total_sim))
        i += 1
        if len(sims) > 100000:
            break
    print(sorted(sims, key=lambda x: x[1], reverse=True)[:10])



    print("here")





    print("here")
    print("there")

# def test_sim():
    # with open("frequencies.pkl", "rb") as f:
    #     frequencies = pickle.load(f)
    #
    # with open("words.pkl", "rb") as f:
    #     words = pickle.load(f)
    # accumulated_counts = calculate_accumulated_stats(frequencies)
    # print("here")


if __name__ == "__main__":
    main()