import warnings

from gtd.internal import Task
from gtd.preprocessor.preprocessor import TaskPreprocessor


class Cropper(TaskPreprocessor):
    llim: int
    ulim: int

    def _run(self, task: Task) -> None:
        if len(task.fractions) > 1:
            warnings.warn(
                f"""Task {task.job_id}-{task.idx}:
                    Can't crop a task with multiple fractions.
                    Continuing to the next one."""
            )
            return

        task.get_fraction_by_idx(0).data = task.get_fraction_by_idx(0).data[
            self.llim : self.ulim
        ]

        return
