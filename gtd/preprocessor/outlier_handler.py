import warnings

from gtd.internal import Task
from gtd.preprocessor.preprocessor import TaskPreprocessor


class OutlierHandler(TaskPreprocessor):
    col: str
    llim: float
    ulim: float

    def _run(self, task: Task) -> None:
        if len(task.fractions) > 1:
            warnings.warn(
                f"""Task {task.job_id}-{task.idx}:
                    Can't handle outliers in a task with multiple fractions.
                    Continuing to the next one."""
            )
            return

        data = task.get_fraction_by_idx(0).data

        pct_lower = data[self.col].quantile(self.llim)
        pct_upper = data[self.col].quantile(self.ulim)

        data[self.col].mask(data[self.col] > pct_upper, pct_upper, inplace=True)
        data[self.col].mask(data[self.col] < pct_lower, pct_lower, inplace=True)

        return
