from typing import Any, Dict

from gtd.input.input_reader import InputReader


class InputFractionReader(InputReader):
    structured: bool = True

    def _read_input(self) -> Dict[str, Dict[str, Any]]:
        if self.structured:
            return self._read_structured_input()
        else:
            return self._read_unstructured_input()

    def _read_structured_input(self) -> Dict[str, Dict[str, Any]]:
        task_subdirs = self._list_subdirs()

        input_dict: Dict[str, Dict[str, Any]] = {}
        for task_subdir in task_subdirs:
            job_id, task_idx = task_subdir.stem.split("-")[:2]
            fraction_files = self._list_files(task_subdir)

            fraction_data = {}
            for fraction_file in fraction_files:
                idx = fraction_file.stem
                data = self._read_file(fraction_file)

                fraction_data[idx] = data

            if job_id not in input_dict:
                input_dict[job_id] = {}

            input_dict[job_id][task_idx] = fraction_data

        return input_dict

    def _read_unstructured_input(self) -> Dict[str, Dict[str, Any]]:
        task_files = self._list_files(self.input_dir)

        input_dict: Dict[str, Dict[str, Any]] = {}
        for task_file in task_files:
            job_id, task_idx, fraction_idx = task_file.stem.split("-")[:3]
            data = self._read_file(task_file)

            if job_id not in input_dict:
                input_dict[job_id] = {}

            if task_idx not in input_dict[job_id]:
                input_dict[job_id][task_idx] = {}

            input_dict[job_id][task_idx][fraction_idx] = data

        return input_dict
