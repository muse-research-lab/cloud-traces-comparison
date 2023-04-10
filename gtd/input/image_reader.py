from pathlib import Path

import cv2
import numpy as np

from gtd.input.input_reader import InputReader


class ImageReader(InputReader):
    @property
    def filetype(self) -> str:
        return "png"

    def _read_file(self, file: Path) -> np.ndarray:
        img: np.ndarray = cv2.imread(str(file), cv2.IMREAD_GRAYSCALE)

        return img
