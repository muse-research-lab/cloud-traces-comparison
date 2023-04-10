import math

import numpy as np
from dtw import dtw

from gtd.internal import Input
from gtd.preprocessor.preprocessor import Preprocessor


class RWSCreator(Preprocessor):
    col: str
    sigma: float = 4.46
    R: int = 512
    DMin: int = 1
    DMax: int = 25

    def run(self, input_obj: Input) -> Input:
        sampleX = []

        for i in range(self.R):
            D = np.random.randint(low=self.DMin, high=self.DMax, size=1)

            sampleX.append(np.random.randn(1, int(D)) / self.sigma)

        m = len(input_obj.get_fraction_uuids())
        l1 = max(x.data.shape[0] for x in input_obj.get_fractions())
        n = len(sampleX)

        KMat = np.zeros((m, n))

        for i, fraction in enumerate(input_obj.get_fractions()):
            Ei = np.zeros((1, n))
            data1 = fraction.data["avg_cpu_usage"].to_numpy()

            for j in range(n):
                l2 = len(sampleX[j][0])

                wSize = min(40, math.ceil(max(l1, l2) / 10))
                wSize = max(wSize, abs(l1 - l2))
                # wSize = 0

                data2 = sampleX[j][0]

                dist, _, _, _ = dtw(
                    data1, data2, dist=lambda x, y: np.abs(x - y) ** 2, w=wSize
                )
                Ei[0, j] = dist

            KMat[i] = Ei / math.sqrt(self.R)

            fraction.data = KMat[i]

        return input_obj
