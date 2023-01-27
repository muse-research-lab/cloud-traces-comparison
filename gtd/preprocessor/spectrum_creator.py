from matplotlib.mlab import specgram

from gtd.internal import Fraction
from gtd.preprocessor.preprocessor import FractionPreprocessor


class SpectrumCreator(FractionPreprocessor):
    col: str
    fs: float = 1 / (5 * 60)

    def _run(self, fraction: Fraction) -> None:
        NFFT = min(fraction.data.shape[0], 72)
        noverlap = round(NFFT / 2)

        spectrum, _, _ = specgram(
            fraction.data[self.col], Fs=self.fs, NFFT=NFFT, noverlap=noverlap
        )

        fraction.data = spectrum

        return
