from abc import ABC, abstractmethod
from typing import Dict, Generic, Tuple

from pydantic.generics import GenericModel

from gtd.internal import (
    Fraction,
    FractionResult,
    Input,
    Job,
    JobResult,
    Output,
    PartialOutput,
    Result,
    Task,
    TaskResult,
)
from gtd.internal.types import ValueT


class Comparator(GenericModel, ABC):
    name: str

    @abstractmethod
    def compare(self, input_obj: Input, output_obj: Output) -> None:
        pass

    @abstractmethod
    def _init_output_structure(self, input_obj: Input) -> PartialOutput:
        pass


class JobComparator(Comparator, Generic[ValueT]):
    def compare(self, input_obj: Input, output_obj: Output) -> None:
        partial_output = self._init_output_structure(input_obj)

        for job1 in input_obj.get_jobs():
            for job2 in input_obj.get_jobs():
                if job1 == job2:
                    continue

                dist = self._compare(job1, job2)

                partial_output.get_result_by_id(
                    job1.id
                ).get_partial_result_by_id(job2.id).value = dist

        output_obj.parts[self.name] = partial_output

    def _init_output_structure(self, input_obj: Input) -> PartialOutput:
        results: Dict[int, Result] = {}
        for job1 in input_obj.get_jobs():

            compared: Dict[int, JobResult] = {}
            for job2 in input_obj.get_jobs():
                if job1 == job2:
                    continue

                compared[job2.id] = JobResult(id_=job2.id, value=0.0)

            results[job1.id] = Result(baseline=job1.id, compared=compared)

        return PartialOutput(name=self.name, results=results)

    @abstractmethod
    def _compare(self, job1: Job, job2: Job) -> ValueT:
        pass


class TaskComparator(Comparator, Generic[ValueT]):
    def compare(self, input_obj: Input, output_obj: Output) -> None:
        partial_output = self._init_output_structure(input_obj)

        for task1 in input_obj.get_tasks():
            for task2 in input_obj.get_tasks():
                if task1 == task2:
                    continue

                dist = self._compare(task1, task2)

                partial_output.get_result_by_id(
                    (task1.job_id, task1.idx)
                ).get_partial_result_by_id(
                    (task2.job_id, task2.idx)
                ).value = dist

        output_obj.parts[self.name] = partial_output

    def _init_output_structure(self, input_obj: Input) -> PartialOutput:
        results: Dict[Tuple[int, int], Result] = {}
        for task1 in input_obj.get_tasks():

            compared: Dict[Tuple[int, int], TaskResult] = {}
            for task2 in input_obj.get_tasks():
                if task1 == task2:
                    continue

                compared[(task2.job_id, task2.idx)] = TaskResult(
                    id_=(task2.job_id, task2.idx), value=0.0
                )

            results[(task1.job_id, task1.idx)] = Result(
                baseline=(task1.job_id, task1.idx), compared=compared
            )

        return PartialOutput(name=self.name, results=results)

    @abstractmethod
    def _compare(self, task1: Task, task2: Task) -> ValueT:
        pass


class FractionComparator(Comparator, Generic[ValueT]):
    def compare(self, input_obj: Input, output_obj: Output) -> None:
        partial_output = self._init_output_structure(input_obj)

        for fr1 in input_obj.get_fractions():
            for fr2 in input_obj.get_fractions():
                if fr1 == fr2:
                    continue

                dist = self._compare(fr1, fr2)

                partial_output.get_result_by_id(
                    (fr1.job_id, fr1.task_idx, fr1.idx)
                ).get_partial_result_by_id(
                    (fr2.job_id, fr2.task_idx, fr2.idx)
                ).value = dist

        output_obj.parts[self.name] = partial_output

    def _init_output_structure(self, input_obj: Input) -> PartialOutput:
        results: Dict[Tuple[int, int, int], Result] = {}
        for fr1 in input_obj.get_fractions():

            compared: Dict[Tuple[int, int, int], FractionResult] = {}
            for fr2 in input_obj.get_fractions():
                if fr1 == fr2:
                    continue

                compared[(fr2.job_id, fr2.task_idx, fr2.idx)] = FractionResult(
                    id_=(fr2.job_id, fr2.task_idx, fr2.idx), value=0.0
                )

            results[(fr1.job_id, fr1.task_idx, fr1.idx)] = Result(
                baseline=(fr1.job_id, fr1.task_idx, fr1.idx), compared=compared
            )

        return PartialOutput(name=self.name, results=results)

    @abstractmethod
    def _compare(self, fraction1: Fraction, fraction2: Fraction) -> ValueT:
        pass
