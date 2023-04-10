from typing import List

import numpy as np

from gtd.comparator.calculators import l2, l2_img
from gtd.comparator.comparator import TaskComparator
from gtd.internal import Task


class L2TaskComparator(TaskComparator):
    col: str

    def _compare(self, task1: Task, task2: Task) -> float:
        data1 = task1.get_fraction_by_idx(0).data
        data2 = task2.get_fraction_by_idx(0).data

        assert data1.shape[0] == data2.shape[0]

        return l2(data1[self.col], data2[self.col])


class L2ImageTaskComparator(TaskComparator):
    def _compare(self, task1: Task, task2: Task) -> float:
        data1 = task1.get_fraction_by_idx(0).data
        data2 = task2.get_fraction_by_idx(0).data

        assert data1.shape == data2.shape

        return l2_img(data1, data2)


class L2TaskFractionComparator(TaskComparator):
    col: str

    def _compare(self, task1: Task, task2: Task) -> List[float]:
        fractions1_len = len(task1.get_fraction_idxs())
        fractions2_len = len(task2.get_fraction_idxs())

        assert fractions1_len == fractions2_len

        dists = []
        for i in range(fractions1_len):
            fr1 = task1.get_fraction_by_idx(i)
            fr2 = task2.get_fraction_by_idx(i)

            dists.append(l2(fr1.data[self.col], fr2.data[self.col]))

        return dists


class L2ImageTaskFractionComparator(TaskComparator):
    def _compare(self, task1: Task, task2: Task) -> List[float]:
        fractions1_len = len(task1.get_fraction_idxs())
        fractions2_len = len(task2.get_fraction_idxs())

        assert fractions1_len == fractions2_len

        dists = []
        for i in range(fractions1_len):
            fr1 = task1.get_fraction_by_idx(i)
            fr2 = task2.get_fraction_by_idx(i)

            dists.append(l2_img(fr1.data, fr2.data))

        return dists


class L2ImageTaskFractionComparatorV2(TaskComparator):
    def _compare(self, task1: Task, task2: Task) -> float:
        fractions1_len = len(task1.get_fraction_idxs())
        fractions2_len = len(task2.get_fraction_idxs())

        assert fractions1_len == fractions2_len

        task_data1 = np.array([])
        task_data2 = np.array([])
        for i in range(fractions1_len):
            task_data1 = np.append(
                task_data1, task1.get_fraction_by_idx(i).data.reshape(1, -1)[0]
            )
            task_data2 = np.append(
                task_data2, task2.get_fraction_by_idx(i).data.reshape(1, -1)[0]
            )

        return l2_img(task_data1, task_data2)
