import os
import random
from typing import Dict, Iterator, List, Optional, Tuple, Type

import pandas as pd

from gtd.experimentation import Result, ResultTask
from gtd.experimentation.job import InputTask, Job
from gtd.experimentation.metrics import Metric
from gtd.experimentation.task import Task
from gtd.utils import import_class
from gtd.visualization.report import (
    create_metadata,
    plot_baseline,
    plot_baseline_spectrum,
    plot_dists,
    plot_single_report,
    plot_single_report_spectrum,
)


# ! Assumption 1: Input tasks are consistent (time, avg_cpu_usage) and sorted
# ! Assumption 2: Input files have consistent naming and are csv files
# !               consistent naming: (task_idx-sample_start-sample_end)
# ! Assumption 3: Input folder structure is consistent job/<tasks-csvs>
class Experiment:
    available_metrics = {
        "l1": "gtd.experimentation.metrics.L1Metric",
        "l2": "gtd.experimentation.metrics.L2Metric",
        "spectrum": "gtd.experimentation.metrics.SpectrumMetric",
        "spectrummse": "gtd.experimentation.metrics.SpectrumMSEMetric",
        "spectrumssim": "gtd.experimentation.metrics.SpectrumSSIMMetric",
        "img100mse": "gtd.experimentation.metrics.Img100MSEMetric",
        "img64mse": "gtd.experimentation.metrics.Img64MSEMetric",
        "img128mse": "gtd.experimentation.metrics.Img128MSEMetric",
        "img100ssim": "gtd.experimentation.metrics.Img100SSIMMetric",
        "img64ssim": "gtd.experimentation.metrics.Img64SSIMMetric",
        "img128ssim": "gtd.experimentation.metrics.Img128SSIMMetric",
        "dtwl2": "gtd.experimentation.metrics.DTWL2Metric",
    }

    def __init__(
        self,
        name: str,
        input_dir: str,
    ):
        self._name = name
        self._jobs = {
            job.id: job for job in self._read_experiment_input(input_dir)
        }

        self.time_configured = False

    def __str__(self) -> str:
        return f"""Experiment( \
            name={self.name},
            jobs={self._jobs}
        )"""

    @property
    def name(self) -> str:
        return self._name

    @property
    def jobs(self) -> Iterator[Job]:
        for job in self._jobs.values():
            yield job

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
        self,
        metrics: List[str],
        sizing_type: str,
        fraction: Optional[Tuple[int, int]] = None,
        fixed_comp_len: Optional[int] = None,
        normalize: bool = False,
    ) -> Dict[str, List[Result]]:
        processed_tasks = self._preprocess_tasks(
            sizing_type, fraction, normalize
        )
        tasks_dict = {k: v for k, v in processed_tasks}

        limit_len = sizing_type == "pad"
        results: Dict[str, List[Result]] = {}
        for metric in metrics:
            if sizing_type == "real":
                res = self._compare_tasks_real(
                    tasks_dict, metric, fixed_comp_len
                )
            else:
                res = self._compare_tasks(tasks_dict, metric, limit_len)
            results[metric] = res

        return results

    def eval_single(
        self,
        result: Result,
        metric: str,
        threshold: float,
        normalization: bool,
        output_dir: str,
    ) -> None:
        baseline_job_id = result.baseline_task.uid.split("-")[0]

        true_match = 0.0
        false_match = 0.0
        true_no_match = 0.0
        false_no_match = 0.0

        colors = []
        result.compared_tasks.sort(key=lambda x: x.dist)
        for task in result.compared_tasks:
            task_job_id = task.uid.split("-")[0]
            matching = False

            colors.append("C3" if task_job_id == baseline_job_id else "C0")

            if task.dist <= threshold:
                matching = True

            if task_job_id == baseline_job_id and matching:
                true_match = true_match + 1
            elif task_job_id == baseline_job_id and not matching:
                false_no_match = false_no_match + 1
            elif task_job_id != baseline_job_id and matching:
                false_match = false_match + 1
            else:
                true_no_match = true_no_match + 1

        conf_matrix = [
            [true_match, false_no_match],
            [false_match, true_no_match],
        ]

        if true_match + true_no_match + false_match + false_no_match == 0:
            accuracy = 0.0
        else:
            accuracy = (true_match + true_no_match) / (
                true_match + true_no_match + false_match + false_no_match
            )

        if true_match + false_match == 0:
            precision = 0.0
        else:
            precision = true_match / (true_match + false_match)

        if true_match + false_no_match == 0:
            recall = 0.0
        else:
            recall = true_match / (true_match + false_no_match)

        final_dir = f"{output_dir}{result.baseline_task.uid}/"
        os.makedirs(final_dir)
        if "spectrum" in metric:
            plot_baseline_spectrum(result, final_dir)
            plot_single_report_spectrum(
                result,
                self.name,
                metric,
                threshold,
                normalization,
                conf_matrix,
                accuracy,
                precision,
                recall,
                colors,
                final_dir,
            )
        else:
            plot_baseline(result, final_dir)
            plot_single_report(
                result,
                self.name,
                metric,
                threshold,
                normalization,
                conf_matrix,
                accuracy,
                precision,
                recall,
                colors,
                final_dir,
            )
        plot_dists(result, colors, final_dir)
        create_metadata(result, metric, threshold, normalization, final_dir)

    def _preprocess_tasks(
        self,
        sizing_type: str,
        fraction: Optional[Tuple[int, int]],
        normalize: bool,
    ) -> Iterator[Tuple[str, pd.DataFrame]]:
        if not self.time_configured:
            self._configure_time()

        if sizing_type == "fraction":
            llim, ulim = fraction if fraction else self._pick_random_fraction()
            tasks = self._get_sliced_tasks(llim, ulim)
        elif sizing_type == "pad":
            max_len = self._find_max_task_len()
            tasks = self._get_padded_tasks(max_len)
        elif sizing_type == "trim":
            min_len = self._find_min_task_len()
            tasks = self._get_trimmed_tasks(min_len)
        elif sizing_type in ["full", "real"]:
            tasks = self._get_full_tasks()
        else:
            raise ValueError(f"'{sizing_type}' is not a valid sizing type!")

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
        col = "avg_cpu_usage"
        for uid, data in tasks:
            data[col] = (data[col] - data[col].min()) / (
                data[col].max() - data[col].min()
            )
            yield uid, data

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

    def _get_full_tasks(self) -> Iterator[Tuple[str, pd.DataFrame]]:
        for task in self.tasks:
            uid = f"{task.job_id}-{task.idx}"
            data = task.data
            yield uid, data

    def _compare_tasks(
        self, tasks: Dict[str, pd.DataFrame], metric: str, limit_len: bool
    ) -> List[Result]:
        cls = Experiment._get_metric_class(metric)
        metric_obj = cls()

        out: List[Result] = []

        for baseline_task_uid, baseline_task_data in tasks.items():
            baseline_job_id, baseline_task_idx = baseline_task_uid.split("-")
            comparison_len = (
                self.get_job_by_id(int(baseline_job_id))
                .get_task_by_idx(int(baseline_task_idx))
                .data.shape[0]
                if limit_len
                else None
            )
            baseline_task = ResultTask(
                baseline_task_uid, baseline_task_data[:comparison_len], 0
            )

            compared_tasks: List[ResultTask] = []
            for task_uid, task_data in tasks.items():
                task_job_id, task_idx = task_uid.split("-")

                if (
                    task_job_id == baseline_job_id
                    and task_idx == baseline_task_idx
                ):
                    continue

                # TODO: Add argument for column instead of avg_cpu_usage
                dist = metric_obj.compare(
                    baseline_task_data[:comparison_len],
                    task_data[:comparison_len],
                    "avg_cpu_usage",
                )

                compared_tasks.append(
                    ResultTask(task_uid, task_data[:comparison_len], dist)
                )

            out.append(Result(baseline_task, compared_tasks))

        return out

    def _compare_tasks_real(
        self,
        tasks: Dict[str, pd.DataFrame],
        metric: str,
        fixed_comp_len: Optional[int] = None,
    ) -> List[Result]:
        cls = Experiment._get_metric_class(metric)
        metric_obj = cls()

        out: List[Result] = []

        for baseline_task_uid, baseline_task_data in tasks.items():
            baseline_job_id, baseline_task_idx = baseline_task_uid.split("-")
            baseline_task = ResultTask(baseline_task_uid, baseline_task_data, 0)

            compared_tasks: List[ResultTask] = []
            for task_uid, task_data in tasks.items():
                task_job_id, task_idx = task_uid.split("-")

                task_len = task_data.shape[0]
                random_len = (
                    random.randint(100, task_len)
                    if task_len > 100
                    else task_len
                )
                comparison_len = fixed_comp_len or random_len

                if (
                    task_job_id == baseline_job_id
                    and task_idx == baseline_task_idx
                ):
                    continue

                # TODO: Add argument for column instead of avg_cpu_usage
                dist = metric_obj.compare(
                    baseline_task_data,
                    task_data[:comparison_len],
                    "avg_cpu_usage",
                )

                compared_tasks.append(
                    ResultTask(task_uid, task_data[:comparison_len], dist)
                )

            out.append(Result(baseline_task, compared_tasks))

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
