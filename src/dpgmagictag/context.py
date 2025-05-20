import collections
import dataclasses
import functools
import typing

from dpgmagictag.path import Constants
from dpgmagictag.path import Path


@dataclasses.dataclass
class Context:
    root: str = 'DEFAULT_ROOT'
    existing: set[Path] = dataclasses.field(default_factory=set)

    @classmethod
    @functools.cache
    def default_context(cls) -> typing.Self:
        return cls()

    # def query(self, pattern: str) -> tuple[typing.ForwardRef('MagicTag'), ...]:
    #     print(pattern_parts)
