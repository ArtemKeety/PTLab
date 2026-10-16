import pytest
from src.CalcRating import CalcRating
from src.Types import DataType, RatingType

class TestCalcRating:

    @pytest.fixture(autouse=True, name="input_data")
    def input_data(self) -> tuple[DataType, RatingType]:
        data: DataType = {
             "Абрамов Петр Сергеевич":
             [
                ("математика", 80),
                ("русский язык", 76),
                ("программирование", 100)
             ],
             "Петров Игорь Владимирович":
             [
                ("математика", 61),
                ("русский язык", 80),
                ("программирование", 78),
                ("литература", 97)
             ],
        }
        rating_scores: RatingType = {
                "Абрамов Петр Сергеевич": 85.3333,
                "Петров Игорь Владимирович": 79.0000
        }

        return data, rating_scores

    def test_init_calc_rating(self, input_data: tuple[DataType, RatingType]) -> None:
        calc_rating = CalcRating(input_data[0])
        assert input_data[0] == calc_rating.data

    def test_calc(self, input_data: tuple[DataType, RatingType]) -> None:
         rating = CalcRating(input_data[0]).calc()
         for student in rating.keys():
            rating_score = rating[student]
            assert pytest.approx(rating_score, abs=0.001) == input_data[1][student]