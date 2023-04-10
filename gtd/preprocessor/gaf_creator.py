from typing import Tuple

import numpy as np
from pyts.image import GramianAngularField

from gtd.internal import Fraction
from gtd.preprocessor.preprocessor import FractionPreprocessor


class FractionGADFCreator(FractionPreprocessor):
    col: str
    image_size: int
    sample_range: Tuple[float, float] = (-1.0, 1.0)

    def _run(self, fraction: Fraction) -> None:
        fraction.data = fraction.data[self.col]

        data_arr = fraction.data.to_numpy(dtype=np.float64).reshape(1, -1)

        gadf = GramianAngularField(
            self.image_size, method="difference", sample_range=self.sample_range
        )
        X_gadf = gadf.fit_transform(data_arr)

        fraction.data = X_gadf[0]

        return


class FractionGASFCreator(FractionPreprocessor):
    col: str
    image_size: int
    sample_range: Tuple[float, float] = (-1.0, 1.0)

    def _run(self, fraction: Fraction) -> None:
        fraction.data = fraction.data[self.col]

        data_arr = fraction.data.to_numpy(dtype=np.float64).reshape(1, -1)

        gasf = GramianAngularField(
            self.image_size, method="summation", sample_range=self.sample_range
        )
        X_gasf = gasf.fit_transform(data_arr)

        fraction.data = X_gasf[0]

        return
