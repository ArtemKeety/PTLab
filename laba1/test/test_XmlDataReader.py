import pytest
from src.Types import DataType
from src.XmlDataReader import XmlDataReader

class TestXmlDataReader:
    @pytest.fixture()
    def file_and_data_content(self) -> tuple[str, DataType]:
        text = """<?xml version="1.0" encoding="UTF-8"?>
                    <root>
                      <student name="Иванов Константин Дмитриевич">
                        <subject name="математика">91</subject>
                        <subject name="химия">100</subject>
                      </student>
                      <student name="Петров Петр Семенович">
                        <subject name="русский язык">87</subject>
                        <subject name="литература">78</subject>
                      </student>
                    </root>
                """

        data = {
             "Иванов Константин Дмитриевич": [
                 ("математика", 91), ("химия", 100)
             ],
             "Петров Петр Семенович": [
                 ("русский язык", 87), ("литература", 78)
             ]
        }
        return text, data

    @pytest.fixture()
    def filepath_and_data(self, file_and_data_content: tuple[str, DataType], tmpdir) -> tuple[str, DataType]:
        file, data_content = file_and_data_content
        p = tmpdir.mkdir("datadir").join("my_data.xml")
        p.write_text(file, encoding='utf-8')
        return str(p), data_content

    def test_read(self, filepath_and_data: tuple[str, DataType]) -> None:
        file_path, file_content = filepath_and_data
        file_content = XmlDataReader().read(file_path)
        assert file_content == file_content
