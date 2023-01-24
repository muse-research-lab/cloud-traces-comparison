from abc import abstractmethod
from pathlib import Path
from typing import Any, Dict

from gtd.input.input_reader import InputReader


class InputFullReader(InputReader):
    structured: bool = True

    def read_input(self) -> Dict[str, Any]:
        if self.structured:
            return self._read_structured_input()
        else:
            return self._read_unstructured_input()

    def _read_structured_input(self) -> Dict[str, Any]:
        job_subdirs = self._list_subdirs()

        input_dict: Dict[str, Any] = {}
        for job_subdir in job_subdirs:
            task_files = self._list_files(job_subdir)

            for task_file in task_files:
                uid = self._get_uid_structured(task_file)
                data = self._read_file(task_file)

                input_dict[uid] = data

        return input_dict

    def _read_unstructured_input(self) -> Dict[str, Any]:
        task_files = self._list_files(self.input_dir)

        input_dict: Dict[str, Any] = {}
        for task_file in task_files:
            uid = self._get_uid_unstructured(task_file)
            data = self._read_file(task_file)

            input_dict[uid] = data

        return input_dict

    @abstractmethod
    def _get_uid_structured(self, file: Path) -> str:
        pass

    @abstractmethod
    def _get_uid_unstructured(self, file: Path) -> str:
        pass

    @abstractmethod
    def _read_file(self, file: Path) -> Any:
        pass
