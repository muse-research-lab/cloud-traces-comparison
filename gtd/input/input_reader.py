from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

from pydantic import BaseModel


class InputReader(BaseModel, ABC):
    input_dir: Path
    filetype: str = "*"

    @abstractmethod
    def read_input(self) -> Dict[str, Any]:
        pass

    def _list_subdirs(self) -> List[Path]:
        return [x for x in self.input_dir.iterdir() if x.is_dir()]

    def _list_files(self, dir: Path) -> List[Path]:
        pattern = f"*.{self.filetype}"

        return list(dir.glob(pattern))
