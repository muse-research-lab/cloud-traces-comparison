from typing import Generic

from pydantic.generics import GenericModel

from gtd.internal.types import DataT


class Fraction(GenericModel, Generic[DataT]):
    job_id: int
    task_idx: int
    idx: int
    data: DataT

    def __str__(self) -> str:
        return f"""Fraction(
            job_id={self.job_id}, task_idx={self.task_idx}, idx={self.idx}
        )"""

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Fraction):
            return (
                self.job_id == other.job_id
                and self.task_idx == other.task_idx
                and self.idx == other.idx
            )

        return False
