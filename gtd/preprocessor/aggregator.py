from gtd.internal import Fraction
from gtd.preprocessor.preprocessor import FractionPreprocessor


class FractionAggregator(FractionPreprocessor):
    col: str
    ts_to_px_ratio: int

    def _run(self, fraction: Fraction) -> None:
        fraction.data[self.col] = (
            fraction.data[self.col]
            .rolling(self.ts_to_px_ratio)
            .mean()
            .loc[self.ts_to_px_ratio - 1 :: self.ts_to_px_ratio]
        )
        fraction.data = fraction.data[fraction.data[self.col].notnull()]

        return
