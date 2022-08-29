import os
import pytest
from anki_parser import AnkiParser

HERE = os.path.abspath(os.path.dirname(__file__))

EXAMPLES_FOLDER = os.path.join(HERE, 'examples')
TEST_FILES = os.listdir(EXAMPLES_FOLDER)


@pytest.mark.parametrize('test_file', TEST_FILES)
def test_parse_apkg(test_file):
    with AnkiParser(os.path.join(EXAMPLES_FOLDER, test_file)) as ap:
        assert isinstance(ap.cards, dict)
        assert len(ap.cards) > 0
