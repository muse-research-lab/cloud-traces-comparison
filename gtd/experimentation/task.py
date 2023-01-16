import pandas as pd


class Task:
    def __init__(self, job_id: int, idx: int, data: pd.DataFrame):
        self._job_id = job_id
        self._idx = idx
        self._data = data

    def __str__(self) -> str:
        return f"Task(job_id={self._job_id}, idx={self._idx})"

    @property
    def job_id(self) -> int:
        return self._job_id

    @property
    def idx(self) -> int:
        return self._idx

    @property
    def data(self) -> pd.DataFrame:
        return self._data

    @data.setter
    def data(self, data: pd.DataFrame) -> None:
        self._data = data

    def get_fraction(
        self, llim: int, ulim: int, copy: bool = True
    ) -> pd.DataFrame:
        return self.data[llim:ulim].copy() if copy else self.data[llim:ulim]

    def convert_ts_col(self, col: str, unit: str) -> None:
        self.data[col] = pd.to_datetime(self.data[col], unit=unit)

    def adjust_freq(self, col: str, freq: str) -> None:
        self.data = self.data.set_index(col)
        self.data = self.data[~self.data.index.duplicated(keep="first")]
        self.data = self.data.asfreq(freq=freq, method="ffill")

    def pad_task(self, lim: int, copy: bool = True) -> pd.DataFrame:
        task_len = self.data.shape[0]

        k, m = divmod(lim, task_len)

        task_data = self.data.copy() if copy else self.data

        for i in range(k - 1):
            new_data = task_data.shift(periods=task_len * (i + 1), freq="5min")[
                :task_len
            ]
            task_data = pd.concat([task_data, new_data])

        if m != 0:
            new_data = task_data.shift(periods=task_len * k, freq="5min")[:m]
            task_data = pd.concat([task_data, new_data])

        return task_data
