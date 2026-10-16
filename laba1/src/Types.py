from typing import Callable, Any


type DataType = dict[str, list[tuple[str, int]]]
type RatingType = dict[str, float]


type RatingFilter = Callable[[str, Any], bool]