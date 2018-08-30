def read_corpus(path):
    with open(path, 'r') as f:
        sentences = []
        cur_sent = []
        for line in f.readlines():
            line = line.strip()
            if line == '</s>':
                sentences.append(cur_sent)
                cur_sent = []
            elif line == '<s>' or line.startswith('<text'):
                continue
            else:
                cur_sent.append(line)
    return sentences

