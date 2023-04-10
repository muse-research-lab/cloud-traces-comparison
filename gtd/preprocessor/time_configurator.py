import pandas as pd

from gtd.internal import Task
from gtd.preprocessor.preprocessor import TaskPreprocessor


class TimeConfigurator(TaskPreprocessor):
    time_col: str
    time_unit: str
    freq: str

    def _run(self, task: Task) -> None:
        for fraction in task.get_fractions():
            fraction.data = self._convert_ts_col(fraction.data)
            fraction.data = self._adjust_freq(fraction.data)

        return

    def _convert_ts_col(self, data: pd.DataFrame) -> pd.DataFrame:
        data[self.time_col] = pd.to_datetime(
            data[self.time_col], unit=self.time_unit
        )

        return data

    def _adjust_freq(self, data: pd.DataFrame) -> pd.DataFrame:
        data.set_index(self.time_col, inplace=True)
        data = data[~data.index.duplicated(keep="first")]
        data = data.resample(self.freq).mean()
        data = data.fillna(method="ffill")
        data = data.asfreq(freq=self.freq, method="ffill")

        return data
