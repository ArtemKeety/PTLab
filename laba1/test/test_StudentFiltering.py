import pytest
from src.Types import RatingType, RatingFilter
from src.StudentFiltering import StudentFiltering


@pytest.fixture(name="filter_func_gt_60")
def get_filter_func_gt_60() -> RatingFilter:
    return lambda _, value: value > 60

class TestStudentFiltering:

    @pytest.fixture(name="input_data")
    def input_data(self) -> tuple[RatingType, RatingType]:
        before_filter: RatingType = {
            "Абрамов Петр Сергеевич": 85.3333,
            "Петров Игорь Владимирович": 59.0000,
            "Олегов Игорь Владимирович": 60.0000,
            "Павлов Игорь Владимирович": 61.0000,
        }
        after_filter: RatingType = {
            "Абрамов Петр Сергеевич": 85.3333,
            "Павлов Игорь Владимирович": 61.0000,
        }
        return before_filter, after_filter


    def test_init_calc_rating(self, filter_func_gt_60: RatingFilter) -> None:
        assert filter_func_gt_60 == StudentFiltering(filter_func_gt_60).func

    def test_calc(self, input_data: tuple[RatingType, RatingType], filter_func_gt_60: RatingFilter) -> None:
        before_filter, after_filter = input_data
        filter_rating = StudentFiltering(filter_func_gt_60).filter(before_filter)
        for new , old in zip(filter_rating.items(), after_filter.items()):
            assert new == old
