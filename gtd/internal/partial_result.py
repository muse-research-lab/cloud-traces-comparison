from abc import ABC, abstractmethod
from typing import Generic, Tuple

from pydantic.generics import GenericModel

from gtd.internal.types import Id, ValueT


class PartialResult(ABC, GenericModel, Generic[Id, ValueT]):
    id_: Id
    value: ValueT

    @abstractmethod
    def get_id(self) -> Id:
        pass


class FractionResult(PartialResult, Generic[ValueT]):
    id_: Tuple[int, int, int]
    value: ValueT

    def __str__(self) -> str:
        return f"""FractionResult(
            job_id={self.job_id},
            task_idx={self.task_idx},
            idx={self.idx},
            value={self.value}
        )"""

    def get_id(self) -> Tuple[int, int, int]:
        return self.id_

    @property
    def job_id(self) -> int:
        return self.id_[0]

    @property
    def task_idx(self) -> int:
        return self.id_[1]

    @property
    def idx(self) -> int:
        return self.id_[2]


class TaskResult(PartialResult, Generic[ValueT]):
    id_: Tuple[int, int]
    value: ValueT

    def __str__(self) -> str:
        return f"""TaskResult(
            job_id={self.job_id}, task_idx={self.task_idx}, value={self.value}
        )"""

    def get_id(self) -> Tuple[int, int]:
        return self.id_

    @property
    def job_id(self) -> int:
        return self.id_[0]

    @property
    def task_idx(self) -> int:
        return self.id_[1]


class JobResult(PartialResult, Generic[ValueT]):
    id_: int
    value: ValueT

    def __str__(self) -> str:
        return f"JobResult(job_id={self.job_id}, value={self.value})"

    def get_id(self) -> int:
        return self.id_

    @property
    def job_id(self) -> int:
        return self.id_
