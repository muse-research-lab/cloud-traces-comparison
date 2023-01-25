from pathlib import Path
from typing import List, Optional

import pandas as pd

from gtd.input.input_reader import InputReader


class CsvReader(InputReader):
    columns: Optional[List[str]]

    @property
    def filetype(self) -> str:
        return "csv"

    def _read_file(self, file: Path) -> pd.DataFrame:
        return pd.read_csv(filepath_or_buffer=file, usecols=self.columns)
