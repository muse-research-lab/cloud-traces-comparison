from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from pydantic import root_validator

from gtd.input.input_full_reader import InputFullReader


class CsvReader(InputFullReader):
    columns: Optional[List[str]]

    # TODO: Fix with upcoming __post_init__ method
    @root_validator()
    def validate_filetype(cls, values: Dict) -> Dict:
        values["filetype"] = "csv"

        return values

    def _get_uid_structured(self, file: Path) -> str:
        job_id = file.parent.stem
        task_idx = file.stem.split("-")[0]

        return f"{job_id}-{task_idx}"

    def _get_uid_unstructured(self, file: Path) -> str:
        job_id = file.stem.split("-")[0]
        task_idx = file.stem.split("-")[1]

        return f"{job_id}-{task_idx}"

    def _read_file(self, file: Path) -> pd.DataFrame:
        return pd.read_csv(filepath_or_buffer=file, usecols=self.columns)
