import numpy as np
from pyts.image import MarkovTransitionField

from gtd.internal import Fraction
from gtd.preprocessor.preprocessor import FractionPreprocessor


class FractionMTFCreator(FractionPreprocessor):
    col: str
    n_bins: int
    size: int = 64

    def _run(self, fraction: Fraction) -> None:
        """buckets = np.linspace(0, 1, num=self.n_bins + 1)

        transitions = np.digitize(fraction.data[self.col], buckets) - 1

        # Fix last interval
        transitions[transitions == self.n_bins] = self.n_bins - 1

        n = self.n_bins  # number of states

        matrix = [[0.0] * n for _ in range(n)]

        for (i, j) in zip(transitions, transitions[1:]):
            matrix[i][j] += 1

        # now convert to probabilities:
        for row in matrix:
            s = sum(row)
            if s > 0:
                row[:] = [f / s for f in row]

        fraction.data = matrix"""

        x = fraction.data["avg_cpu_usage"].to_numpy()
        X = np.array([x])

        mtf = MarkovTransitionField(
            self.size, n_bins=self.n_bins, strategy="uniform"
        )
        X_mtf = mtf.fit_transform(X)

        fraction.data = X_mtf[0]

        return
