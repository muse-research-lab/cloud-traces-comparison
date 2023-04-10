import warnings

import pandas as pd

from gtd.internal import Task
from gtd.preprocessor.preprocessor import TaskPreprocessor


class TaskNormalizer(TaskPreprocessor):
    col: str

    def _run(self, task: Task) -> None:
        if len(task.fractions) > 1:
            warnings.warn(
                f"""Task {task.job_id}-{task.idx}:
                    Can't normalize in a task with multiple fractions.
                    Continuing to the next one."""
            )
            return

        data = task.get_fraction_by_idx(0).data
        self._normalize(data)

        return

    def _normalize(self, data: pd.DataFrame) -> None:
        # Normalize between 0 and 1
        data[self.col] = (data[self.col] - data[self.col].min()) / (
            data[self.col].max() - data[self.col].min()
        )

        return
