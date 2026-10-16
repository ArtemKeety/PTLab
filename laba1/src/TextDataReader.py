from Types import DataType
from IDataReader import IDataReader


class TextDataReader(IDataReader):
    def __init__(self) -> None:
        self.key: str = str()
        self.students: DataType = dict()


    def read(self, path: str) -> DataType:
        with open(path, encoding='utf-8') as file:
            for line in file:
                if not line.startswith(" "):
                    self.key = line.strip()
                    self.students[self.key] = []
                else:
                    subj, score = line.split(":", maxsplit=1)
                    self.students[self.key].append((subj.strip(), int(score.strip())))
        return self.students