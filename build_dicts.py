from paths_extraction import Path
import math
from collections import defaultdict, namedtuple
X = 0
Y = 1
EPSILON = 1e-100
CONCAT = "#"
AccumulatedCounts = namedtuple('AccumulatedCounts', ['path_slot', 'slot', 'slot_word'])


def DIRT_counts(all_paths, verbose=True):
    frequencies = {} # dictionary for each path containing dictionary of X, Y
    words = {} # dictionary of all words that appeared at any path
    for i, p in enumerate(all_paths):
        if i % 1000 == 0 and verbose:
            print("finished counting for %d paths out of %d" % (i, len(all_paths)))
        if p not in frequencies:
            frequencies[p] = [{}, {}]
        if p[X] not in words:
            words[p[X]] = set()
        words[p[X]].add(p)
        if p[Y] not in words:
            words[p[Y]] = set()
        words[p[Y]].add(p)
        if p[X] not in frequencies[p][X]:
            frequencies[p][X][p[X]] = 0
        frequencies[p][X][p[X]] += 1
        if p[Y] not in frequencies[p][Y]:
            frequencies[p][Y][p[Y]] = 0
        frequencies[p][Y][p[Y]] += 1
    return frequencies, words


def our_counts(all_paths, verbose=True):
    frequencies = {} # dictionary for each path containing dictionary of X, Y
    words = {} # dictionary of all words that appeared at any path
    for i, p in enumerate(all_paths):
        if i % 1000 == 0 and verbose:
            print("finished counting for %d paths out of %d" % (i, len(all_paths)))
        w1_w2 = p[X] + CONCAT + p[Y]
        if p not in frequencies:
            frequencies[p] = [{}]
        if p[w1_w2] not in words:
            words[w1_w2] = set()
        words[w1_w2].add(p)
        if w1_w2 not in frequencies[p][X]:
            frequencies[p][X][w1_w2] = 0
        frequencies[p][X][w1_w2] += 1
    return frequencies, words


# sim that would work for both cases

def mi(p, slot, w, frequencies, accumulated_counts):
    """
    :param p: the path
    :param slot: x or y represented by the constants X and Y
    :param w: word
    :return: mutual information for the triplet, calculated by:
    mi(p, slot, w) = log((|p,slot,w|x|*,slot,*)/(p,slot,*|x|*, slot, w))
    """
    counter = frequencies[p][slot][w] * accumulated_counts.slot[slot]
    denominator = accumulated_counts.path_slot[(p, slot)] * accumulated_counts.slot_word[(slot, w)]
    return math.log((counter / denominator) + EPSILON)


def calculate_accumulated_stats(frequencies, verbose=True):
    path_slot_counts = defaultdict(lambda: 0)
    slot_counts = defaultdict(lambda: 0)
    slot_word_counts = defaultdict(lambda: 0)
    i = 0
    for path, counts in frequencies.items():
        if i % 1000 == 0 and verbose:
            print("finished accumulating counts for %d unique paths out of %d" % (i, len(frequencies)))
        for word, count in counts[X].items():
            path_slot_counts[(path, X)] += 1
            slot_counts[X] += 1
            slot_word_counts[(X, word)] += 1

        for word, count in counts[Y].items():
            path_slot_counts[(path, Y)] += 1
            slot_counts[Y] += 1
            slot_word_counts[(Y, word)] += 1
        i += 1

    return AccumulatedCounts(path_slot=path_slot_counts, slot=slot_counts, slot_word=slot_word_counts)


def sim(p1, s1, p2, s2, frequencies, accumulated_counts):
    T_p1_s = set(frequencies[p1][s1].keys())
    T_p2_s = set(frequencies[p2][s2].keys())  # added set() to minimize the cost of the next line
    inter = [word for word in T_p1_s if word in T_p2_s]

    counter = 0
    for w in inter:
        counter += mi(p1, s1, w, frequencies, accumulated_counts) + mi(p2, s2, w, frequencies,
                                                                       accumulated_counts)
    if counter == 0:  # avoid unnecessary computations
        return 0
    denominator = 0
    for w in T_p1_s:
        denominator += mi(p1, s1, w, frequencies, accumulated_counts)
    for w in T_p2_s:
        denominator += mi(p2, s2, w, frequencies, accumulated_counts)
    return counter/denominator


def S(p1, p2):
    return math.sqrt(sim(p1, X, p2, X) * sim((p1, Y, p2, Y)))

