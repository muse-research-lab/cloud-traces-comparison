from typing import List

import numpy as np

from gtd.comparator.calculators import sdsim, sdsim_img, ssim, ssim_img
from gtd.comparator.comparator import TaskComparator
from gtd.internal import Task


class SSIMTaskComparator(TaskComparator):
    col: str

    def _compare(self, task1: Task, task2: Task) -> float:
        data1 = task1.get_fraction_by_idx(0).data
        data2 = task2.get_fraction_by_idx(0).data

        assert data1.shape[0] == data2.shape[0]

        return ssim(data1[self.col], data2[self.col])


class SSIMImageTaskComparator(TaskComparator):
    def _compare(self, task1: Task, task2: Task) -> float:
        data1 = task1.get_fraction_by_idx(0).data
        data2 = task2.get_fraction_by_idx(0).data

        assert data1.shape == data2.shape

        return ssim_img(data1, data2)


class SSIMTaskFractionComparator(TaskComparator):
    col: str

    def _compare(self, task1: Task, task2: Task) -> List[float]:
        fractions1_len = len(task1.get_fraction_idxs())
        fractions2_len = len(task2.get_fraction_idxs())

        assert fractions1_len == fractions2_len

        dists = []
        for i in range(fractions1_len):
            fr1 = task1.get_fraction_by_idx(i)
            fr2 = task2.get_fraction_by_idx(i)

            dists.append(ssim(fr1.data[self.col], fr2.data[self.col]))

        return dists


class SSIMImageTaskFractionComparator(TaskComparator):
    def _compare(self, task1: Task, task2: Task) -> List[float]:
        fractions1_len = len(task1.get_fraction_idxs())
        fractions2_len = len(task2.get_fraction_idxs())

        assert fractions1_len == fractions2_len

        dists = []
        for i in range(fractions1_len):
            fr1 = task1.get_fraction_by_idx(i)
            fr2 = task2.get_fraction_by_idx(i)

            dists.append(ssim_img(fr1.data, fr2.data))

        return dists


class SDSIMImageTaskFractionComparator(TaskComparator):
    def _compare(self, task1: Task, task2: Task) -> float:
        fractions1_len = len(task1.get_fraction_idxs())
        fractions2_len = len(task2.get_fraction_idxs())

        assert fractions1_len == fractions2_len

        task_data1 = task1.get_fraction_by_idx(0).data
        task_data2 = task2.get_fraction_by_idx(0).data
        for i in range(1, fractions1_len):
            task_data1 = np.append(
                task_data1, task1.get_fraction_by_idx(i).data, axis=1
            )
            task_data2 = np.append(
                task_data2, task2.get_fraction_by_idx(i).data, axis=1
            )

        return sdsim_img(task_data1, task_data2)


class SDSIMTaskComparator(TaskComparator):
    col: str

    def _compare(self, task1: Task, task2: Task) -> float:
        data1 = task1.get_fraction_by_idx(0).data
        data2 = task2.get_fraction_by_idx(0).data

        assert data1.shape[0] == data2.shape[0]

        return sdsim(data1[self.col], data2[self.col])
