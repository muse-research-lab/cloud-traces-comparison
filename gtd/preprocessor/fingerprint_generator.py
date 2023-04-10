from typing import List

import numpy as np

from gtd.internal import Fraction
from gtd.preprocessor.preprocessor import FractionPreprocessor


class FractionFingerprintGenerator(FractionPreprocessor):
    col: str
    fs: float = 1 / (5 * 60)
    n_top: int = 5

    def _run(self, fraction: Fraction) -> None:
        dft = np.fft.fft(fraction.data[self.col])

        N = len(dft)
        n = np.arange(N)
        T = N / self.fs
        freq = n / T

        # Remove freq = 0
        dft[0] = 0

        n_oneside = N // 2
        # get the one side frequency
        f_oneside = freq[:n_oneside]

        dft_oneside = dft[:n_oneside]

        # normalize the amplitude
        dft_oneside = dft_oneside / n_oneside

        top_freq_idxs = np.argsort(abs(dft_oneside))[-self.n_top :]

        top_freqs = []
        for i in reversed(top_freq_idxs):
            top_freqs.append(f_oneside[i])

        # h = self._hash(top_freqs)

        h = [int(x * 10000000) for x in top_freqs]

        fraction.data = h

        return

    def _hash(self, top_freqs: List[float]) -> float:
        return 0.0
