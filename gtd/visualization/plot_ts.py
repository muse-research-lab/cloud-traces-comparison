from typing import List, Tuple, Union

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from gtd.visualization.common import set_color_scheme


def sort_ts(df: pd.DataFrame, columns: Union[str, List[str]]) -> pd.DataFrame:
    return df.sort_values(columns, ignore_index=True)


def reset_time(
    col: pd.core.series.Series, to_type: str = "h"
) -> pd.core.series.Series:
    if to_type == "h":
        divider = 1000 * 1000 * 60 * 60
    elif to_type == "min":
        divider = 1000 * 1000 * 60
    elif to_type == "s":
        divider = 1000 * 1000
    else:
        raise ValueError("Choose one of the following valid types: h, min, s")

    return col / divider - (col.iloc[0] / divider)


def get_split_col_intervals(
    col: pd.core.series.Series, start: int, end: int, step: int
) -> List[Tuple[int, Union[None, int]]]:
    n = end - start
    k, m = divmod(n, step)

    if k == 0:
        return [(0, None)]

    step_start = start
    lims = [step_start]
    for idx, time in col.items():
        if time - step_start > step:
            lims.append(idx)
            step_start = time

    if m >= step / 2:
        k = k + 1
        intervals_len = len(lims)
    else:
        intervals_len = len(lims) - 1

    intervals: List[Tuple[int, Union[None, int]]] = []
    for i in range(intervals_len):
        if i == k - 1:
            intervals.append((lims[i], None))
        else:
            intervals.append((lims[i], lims[i + 1]))

    return intervals


def create_fig(
    x: pd.core.series.Series,
    y_list: List[pd.core.series.Series],
    labels: List[str],
    title: str,
    xtitle: str,
    ytitle: str,
    lylim: float,
    uylim: float,
) -> Figure:
    set_color_scheme()
    fig, ax = plt.subplots(figsize=(24, 4))

    for y, label in zip(y_list, labels):
        ax.plot(x, y, label=label)

    ax.set_ylim(lylim, uylim)

    ax.set_xlabel(xtitle)
    ax.set_ylabel(ytitle)

    ax.set_title(title)
    ax.legend()

    return fig


def save_fig(fig: Figure, path: str, dpi: int = 600) -> None:
    fig.savefig(path, dpi=dpi)
