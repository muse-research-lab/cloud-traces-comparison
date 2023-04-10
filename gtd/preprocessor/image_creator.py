import cv2
import numpy as np

from gtd.internal import Fraction
from gtd.preprocessor.preprocessor import FractionPreprocessor


class FractionImageCreator(FractionPreprocessor):
    col: str
    image_size: int

    def _run(self, fraction: Fraction) -> None:
        fraction.data = fraction.data[self.col].apply(
            lambda x: x * (self.image_size - 1)
        )

        data_arr = fraction.data.to_numpy(dtype=np.uint8)

        img = np.full((self.image_size, self.image_size), 255, dtype=np.uint8)

        pts = []
        for idx, elem in enumerate(data_arr):
            pts.append([idx, abs(self.image_size - 1 - elem)])

        pts_arr = [np.array(pts)]

        img_poly = cv2.polylines(
            img, pts_arr, isClosed=False, color=(0, 0, 0), thickness=0
        )

        fraction.data = img_poly

        return
