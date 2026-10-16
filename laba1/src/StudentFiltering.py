from dataclasses import dataclass, field
from Types import RatingType, RatingFilter


@dataclass(slots=True, frozen=True)
class StudentFiltering:
    func: RatingFilter  = field(default=lambda _n, _v: True, repr=False)

    def filter(self, r: RatingType) -> RatingType:
        return {name: value for name, value in r.items() if self.func(name, value)}