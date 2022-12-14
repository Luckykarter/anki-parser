import os
import zipfile
import sqlite3
from html.parser import HTMLParser


class LineStripper(HTMLParser):
    """
    Class used for removing HTML tags from content
    """
    def error(self, message):
        pass

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)


class AnkiParser:
    """
    This class parses anki file (apkg)
    Parsed result is a dictionary of cards {question: answer} stored in cards attribute
    Then parsed dictionary can be used to export to other formats (such as Quizlet)

    When used as a context manager - it cleans up temporary files created when file unpacked
    """
    def __init__(self, apkg_file_path: str):
        self.suffix = 'anki2'
        self.db_file = f'db.{self.suffix}'
        self.collection_name = f'collection.{self.suffix}'
        self.zip_file = zipfile.ZipFile(apkg_file_path)
        self.tables = []
        self.html_parser = LineStripper()

        self.cards = {}

    def __enter__(self):
        self.parse()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.db_file)

    def unpack_collection(self):
        with open(self.db_file, 'wb') as f:
            f.write(self.zip_file.read(self.collection_name))

    def strip_answer(self, value: str) -> str:
        res = value.split('\x1f')
        if len(res) < 2:
            return ""
        return self.remove_html(res[1])

    def remove_html(self, value: str) -> str:
        self.html_parser.feed(value)
        if not self.html_parser.fed:
            return value
        v = self.html_parser.fed[0]
        self.html_parser.reset()
        self.html_parser.fed = []
        return v

    def parse(self) -> dict:
        """
        Unpacks apkg and parses notes (cards) into dictionary
        """
        self.unpack_collection()

        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            output = cursor.execute("SELECT * FROM notes;")
            for row in output:
                if len(row) < 8:
                    continue
                answer = self.strip_answer(row[6])
                note = row[7]
                self.cards[note] = answer
            cursor.close()
        return self.cards

    def to_quizlet(self):
        """
        Prints parsed cards in Quizlet format
        """
        print("The following can be copied to Quizlet import on StudySmarter:")

        for i, (q, a) in enumerate(self.cards.items()):
            if a.startswith('<'):
                continue
            sep = '\#' if i < len(self.cards) - 1 else ''
            print(f'{q}/#*#/{a}\n{sep}')
