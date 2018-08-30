from itertools import combinations
from copy import copy
CONTENT_WORD_POS = {"PROPN", "VERB", "NOUN", "ADJ"} # TODO: check if other POS tags should be here
NOUNS = ["NOUN", "PROPN"]
PROPN = "PROPN"
TOKEN = "TOKEN"
DEP = "DEP"
RIGHT = "-->>"
LEFT = "<<--"


class SimplifiedToken(object):
    """
    simplified objects which stores only relevant info from the spacy token object
    """
    def __init__(self, token):
        self.str = str(token.lemma_)
        self.dep_ = token.dep_
        self.pos_ = token.pos_

    def __str__(self):
        return self.str

    def __repr__(self):
        return str(self)

class Path(object):  # TODO: implement simple token replacement to allow path pickling
    def __init__(self, token_a, token_b):
        self.token_a = SimplifiedToken(token_a)
        self.token_b = SimplifiedToken(token_b)
        a_anc = [token for token in token_a.ancestors][::-1] + [token_a]
        b_anc = [token for token in token_b.ancestors][::-1] + [token_b]
        lca = min(len(a_anc), len(b_anc)) - 1
        for i in range(min(len(a_anc), len(b_anc))):
            if a_anc[i] != b_anc[i]:
                lca = i - 1
                break
        left_path = a_anc[-1:lca:-1]
        right_path = b_anc[lca + 1:]
        self.root_index = 2 * len(left_path)

        tokens_path = left_path + [a_anc[lca]] + right_path
        self.tokens_path = [SimplifiedToken(t) for t in tokens_path]
        self.full_path = []
        for token in left_path:
            self.full_path.append((SimplifiedToken(token), TOKEN))
            self.full_path.append((token.dep_, DEP))
        self.full_path.append((SimplifiedToken(a_anc[lca]), TOKEN))
        for token in right_path:
            self.full_path.append((token.dep_, DEP))
            self.full_path.append((SimplifiedToken(token), TOKEN))

    def get_tokens(self):
        return self.tokens_path

    def get_path(self):
        return self.full_path

    def reverse(self):
        reverse = copy(self)
        reverse.full_path = self.full_path[::-1].copy()
        reverse.tokens_path = self.tokens_path[::-1].copy()
        reverse.token_a = self.token_b
        reverse.token_b = self.token_a
        reverse.root_index = len(self.full_path) - self.root_index - 1
        return reverse

    def __str__(self):
        strings = []
        for i, element in enumerate(self.full_path):
            if i < len(self.full_path) - 1:
                if i > 0:
                    strings.append(str(element[0]))
                if i < self.root_index:
                    strings.append(RIGHT)
                else:
                    strings.append(LEFT)

        return "".join(strings)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def get_triplet(self):
        return (str(self), self.token_a, self.token_b)

    def remove_dep(self, i):
        val, kind =  self.full_path[i]
        assert kind == DEP
        if i < self.root_index:
            self.root_index -= 1
        self.full_path.pop(i)

    def __getitem__(self, item):
        """
        operator override for convenience get_filler calls
        same API as get_filler
        """
        return self.get_filler(item)

    def get_filler(self, item):
        """
        returns the string of the filler word in slot X or Y
        :param item: 0 for slotX 1 for slotY
        :return: the string of the relevant word
        """
        if item not in [0,1]:
            raise ValueError("invalid input for function get_filler")
        return str(self.token_a) if item == 0 else str(self.token_b)

    def __repr__(self):
        return str(self)


class SimplifiedPath(object):
    def __init__(self, path_object):
        self.path_string = str(path_object)
        self.word_a = str(path_object.token_a)
        self.word_b = str(path_object.token_b)

    def __getitem__(self, item):
        """
        operator override for convenience get_filler calls
        same API as get_filler
        """
        return self.get_filler(item)

    def get_filler(self, item):
        """
        returns the string of the filler word in slot X or Y
        :param item: 0 for slotX 1 for slotY
        :return: the string of the relevant word
        """
        if item not in [0,1]:
            raise ValueError("invalid input for function get_filler")
        return self.word_a if item == 0 else self.word_b

    def get_triplet(self):
        return (str(self), self.word_a, self.word_b)

    def __str__(self):
        return self.path_string

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def __repr__(self):
        return str(self)


def extract_nouns_from_sentence(sent):
    nouns = []
    for token in sent:
        if token.pos_ in NOUNS:
            nouns.append(token)
    return nouns


def extract_paths_from_sent(sent):
    paths = []
    nouns = extract_nouns_from_sentence(sent)
    for noun_a, noun_b in combinations(nouns, 2):
        if noun_a == noun_b.head or noun_b == noun_a.head:  # discard empty rough paths before creation
            continue
        raw_path = Path(noun_a, noun_b)
        to_remove = []
        for i, element in enumerate(raw_path.get_path()):
            if element[1] == DEP:
                prev_pos = raw_path.full_path[i-1][0].pos_
                next_pos = raw_path.full_path[i + 1][0].pos_
                if (prev_pos not in CONTENT_WORD_POS) and (next_pos not in CONTENT_WORD_POS):
                    to_remove.append(i)
        for index in to_remove[::-1]:
            raw_path.remove_dep(index)

        if len(raw_path.tokens_path) < 3: # there are only filler words in the path..
            continue
        if PROPN in [t.pos_ for t in raw_path.tokens_path]:  # filter relations with proper nouns
            continue
        paths.append(SimplifiedPath(raw_path))
        paths.append(SimplifiedPath(raw_path.reverse()))
    return paths


def extract_paths_from_corpus(analyzed_corpus):
    """
    returns all extracted paths from a spacy analyzed corpus.
    paths are returned both in their reverse version.
    extracted paths should comply with the conditions from DIRT paper:
    1. link between two NOUNS
    2. any dependency relation which doesn't connect two content words is ommited.
    3. frequency threshold??
    :param analyzed_corpus: spacy analyzed text
    :return: list of P, w1, w2 triplets
    """
    all_paths = []
    for sent in analyzed_corpus.sents:
        all_paths.extend(extract_paths_from_sent(sent))
    return all_paths


