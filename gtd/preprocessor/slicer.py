import warnings
from typing import Dict, List, Tuple

from gtd.internal import Fraction, Task
from gtd.preprocessor.preprocessor import TaskPreprocessor


class TaskSlicer(TaskPreprocessor):
    step: int

    def _run(self, task: Task) -> None:
        if len(task.fractions) > 1:
            warnings.warn(
                f"""Task {task.job_id}-{task.idx} is already sliced!
                    Continuing to the next one."""
            )
            return

        task_ts = task.get_fraction_by_idx(0).data.shape[0]
        slices = self._get_slices(0, task_ts)

        new_fractions: Dict[int, Fraction] = {}
        for i, slice in enumerate(slices):
            llim, ulim = slice
            data = task.get_fraction_by_idx(0).data[llim:ulim].copy()

            new_fractions[i] = Fraction(
                job_id=task.job_id, task_idx=task.idx, idx=i, data=data
            )

        task.fractions = new_fractions

        return

    def _get_slices(self, start: int, end: int) -> List[Tuple[int, int]]:
        n = end - start
        k, m = divmod(n, self.step)

        if k == 0:
            return []
        else:
            return [(start, start + self.step)] + self._get_slices(
                start + self.step, end
            )
