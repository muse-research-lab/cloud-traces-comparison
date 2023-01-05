import io
import math
from abc import ABC, abstractmethod
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.mlab import specgram
from PIL import Image
from skimage.metrics import structural_similarity as ssim


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
    def __str__(self) -> str:
        return "L1 = Sum(|x-y|) / Len()"

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

        return sum(dists) / len(dists)

    @staticmethod
    def calc_dist(x: float, y: float) -> float:
        return abs(x - y)


class L2Metric(Metric):
    def __str__(self) -> str:
        return "L2 = √(Sum(|x-y|^2)) / Len()"

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

        return math.sqrt(sum(dists)) / len(dists)

    @staticmethod
    def calc_dist(x: float, y: float) -> float:
        return abs(x - y) ** 2


class SpectrumMetric(Metric):
    def __str__(self) -> str:
        return "Spectrum = √(Sum(Sum(|a-b|^2)))"

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

        # Normalize by row * column of matrices?
        return math.sqrt(total)


class ImgMetric(Metric):
    @staticmethod
    def calc_metric(data: pd.DataFrame, col: str) -> float:
        raise NotImplementedError("This method is not supported")

    @staticmethod
    def calc_list_metric(data: pd.DataFrame, col: str) -> List[float]:
        raise NotImplementedError("This method is not supported")

    @staticmethod
    def calc_matrix_metric(
        data: pd.DataFrame, col: str, size: int = 100
    ) -> List[List[float]]:
        dpi = 100
        width = data.shape[0] / dpi
        height = (
            1  # alternative: len(task.data["avg_cpu_usage"].unique()) / dpi
        )

        fig = plt.figure(figsize=(width, height), frameon=True)

        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_axis_off()
        ax.set_xmargin(0)
        ax.plot(data.index, data["avg_cpu_usage"], color="k")

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        plt.close()

        buf.seek(0)
        im = Image.open(buf).convert("L")
        im = im.resize((size, size))
        im_array = np.asarray(im)

        image_matrix: List[List[float]] = im_array.tolist()

        return image_matrix

    @staticmethod
    def calc_dist(
        xm: List[List[float]], ym: List[List[float]], metric: str = "mse"
    ) -> float:
        img1 = np.asarray(xm, dtype=np.float32)
        img2 = np.asarray(ym, dtype=np.float32)

        if metric == "mse":
            h, w = img1.shape
            diff = np.subtract(img1, img2)
            err: float = np.sum(diff**2)
            mse = err / (float(h * w))

            return mse
        elif metric == "ssim":
            mssim: float = ssim(img1, img2)

            return mssim
        else:
            return 0.0


class Img100MSEMetric(ImgMetric):
    def __str__(self) -> str:
        return "Img100 MSE = MSE(imgA, imgB), imgA = imgB = 100x100"

    @staticmethod
    def compare(data1: pd.DataFrame, data2: pd.DataFrame, col: str) -> float:
        image1 = ImgMetric.calc_matrix_metric(data1, col, 100)
        image2 = ImgMetric.calc_matrix_metric(data2, col, 100)

        dist = ImgMetric.calc_dist(image1, image2, "mse")
        return dist


class Img64MSEMetric(ImgMetric):
    def __str__(self) -> str:
        return "Img64 MSE = MSE(imgA, imgB), imgA = imgB = 64x64"

    @staticmethod
    def compare(data1: pd.DataFrame, data2: pd.DataFrame, col: str) -> float:
        image1 = ImgMetric.calc_matrix_metric(data1, col, 64)
        image2 = ImgMetric.calc_matrix_metric(data2, col, 64)

        dist = ImgMetric.calc_dist(image1, image2, "mse")
        return dist


class Img128MSEMetric(ImgMetric):
    def __str__(self) -> str:
        return "Img128 MSE = MSE(imgA, imgB), imgA = imgB = 128x128"

    @staticmethod
    def compare(data1: pd.DataFrame, data2: pd.DataFrame, col: str) -> float:
        image1 = ImgMetric.calc_matrix_metric(data1, col, 128)
        image2 = ImgMetric.calc_matrix_metric(data2, col, 128)

        dist = ImgMetric.calc_dist(image1, image2, "mse")
        return dist


class Img100SSIMMetric(ImgMetric):
    def __str__(self) -> str:
        return "Img100 SSIM = SSIM(imgA, imgB), imgA = imgB = 100x100"

    @staticmethod
    def compare(data1: pd.DataFrame, data2: pd.DataFrame, col: str) -> float:
        image1 = ImgMetric.calc_matrix_metric(data1, col, 100)
        image2 = ImgMetric.calc_matrix_metric(data2, col, 100)

        dist = ImgMetric.calc_dist(image1, image2, "ssim")
        return dist


class Img64SSIMMetric(ImgMetric):
    def __str__(self) -> str:
        return "Img64 SSIM = SSIM(imgA, imgB), imgA = imgB = 64x64"

    @staticmethod
    def compare(data1: pd.DataFrame, data2: pd.DataFrame, col: str) -> float:
        image1 = ImgMetric.calc_matrix_metric(data1, col, 64)
        image2 = ImgMetric.calc_matrix_metric(data2, col, 64)

        dist = ImgMetric.calc_dist(image1, image2, "ssim")
        return dist


class Img128SSIMMetric(ImgMetric):
    def __str__(self) -> str:
        return "Img128 SSIM = SSIM(imgA, imgB), imgA = imgB = 128x128"

    @staticmethod
    def compare(data1: pd.DataFrame, data2: pd.DataFrame, col: str) -> float:
        image1 = ImgMetric.calc_matrix_metric(data1, col, 128)
        image2 = ImgMetric.calc_matrix_metric(data2, col, 128)

        dist = ImgMetric.calc_dist(image1, image2, "ssim")
        return dist


class SpectrumImgMetric(Metric):
    @staticmethod
    def calc_metric(data: pd.DataFrame, col: str) -> float:
        raise NotImplementedError("This method is not supported")

    @staticmethod
    def calc_list_metric(data: pd.DataFrame, col: str) -> List[float]:
        raise NotImplementedError("This method is not supported")

    @staticmethod
    def calc_matrix_metric(
        data: pd.DataFrame, col: str, size: int = 100
    ) -> List[List[float]]:
        Fs = 1 / (5 * 60)
        NFFT = min(data.shape[0], 72)
        noverlap = round(NFFT / 2)

        dpi = 100
        width = (data.shape[0] // NFFT) / dpi * 4
        height = (
            1  # alternative: len(task.data["avg_cpu_usage"].unique()) / dpi
        )

        fig = plt.figure(figsize=(width, height), frameon=True)

        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_axis_off()
        ax.set_xmargin(0)

        ax.specgram(
            data["avg_cpu_usage"],
            NFFT=NFFT,
            Fs=Fs,
            noverlap=noverlap,
            cmap="RdYlGn_r",
        )

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        plt.close()

        buf.seek(0)
        im = Image.open(buf).convert("L")
        im = im.resize((size, size))
        im_array = np.asarray(im)

        image_matrix: List[List[float]] = im_array.tolist()

        return image_matrix

    @staticmethod
    def calc_dist(
        xm: List[List[float]], ym: List[List[float]], metric: str = "mse"
    ) -> float:
        img1 = np.asarray(xm, dtype=np.float32)
        img2 = np.asarray(ym, dtype=np.float32)

        if metric == "mse":
            h, w = img1.shape
            diff = np.subtract(img1, img2)
            err: float = np.sum(diff**2)
            mse = err / (float(h * w))

            return mse
        elif metric == "ssim":
            mssim: float = ssim(img1, img2)

            return mssim
        else:
            return 0.0


class SpectrumMSEMetric(SpectrumImgMetric):
    def __str__(self) -> str:
        return "Spectrum MSE = MSE(imgA, imgB), imgA = imgB = 64x64"

    @staticmethod
    def compare(data1: pd.DataFrame, data2: pd.DataFrame, col: str) -> float:
        image1 = SpectrumImgMetric.calc_matrix_metric(data1, col, 64)
        image2 = SpectrumImgMetric.calc_matrix_metric(data2, col, 64)

        dist = SpectrumImgMetric.calc_dist(image1, image2, "mse")
        return dist


class SpectrumSSIMMetric(SpectrumImgMetric):
    def __str__(self) -> str:
        return "Spectrum SSIM = SSIM(imgA, imgB), imgA = imgB = 64x64"

    @staticmethod
    def compare(data1: pd.DataFrame, data2: pd.DataFrame, col: str) -> float:
        image1 = SpectrumImgMetric.calc_matrix_metric(data1, col, 64)
        image2 = SpectrumImgMetric.calc_matrix_metric(data2, col, 64)

        dist = SpectrumImgMetric.calc_dist(image1, image2, "ssim")
        return dist
