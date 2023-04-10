from typing import Any, Dict

from gtd.input.input_reader import InputReader


class InputFullReader(InputReader):
    structured: bool = True

    def _read_input(self) -> Dict[str, Dict[str, Any]]:
        if self.structured:
            return self._read_structured_input()
        else:
            return self._read_unstructured_input()

    def _read_structured_input(self) -> Dict[str, Dict[str, Any]]:
        job_subdirs = self._list_subdirs()

        input_dict: Dict[str, Dict[str, Any]] = {}
        for job_subdir in job_subdirs:
            job_id = job_subdir.stem
            task_files = self._list_files(job_subdir)

            job_dict: Dict[str, Any] = {}
            for task_file in task_files:
                task_idx = task_file.stem.split("-")[0]
                data = self._read_file(task_file)

                job_dict[task_idx] = data

            input_dict[job_id] = job_dict

        return input_dict

    def _read_unstructured_input(self) -> Dict[str, Dict[str, Any]]:
        task_files = self._list_files(self.input_dir)

        input_dict: Dict[str, Dict[str, Any]] = {}
        for task_file in task_files:
            job_id, task_idx = task_file.stem.split("-")[:2]
            data = self._read_file(task_file)

            if job_id not in input_dict:
                input_dict[job_id] = {}

            input_dict[job_id][task_idx] = data

        return input_dict
