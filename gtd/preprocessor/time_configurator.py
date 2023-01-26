import pandas as pd

from gtd.internal import Task
from gtd.preprocessor.preprocessor import TaskPreprocessor


class TimeConfigurator(TaskPreprocessor):
    time_col: str
    time_unit: str
    freq: str

    def _run(self, task: Task) -> None:
        for fraction in task.get_fractions():
            self._convert_ts_col(fraction.data)
            self._adjust_freq(fraction.data)

        return

    def _convert_ts_col(self, data: pd.DataFrame) -> None:
        data[self.time_col] = pd.to_datetime(
            data[self.time_col], unit=self.time_unit
        )

        return

    def _adjust_freq(self, data: pd.DataFrame) -> None:
        data.set_index(self.time_col, inplace=True)
        data = data[~data.index.duplicated(keep="first")]
        data = data.asfreq(freq=self.freq, method="ffill")

        return
