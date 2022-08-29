import sys
from anki_parser import AnkiParser

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise ValueError('Please provide anki (apkg) filename')
    with AnkiParser(sys.argv[1]) as ap:
        ap.to_quizlet()
