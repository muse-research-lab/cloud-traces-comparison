from typing import Generic, TypeVar

from pydantic.generics import GenericModel

DataT = TypeVar("DataT")


class Fraction(GenericModel, Generic[DataT]):
    task_idx: int
    idx: int
    data: DataT

    def __str__(self) -> str:
        return f"Fraction(task_idx={self.task_idx}, idx={self.idx})"
