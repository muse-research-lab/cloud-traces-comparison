from typing import Dict, Iterator, List, Tuple

from pydantic import BaseModel

from gtd.internal import Fraction, Job, Task


class Input(BaseModel):
    jobs: Dict[int, Job]

    def __str__(self) -> str:
        return f"Input({self.jobs})"

    def get_job_by_id(self, job_id: int) -> Job:
        return self.jobs[job_id]

    def get_jobs(self) -> Iterator[Job]:
        for job in self.jobs.values():
            yield job

    def get_job_ids(self) -> List[int]:
        return [idx for idx in self.jobs.keys()]

    def get_task_by_uid(self, job_id: int, task_idx: int) -> Task:
        return self.jobs[job_id].get_task_by_idx(task_idx)

    def get_tasks(self) -> Iterator[Task]:
        for job in self.jobs.values():
            for task in job.get_tasks():
                yield task

    def get_task_uids(self) -> List[Tuple[int, int]]:
        uids = []
        for job in self.jobs.values():
            for task in job.get_tasks():
                uids.append((task.job_id, task.idx))

        return uids

    def get_fraction_by_uuid(
        self, job_id: int, task_idx: int, fraction_idx: int
    ) -> Fraction:
        return (
            self.jobs[job_id]
            .get_task_by_idx(task_idx)
            .get_fraction_by_idx(fraction_idx)
        )

    def get_fractions(self) -> Iterator[Fraction]:
        for job in self.jobs.values():
            for task in job.get_tasks():
                for fraction in task.get_fractions():
                    yield fraction

    def get_fraction_uuids(self) -> List[Tuple[int, int, int]]:
        uuids = []
        for job in self.jobs.values():
            for task in job.get_tasks():
                for fraction in task.get_fractions():
                    uuids.append((task.job_id, fraction.task_idx, fraction.idx))

        return uuids
