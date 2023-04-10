from typing import Dict, Generic, Iterator, List

from pydantic.generics import GenericModel

from gtd.internal.result import Result
from gtd.internal.types import Id


class PartialOutput(GenericModel, Generic[Id]):
    name: str
    results: Dict[Id, Result]

    def __str__(self) -> str:
        result_ids = self.get_result_ids()
        return f"PartialOutput(name={self.name}, results={result_ids})"

    def get_result_by_id(self, id: Id) -> Result:
        return self.results[id]

    def get_results(self) -> Iterator[Result]:
        for result in self.results.values():
            yield result

    def get_result_ids(self) -> List[Id]:
        return [id for id in self.results.keys()]
