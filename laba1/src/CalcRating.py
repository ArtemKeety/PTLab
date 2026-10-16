from Types import DataType, RatingType


class CalcRating:
    def __init__(self, data: DataType) -> None:
        self.data: DataType = data
        self.rating: RatingType = dict()

    def calc(self) -> RatingType:
        for key in self.data:
            rating: float = 0.0
            gress: list[tuple[str, int]] = self.data[key]
            for subject_name, subject_value in gress:
                rating += subject_value
            self.rating[key] = rating / len(gress)
        return self.rating
