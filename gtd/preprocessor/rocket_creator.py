import warnings

from pyts.transformation import ROCKET

from gtd.internal import Fraction, Task
from gtd.preprocessor.preprocessor import FractionPreprocessor, TaskPreprocessor


class FractionROCKETCreator(FractionPreprocessor):
    col: str
    n_kernels: int
    random_state: int = 42

    def _run(self, fraction: Fraction) -> None:
        X = fraction.data[self.col].to_numpy().reshape(1, -1)

        rocket = ROCKET(
            n_kernels=self.n_kernels, random_state=self.random_state
        )
        X_rocket = rocket.fit_transform(X)

        fraction.data = X_rocket[0]

        return


class TaskROCKETCreator(TaskPreprocessor):
    col: str
    n_kernels: int
    random_state: int = 42

    def _run(self, task: Task) -> None:
        if len(task.fractions) > 1:
            warnings.warn(
                f"""Task {task.job_id}-{task.idx}:
                    Can't use the transformer in a task with multiple fractions.
                    Continuing to the next one."""
            )
            return

        X = task.get_fraction_by_idx(0).data[self.col].to_numpy().reshape(1, -1)

        rocket = ROCKET(
            n_kernels=self.n_kernels, random_state=self.random_state
        )

        X_rocket = rocket.fit_transform(X)

        task.get_fraction_by_idx(0).data = X_rocket[0]

        return
