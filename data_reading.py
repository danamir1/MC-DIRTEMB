import glob
import sys

def generate_texts_from_files(filenames):
    for name in filenames:
        with open(name, "r") as f:
            try:
                text = f.read()
            except UnicodeDecodeError:
                print("couldn't read file: %s" % name, file=sys.stderr)
                continue
            yield text, name


def read_text_from_dir(dir="/Users/danamir/CS/MC/MC-Project/bbcsport"):
    paths = glob.glob(dir + "/**/*.txt", recursive=True)
    return generate_texts_from_files(paths)

def read_corpus(path):
    with open(path, 'r', encoding="ISO-8859-1") as f:
        sentences = []
        cur_sent = []
        i = 0
        for line in f.readlines():
            line = line.strip()
            if line == '</s>':
                sentences.append(" ".join(cur_sent))
                cur_sent = []
                if (i > 0) and (i % 100 == 0):
                    yield " ".join(sentences)
                    sentences = []
            elif line == '<s>' or line.startswith('<text'):
                continue
            else:
                cur_sent.append(line)
            i += 1


    yield " ".join(sentences)
