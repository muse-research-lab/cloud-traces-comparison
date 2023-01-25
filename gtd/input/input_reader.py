from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

from pydantic import BaseModel

from gtd.internal import Fraction, Input, Job, Task


class InputReader(BaseModel, ABC):
    input_dir: Path

    @property
    @abstractmethod
    def filetype(self) -> str:
        pass

    def read_input(self) -> Input:
        input_dict = self._read_input()
        return self._dict_to_input(input_dict)

    @abstractmethod
    def _read_input(self) -> Dict[str, Dict[str, Any]]:
        pass

    @abstractmethod
    def _read_file(self, file: Path) -> Any:
        pass

    def _dict_to_input(self, input_dict: Dict[str, Dict[str, Any]]) -> Input:
        jobs: Dict[int, Job] = {}
        for job_id_str, tasks_dict in input_dict.items():
            job_id = int(job_id_str)

            tasks: Dict[int, Task] = {}
            for task_idx_str, fractions_data in tasks_dict.items():
                task_idx = int(task_idx_str)

                fractions: Dict[int, Fraction] = {}
                if type(fractions_data) is dict:
                    for fraction_idx_str, data in fractions_data.items():
                        fraction_idx = int(fraction_idx_str)

                        fractions[fraction_idx] = Fraction(
                            task_idx=task_idx,
                            idx=fraction_idx,
                            data=data,
                        )
                else:
                    fractions[0] = Fraction(
                        task_idx=task_idx,
                        idx=0,
                        data=fractions_data,
                    )

                tasks[task_idx] = Task(
                    job_id=job_id, idx=task_idx, fractions=fractions
                )

            jobs[job_id] = Job(id=job_id, tasks=tasks)

        return Input(jobs=jobs)

    def _list_subdirs(self) -> List[Path]:
        return [x for x in self.input_dir.iterdir() if x.is_dir()]

    def _list_files(self, dir: Path) -> List[Path]:
        pattern = f"*.{self.filetype}"

        return list(dir.glob(pattern))
