from pathlib import Path
from typing import Dict

import cv2
import numpy as np
from pydantic import root_validator

from gtd.input.input_fraction_reader import InputFractionReader


class ImageFractionReader(InputFractionReader):
    # TODO: Fix with upcoming __post_init__ method
    @root_validator()
    def validate_filetype(cls, values: Dict) -> Dict:
        if values["filetype"] == "*":
            values["filetype"] = "png"

        return values

    def _get_uid_structured(self, dir: Path) -> str:
        job_id, task_idx = dir.stem.split("-")[:2]

        return f"{job_id}-{task_idx}"

    def _get_uid_unstructured(self, file: Path) -> str:
        job_id, task_idx = file.stem.split("-")[:2]

        return f"{job_id}-{task_idx}"

    def _read_file(self, file: Path) -> np.ndarray:
        img: np.ndarray = cv2.imread(str(file), cv2.IMREAD_GRAYSCALE)

        return img
