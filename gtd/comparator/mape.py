from typing import List

from gtd.comparator.calculators import mape, mape_img
from gtd.comparator.comparator import TaskComparator
from gtd.internal import Task


class MAPETaskComparator(TaskComparator):
    col: str

    def _compare(self, task1: Task, task2: Task) -> float:
        data1 = task1.get_fraction_by_idx(0).data
        data2 = task2.get_fraction_by_idx(0).data

        assert data1.shape[0] == data2.shape[0]

        return mape(data1[self.col], data2[self.col])


class MAPEImageTaskComparator(TaskComparator):
    def _compare(self, task1: Task, task2: Task) -> float:
        data1 = task1.get_fraction_by_idx(0).data
        data2 = task2.get_fraction_by_idx(0).data

        assert data1.shape == data2.shape

        return mape_img(data1, data2)


class MAPETaskFractionComparator(TaskComparator):
    col: str

    def _compare(self, task1: Task, task2: Task) -> List[float]:
        fractions1_len = len(task1.get_fraction_idxs())
        fractions2_len = len(task2.get_fraction_idxs())

        assert fractions1_len == fractions2_len

        dists = []
        for i in range(fractions1_len):
            fr1 = task1.get_fraction_by_idx(i)
            fr2 = task2.get_fraction_by_idx(i)

            dists.append(mape(fr1.data[self.col], fr2.data[self.col]))

        return dists


class MAPEImageTaskFractionComparator(TaskComparator):
    def _compare(self, task1: Task, task2: Task) -> List[float]:
        fractions1_len = len(task1.get_fraction_idxs())
        fractions2_len = len(task2.get_fraction_idxs())

        assert fractions1_len == fractions2_len

        dists = []
        for i in range(fractions1_len):
            fr1 = task1.get_fraction_by_idx(i)
            fr2 = task2.get_fraction_by_idx(i)

            dists.append(mape_img(fr1.data, fr2.data))

        return dists
