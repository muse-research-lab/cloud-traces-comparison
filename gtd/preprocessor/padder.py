import warnings

import pandas as pd

from gtd.internal import Input
from gtd.preprocessor.preprocessor import Preprocessor


class Padder(Preprocessor):
    freq: str

    def run(self, input_obj: Input) -> Input:
        lim = self._find_max_task_len(input_obj)

        for task in input_obj.get_tasks():
            if len(task.fractions) > 1:
                warnings.warn(
                    f"""Task {task.job_id}-{task.idx}:
                        Can't trim a task with multiple fractions.
                        Continuing to the next one."""
                )
                continue

            task.get_fraction_by_idx(0).data = self._pad_task(
                lim, task.get_fraction_by_idx(0).data
            )

        return input_obj

    def _find_max_task_len(self, input_obj: Input) -> int:
        len_of_tasks = []
        for task in input_obj.get_tasks():
            if len(task.fractions) > 1:
                continue

            len_of_tasks.append(task.get_fraction_by_idx(0).data.shape[0])

        max_len: int = max(len_of_tasks) if len_of_tasks else 0

        return max_len

    def _pad_task(self, lim: int, data: pd.DataFrame) -> pd.DataFrame:
        task_len = data.shape[0]

        k, m = divmod(lim, task_len)

        for i in range(k - 1):
            new_data = data.shift(periods=task_len * (i + 1), freq=self.freq)[
                :task_len
            ]
            data = pd.concat([data, new_data])

        if m != 0:
            new_data = data.shift(periods=task_len * k, freq=self.freq)[:m]
            data = pd.concat([data, new_data])

        return data
