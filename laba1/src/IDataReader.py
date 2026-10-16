from Types import DataType
from typing import Protocol


class IDataReader(Protocol):

    def read(self, path: str) -> DataType:
        ...