import warnings

from gtd.internal import Input
from gtd.preprocessor.preprocessor import Preprocessor


class Trimmer(Preprocessor):
    def run(self, input_obj: Input) -> Input:
        lim = self._find_min_task_len(input_obj)

        for task in input_obj.get_tasks():
            if len(task.fractions) > 1:
                warnings.warn(
                    f"""Task {task.job_id}-{task.idx}:
                        Can't trim a task with multiple fractions.
                        Continuing to the next one."""
                )
                continue

            task.get_fraction_by_idx(0).data = task.get_fraction_by_idx(0).data[
                0:lim
            ]

        return input_obj

    def _find_min_task_len(self, input_obj: Input) -> int:
        len_of_tasks = []
        for task in input_obj.get_tasks():
            if len(task.fractions) > 1:
                continue

            len_of_tasks.append(task.get_fraction_by_idx(0).data.shape[0])

        min_len: int = min(len_of_tasks) if len_of_tasks else 0

        return min_len
