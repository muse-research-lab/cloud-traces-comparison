import os
import random
from typing import Dict, Iterator, List, Optional, Tuple, Type

import pandas as pd

from gtd.experimentation.job import InputTask, Job
from gtd.experimentation.metrics import Metric
from gtd.experimentation.task import Task
from gtd.utils import import_class


# ! Assumption 1: Input tasks have consistent format (time, ts) and are sorted
# ! Assumption 2: Input files have consistent naming and are csv files
# !               consistent naming: (task_idx-sample_start-sample_end)
# ! Assumption 3: Input folder structure is consistent job/<tasks-csvs>
class Experiment:
    available_metrics = {
        "l1": "gtd.experimentation.metrics.L1Metric",
        "l2": "gtd.experimentation.metrics.L2Metric",
        "spectrum": "gtd.experimentation.metrics.SpectrumMetric",
    }

    def __init__(
        self,
        input_dir: str,
        metrics: List[str],
        comparison: str,
        fraction: Optional[Tuple[int, int]],
    ):
        self._jobs = {
            job.id: job for job in self._read_experiment_input(input_dir)
        }
        self._metrics = metrics
        self._comparison = comparison
        self._fraction = fraction or None

        self.time_configured = False

    def __str__(self) -> str:
        return f"""Experiment( \
            jobs={self._jobs}, \
            metrics={self._metrics}, \
            comparison={self._comparison}, \
            fraction={self._fraction} \
        )"""

    @property
    def jobs(self) -> Iterator[Job]:
        for job in self._jobs.values():
            yield job

    @property
    def metrics(self) -> List[str]:
        return self._metrics

    @metrics.setter
    def metrics(self, metrics: List[str]) -> None:
        self._metrics = metrics

    @property
    def comparison(self) -> str:
        return self._comparison

    @comparison.setter
    def comparison(self, comparison: str) -> None:
        self._comparison = comparison

    @property
    def fraction(self) -> Tuple[int, int]:
        return self._fraction or (-1, -1)

    @fraction.setter
    def fraction(self, fraction: Tuple[int, int]) -> None:
        self._fraction = fraction

    @property
    def tasks(self) -> Iterator[Task]:
        for job in self.jobs:
            for task in job.tasks:
                yield task

    def get_jobs_id(self) -> List[int]:
        return [id for id in self._jobs.keys()]

    def get_job_by_id(self, id: int) -> Job:
        return self._jobs[id]

    def run(
        self, output_dir: str, normalize: bool = False
    ) -> Dict[str, List[List[float]]]:
        tasks = self._preprocess_tasks(self.comparison, normalize)
        tasks_dict = {k: v for k, v in tasks}

        results: Dict[str, List[List[float]]] = {}
        for metric in self.metrics:
            res = self._compare_tasks(tasks_dict, metric)
            results[metric] = res

        return results

    def _preprocess_tasks(
        self, comp: str, normalize: bool
    ) -> Iterator[Tuple[str, pd.DataFrame]]:
        if not self.time_configured:
            self._configure_time()

        if comp == "fraction":
            llim, ulim = (
                self.fraction if self.fraction else self._pick_random_fraction()
            )
            tasks = self._get_sliced_tasks(llim, ulim)
        elif comp == "pad":
            max_len = self._find_max_task_len()
            tasks = self._get_padded_tasks(max_len)
        elif comp == "trim":
            min_len = self._find_min_task_len()
            tasks = self._get_trimmed_tasks(min_len)
        else:
            raise ValueError(f"'{comp}' is not a valid comparison name!")

        if normalize:
            return self._get_normalized_tasks(tasks)

        return tasks

    def _configure_time(self) -> None:
        # * Universal for all experiments, performs in place transformations
        for job in self.jobs:
            for task in job.tasks:
                task.convert_ts_col("time", "us")
                task.adjust_freq("time", "5min")

        self.time_configured = True

    def _get_normalized_tasks(
        self, tasks: Iterator[Tuple[str, pd.DataFrame]]
    ) -> Iterator[Tuple[str, pd.DataFrame]]:
        print("Continuing... [NotImplemented normalization function]")
        return tasks

    def _pick_random_fraction(self) -> Tuple[int, int]:
        min_len = self._find_min_task_len()
        ulim = random.randint(1, min_len)
        return (0, ulim)

    def _find_max_task_len(self) -> int:
        len_of_tasks = [
            task.data.shape[0] for job in self.jobs for task in job.tasks
        ]
        max_len: int = max(len_of_tasks) if len_of_tasks else 0

        return max_len

    def _find_min_task_len(self) -> int:
        len_of_tasks = [
            task.data.shape[0] for job in self.jobs for task in job.tasks
        ]
        min_len: int = min(len_of_tasks) if len_of_tasks else 0

        return min_len

    def _get_sliced_tasks(
        self, llim: int, ulim: int
    ) -> Iterator[Tuple[str, pd.DataFrame]]:
        for task in self.tasks:
            uid = f"{task.job_id}-{task.idx}"
            data = task.get_fraction(llim, ulim)
            yield uid, data

    def _get_padded_tasks(self, lim: int) -> Iterator[Tuple[str, pd.DataFrame]]:
        for task in self.tasks:
            uid = f"{task.job_id}-{task.idx}"
            data = task.pad_task(lim)
            yield uid, data

    def _get_trimmed_tasks(
        self, lim: int
    ) -> Iterator[Tuple[str, pd.DataFrame]]:
        for task in self.tasks:
            uid = f"{task.job_id}-{task.idx}"
            data = task.get_fraction(0, lim)
            yield uid, data

    def _compare_tasks(
        self, tasks: Dict[str, pd.DataFrame], metric: str
    ) -> List[List[float]]:
        cls = Experiment._get_metric_class(metric)
        metric_obj = cls()

        out: List[List[float]] = []
        for task1 in tasks.values():
            comparisons = []
            for task2 in tasks.values():
                # TODO: Add argument for column instead of avg_cpu_usage
                comp = metric_obj.compare(task1, task2, "avg_cpu_usage")
                comparisons.append(comp)
            out.append(comparisons)

        return out

    @classmethod
    def _get_metric_class(cls, metric: str) -> Type[Metric]:
        if metric in Experiment.available_metrics:
            metric_type = Experiment.available_metrics[metric]
        module_name, metric_class_name = metric_type.rsplit(".", 1)

        metric_class: Type[Metric] = import_class(
            module_name, metric_class_name, "Metric"
        )

        return metric_class

    def _read_experiment_input(self, dir: str) -> List[Job]:
        job_ids = self._get_job_ids(dir)

        jobs: List[Job] = []
        for job_id in job_ids:
            job_folder = os.path.join(dir, str(job_id))
            tasks = self._get_input_tasks(job_folder)

            new_job = Job(job_id, tasks)
            jobs.append(new_job)

        return jobs

    def _get_input_tasks(self, dir: str) -> List[InputTask]:
        ts_filenames = self._get_ts_filenames(dir)

        tasks: List[InputTask] = []
        for filename in ts_filenames:
            idx = self._get_task_idx(filename)

            ts_path = os.path.join(dir, filename)
            data = self._get_task_data(ts_path)

            new_task = InputTask(idx, data)
            tasks.append(new_task)

        return tasks

    def _get_task_data(self, path: str) -> pd.DataFrame:
        # TODO: Sort data before returning
        # TODO: Check input format (two columns only?)
        return self._read_ts_from_csv(path)

    def _get_task_idx(self, filename: str) -> int:
        return int(filename.split("-")[0])

    def _get_ts_filenames(self, dir: str, suffix: str = ".csv") -> List[str]:
        return [
            filename
            for filename in os.listdir(dir)
            if filename.endswith(suffix)
        ]

    def _get_job_ids(self, dir: str) -> List[int]:
        return [int(job_id) for job_id in os.listdir(dir)]

    def _read_ts_from_csv(self, path: str) -> pd.DataFrame:
        return pd.read_csv(path)
