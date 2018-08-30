import spacy
import gensim

from paths_extraction import extract_paths_from_corpus

def run_dirt(corpus):
    paths = extract_paths_from_corpus(corpus)
    return paths
