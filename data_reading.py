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
