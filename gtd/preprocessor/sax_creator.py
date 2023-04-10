import warnings

from pyts.approximation import SymbolicAggregateApproximation as SAX

from gtd.internal import Fraction, Task
from gtd.preprocessor.preprocessor import FractionPreprocessor, TaskPreprocessor


class FractionSAXCreator(FractionPreprocessor):
    col: str
    n_bins: int

    def _run(self, fraction: Fraction) -> None:
        X = fraction.data[self.col].to_numpy().reshape(1, -1)

        sax = SAX(n_bins=self.n_bins, strategy="uniform")
        X_sax = sax.fit_transform(X)

        fraction.data = X_sax

        return


class TaskSAXCreator(TaskPreprocessor):
    col: str
    n_bins: int

    def _run(self, task: Task) -> None:
        if len(task.fractions) > 1:
            warnings.warn(
                f"""Task {task.job_id}-{task.idx}:
                    Can't use sax transformer in a task with multiple fractions.
                    Continuing to the next one."""
            )
            return

        X = task.get_fraction_by_idx(0).data[self.col].to_numpy().reshape(1, -1)

        sax = SAX(n_bins=self.n_bins, strategy="uniform")
        X_sax = sax.fit_transform(X)

        task.get_fraction_by_idx(0).data = X_sax

        return
