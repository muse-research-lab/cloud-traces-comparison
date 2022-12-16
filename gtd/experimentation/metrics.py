from abc import ABC, abstractmethod
from typing import List

import pandas as pd
from matplotlib.mlab import specgram


class Metric(ABC):
    @staticmethod
    @abstractmethod
    def calc_metric(data: pd.DataFrame, col: str) -> float:
        pass

    @staticmethod
    @abstractmethod
    def calc_list_metric(data: pd.DataFrame, col: str) -> List[float]:
        pass

    @staticmethod
    @abstractmethod
    def calc_matrix_metric(data: pd.DataFrame, col: str) -> List[List[float]]:
        pass

    @staticmethod
    @abstractmethod
    def compare(data1: pd.DataFrame, data2: pd.DataFrame, col: str) -> float:
        pass


class L1Metric(Metric):
    @staticmethod
    def calc_metric(data: pd.DataFrame, col: str) -> float:
        raise NotImplementedError("This method is not supported")

    @staticmethod
    def calc_list_metric(data: pd.DataFrame, col: str) -> List[float]:
        raise NotImplementedError("This method is not supported")

    @staticmethod
    def calc_matrix_metric(data: pd.DataFrame, col: str) -> List[List[float]]:
        raise NotImplementedError("This method is not supported")

    @staticmethod
    def compare(data1: pd.DataFrame, data2: pd.DataFrame, col: str) -> float:
        assert data1.shape[0] == data2.shape[0]

        dists = [
            L1Metric.calc_dist(x, y) for x, y in zip(data1[col], data2[col])
        ]

        return sum(dists)

    @staticmethod
    def calc_dist(x: float, y: float) -> float:
        return abs(x - y)


class L2Metric(Metric):
    @staticmethod
    def calc_metric(data: pd.DataFrame, col: str) -> float:
        raise NotImplementedError("This method is not supported")

    @staticmethod
    def calc_list_metric(data: pd.DataFrame, col: str) -> List[float]:
        raise NotImplementedError("This method is not supported")

    @staticmethod
    def calc_matrix_metric(data: pd.DataFrame, col: str) -> List[List[float]]:
        raise NotImplementedError("This method is not supported")

    @staticmethod
    def compare(data1: pd.DataFrame, data2: pd.DataFrame, col: str) -> float:
        assert data1.shape[0] == data2.shape[0]

        dists = [
            L2Metric.calc_dist(x, y) for x, y in zip(data1[col], data2[col])
        ]

        return sum(dists)

    @staticmethod
    def calc_dist(x: float, y: float) -> float:
        return abs(x - y) ** 2


class SpectrumMetric(Metric):
    @staticmethod
    def calc_metric(data: pd.DataFrame, col: str) -> float:
        raise NotImplementedError("This method is not supported")

    @staticmethod
    def calc_list_metric(data: pd.DataFrame, col: str) -> List[float]:
        raise NotImplementedError("This method is not supported")

    @staticmethod
    def calc_matrix_metric(data: pd.DataFrame, col: str) -> List[List[float]]:
        Fs = 1 / (5 * 60)
        NFFT = min(data.shape[0], 72)
        noverlap = round(NFFT / 2)

        spectrum, _, _ = specgram(
            data[col], Fs=Fs, NFFT=NFFT, noverlap=noverlap
        )

        spectrum_matrix: List[List[float]] = spectrum.tolist()

        return spectrum_matrix

    @staticmethod
    def compare(data1: pd.DataFrame, data2: pd.DataFrame, col: str) -> float:
        assert data1.shape[0] == data2.shape[0]

        spectrum1 = SpectrumMetric.calc_matrix_metric(data1, col)
        spectrum2 = SpectrumMetric.calc_matrix_metric(data2, col)

        dist = SpectrumMetric.calc_dist(spectrum1, spectrum2)
        return dist

    @staticmethod
    def calc_dist(xm: List[List[float]], ym: List[List[float]]) -> float:
        total = 0.0
        for xl, yl in zip(xm, ym):
            for x, y in zip(xl, yl):
                total = total + abs(x - y) ** 2

        return total
