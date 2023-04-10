import numpy as np

from gtd.internal import Fraction
from gtd.preprocessor.preprocessor import FractionPreprocessor


class FractionIoUPreprocessor(FractionPreprocessor):
    epsilon: int
    border_size: int = 1

    def _run(self, fraction: Fraction) -> None:
        border_rows = np.full(
            (self.border_size, fraction.data.shape[1]), 255, dtype=int
        )
        padded_img = np.vstack([border_rows, fraction.data, border_rows])

        columns = padded_img.shape[1]

        # for each column in the picture find the index of
        # the higher and the lower black pixel
        # min level = index of higher black pixel
        # max level = index of lower black pixel
        # image coordinate have (0,0) in top left corner

        for i in range(columns):
            levels = np.where(padded_img[:, i] == 0)
            min_level = levels[0].min()
            max_level = levels[0].max()

            for j in range(1, self.epsilon + 1):
                # Add grey pixel on top
                padded_img[max(min_level - j, 0), i] = 127
                # Add grey pixel on bottom
                padded_img[min(max_level + j, padded_img.shape[0] - 1), i] = 127

        fraction.data = padded_img

        return
