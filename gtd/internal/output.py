from typing import Dict, Iterator, List

from pydantic import BaseModel

from gtd.internal.partial_output import PartialOutput


class Output(BaseModel):
    parts: Dict[str, PartialOutput] = {}

    def __str__(self) -> str:
        part_names = self.get_part_names()
        return f"Output(parts={part_names})"

    def get_part_by_name(self, part: str) -> PartialOutput:
        return self.parts[part]

    def get_parts(self) -> Iterator[PartialOutput]:
        for part in self.parts.values():
            yield part

    def get_part_names(self) -> List[str]:
        return [name for name in self.parts.keys()]
