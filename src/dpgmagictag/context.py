import collections
import dataclasses
import functools
import operator
import typing

from dpgmagictag.path import Path
from dpgmagictag.path import Constants


@dataclasses.dataclass
class Context:
    root: str = 'DEFAULT_ROOT'
    existing: set[Path] = dataclasses.field(default_factory=set)

    @classmethod
    @functools.cache
    def default_context(cls) -> typing.Self:
        return cls()

    def query(self, pattern: str) -> set[Path]:
        filter_func = operator.methodcaller('match', pattern)
        return set(filter(filter_func, self.existing))
