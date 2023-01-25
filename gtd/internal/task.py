from typing import Dict, Iterator, List

from pydantic import BaseModel

from gtd.internal import Fraction


class Task(BaseModel):
    job_id: int
    idx: int
    fractions: Dict[int, Fraction]

    def __str__(self) -> str:
        fr_idxs = self.get_fraction_idxs()
        return f"""
            Task(job_id={self.job_id}, idx={self.idx}, fractions={fr_idxs})
        """

    def get_fraction_by_idx(self, fraction_idx: int) -> Fraction:
        return self.fractions[fraction_idx]

    def get_fractions(self) -> Iterator[Fraction]:
        for fraction in self.fractions.values():
            yield fraction

    def get_fraction_idxs(self) -> List[int]:
        return [idx for idx in self.fractions.keys()]
