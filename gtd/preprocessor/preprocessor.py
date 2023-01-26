from abc import ABC, abstractmethod

from pydantic import BaseModel

from gtd.internal import Fraction, Input, Job, Task


class Preprocessor(BaseModel, ABC):
    @abstractmethod
    def run(self, input_obj: Input) -> Input:
        pass


class JobPreprocessor(Preprocessor):
    def run(self, input_obj: Input) -> Input:
        for job in input_obj.get_jobs():
            self._run(job)

        return input_obj

    @abstractmethod
    def _run(self, job: Job) -> None:
        pass


class TaskPreprocessor(Preprocessor):
    def run(self, input_obj: Input) -> Input:
        for task in input_obj.get_tasks():
            self._run(task)

        return input_obj

    @abstractmethod
    def _run(self, task: Task) -> None:
        pass


class FractionPreprocessor(Preprocessor):
    def run(self, input_obj: Input) -> Input:
        for fraction in input_obj.get_fractions():
            self._run(fraction)

        return input_obj

    @abstractmethod
    def _run(self, fraction: Fraction) -> None:
        pass
