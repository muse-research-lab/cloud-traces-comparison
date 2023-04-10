import math
from typing import List

import numpy as np
import pandas as pd
from fastdtw import fastdtw
from skimage.metrics import structural_similarity


def l1(data1: pd.Series, data2: pd.Series) -> float:
    dist: float = sum([abs(x - y) for x, y in zip(data1, data2)])

    return dist


def l1_img(data1: np.ndarray, data2: np.ndarray) -> float:
    diff = np.subtract(data1, data2)
    acc_dist: float = np.sum(np.abs(diff))

    return acc_dist


def l2(data1: pd.Series, data2: pd.Series) -> float:
    dist = sum([abs(x - y) ** 2 for x, y in zip(data1, data2)])

    return math.sqrt(dist)


def l2_img(data1: np.ndarray, data2: np.ndarray) -> float:
    diff = np.subtract(data1, data2)
    acc_dist: float = np.sum(diff**2)

    return math.sqrt(acc_dist)


def mae(data1: pd.Series, data2: pd.Series) -> float:
    dist: float = l1(data1, data2) / data1.shape[0]

    return dist


def mae_img(data1: np.ndarray, data2: np.ndarray) -> float:
    h, w = data1.shape

    return l1_img(data1, data2) / (float(h * w))


def mse(data1: pd.Series, data2: pd.Series) -> float:
    dists = [abs(x - y) ** 2 for x, y in zip(data1, data2)]
    dist: float = sum(dists) / len(dists)

    return dist


def mse_img(data1: np.ndarray, data2: np.ndarray) -> float:
    h, w = data1.shape
    diff = np.subtract(data1, data2)
    acc_dist: float = np.sum(diff**2)

    return acc_dist / (float(h * w))


def mape_img(data1: np.ndarray, data2: np.ndarray) -> float:
    dist: float = (
        np.mean(
            np.abs(
                np.divide(
                    (data1 - data2),
                    data1,
                    out=np.zeros_like(data1 - data2),
                    where=data1 != 0,
                )
            )
        )
        * 100
    )

    return dist


def mape(data1: pd.Series, data2: pd.Series) -> float:
    data1_tmp = data1.to_numpy(copy=True)
    data2_tmp = data2.to_numpy(copy=True)

    return mape_img(data1_tmp, data2_tmp)


def ssim_img(data1: np.ndarray, data2: np.ndarray) -> float:
    mssim = structural_similarity(data1, data2)

    return float(mssim)


def ssim(data1: pd.Series, data2: pd.Series) -> float:
    data1_tmp = data1.to_numpy(copy=True)
    data2_tmp = data2.to_numpy(copy=True)

    return ssim_img(data1_tmp, data2_tmp)


def sdsim_img(data1: np.ndarray, data2: np.ndarray) -> float:
    return 1 - ssim_img(data1, data2)


def sdsim(data1: pd.Series, data2: pd.Series) -> float:
    return 1 - ssim(data1, data2)


def cosine(data1: pd.Series, data2: pd.Series) -> float:
    data1_tmp = data1  # .to_numpy(copy=True)
    data2_tmp = data2  # .to_numpy(copy=True)

    cosine_sim = np.dot(data1_tmp, data2_tmp) / (
        np.linalg.norm(data1_tmp) * np.linalg.norm(data2_tmp)
    )

    return float(1 - cosine_sim)


def iou(data1: np.ndarray, data2: np.ndarray) -> float:
    columns = data2.shape[1]

    IoU: List[float] = []
    for i in range(columns):
        # Get column cells
        column_gt = data1[:, i]
        column_pred = data2[:, i]

        # Get the rows whose value is grey
        rows_gt = [i for i, _ in enumerate(column_gt) if _ == 127]
        rows_pred = [i for i, _ in enumerate(column_pred) if _ == 127]

        # determine the y-coordinates of the intersection rectangle
        yA = max(min(rows_gt), min(rows_pred))
        yB = min(max(rows_gt), max(rows_pred))

        # compute the area of intersection rectangle
        interArea = max((yB - yA), 0)
        if interArea == 0:
            IoU.append(0)
            continue

        # compute the area of both the prediction and ground-truth
        # rectangles
        boxGt = abs(max(rows_gt) - min(rows_gt))
        boxPred = abs(max(rows_pred) - min(rows_pred))

        # compute the intersection over union by taking the intersection
        # area and dividing it by the sum of prediction + ground-truth
        # areas - the intersection area
        iou = interArea / float(boxGt + boxPred - interArea)
        IoU.append(iou)

    # return the intersection over union value
    dist: float = sum(IoU) / len(IoU)
    return dist


def dtwl2(data1: pd.Series, data2: pd.Series) -> float:
    dist: float = 0.0
    dist, _ = fastdtw(data1, data2, dist=2)

    return dist
