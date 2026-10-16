from Types import DataType
import xml.etree.ElementTree as parser
from IDataReader import IDataReader

import io

class XmlDataReader(IDataReader):

    def __init__(self) -> None:
        self.students: DataType = dict()
        self._student_field: str = "student"
        self._subject_field: str = "subject"

    def read(self, path: str) -> DataType:
        tree = parser.parse(path)
        root = tree.getroot()

        for student in root.findall(self._student_field):
            name = student.get("name")
            grades = [
                (subject.get("name"), int(subject.text))
                for subject in student.findall(self._subject_field)
            ]
            self.students[name] = grades

        return self.students



if __name__ == "__main__":
    reader = XmlDataReader()
    import os
    path_main = os.path.join(os.getcwd(), os.path.abspath(".."), "data", "data.xml")
    data = reader.read(path_main)