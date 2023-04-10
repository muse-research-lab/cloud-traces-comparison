from typing import List, Tuple, TypeVar

Id = TypeVar("Id", int, Tuple[int, int], Tuple[int, int, int])

DataT = TypeVar("DataT")

ValueT = TypeVar("ValueT", float, int, List[float], List[int])
