from abc import abstractmethod
from pathlib import Path
from typing import Any, Dict

from gtd.input.input_reader import InputReader


class InputFractionReader(InputReader):
    structured: bool = True

    def read_input(self) -> Dict[str, Any]:
        if self.structured:
            return self._read_structured_input()
        else:
            return self._read_unstructured_input()

    def _read_structured_input(self) -> Dict[str, Any]:
        task_subdirs = self._list_subdirs()

        input_dict: Dict[str, Any] = {}
        for task_subdir in task_subdirs:
            uid = self._get_uid_structured(task_subdir)
            fraction_files = self._list_files(task_subdir)

            fraction_data = {}
            for fraction_file in fraction_files:
                idx = fraction_file.stem
                data = self._read_file(fraction_file)

                fraction_data[idx] = data

            input_dict[uid] = fraction_data

        return input_dict

    def _read_unstructured_input(self) -> Dict[str, Any]:
        task_files = self._list_files(self.input_dir)

        input_dict: Dict[str, Any] = {}
        for task_file in task_files:
            uid = self._get_uid_unstructured(task_file)
            idx = task_file.stem.split("-")[2]
            data = self._read_file(task_file)

            if uid not in input_dict:
                input_dict[uid] = {}

            input_dict[uid][idx] = data

        return input_dict

    @abstractmethod
    def _get_uid_structured(self, dir: Path) -> str:
        pass

    @abstractmethod
    def _get_uid_unstructured(self, file: Path) -> str:
        pass

    @abstractmethod
    def _read_file(self, file: Path) -> Any:
        pass
