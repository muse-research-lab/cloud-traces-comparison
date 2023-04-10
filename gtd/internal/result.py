from typing import Dict, Iterator, List

from pydantic.generics import Generic, GenericModel

from gtd.internal.partial_result import PartialResult
from gtd.internal.types import Id


class Result(GenericModel, Generic[Id]):
    baseline: Id
    compared: Dict[Id, PartialResult]

    def __str__(self) -> str:
        compared_ids = self.get_partial_result_ids()
        return f"Result(baseline={self.baseline}, compared={compared_ids})"

    def get_partial_result_by_id(self, id: Id) -> PartialResult:
        return self.compared[id]

    def get_partial_results(self) -> Iterator[PartialResult]:
        for partial_result in self.compared.values():
            yield partial_result

    def get_partial_result_ids(self) -> List[Id]:
        return [id for id in self.compared.keys()]
