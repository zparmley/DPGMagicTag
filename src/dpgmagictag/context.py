import collections
import dataclasses
import functools
import typing

from dpgmagictag.path import Constants


@dataclasses.dataclass
class Context:
    root: str = 'DEFAULT_ROOT'
    created: list[str] = dataclasses.field(default_factory=list)  # Eventually move this to a debugging context
    deleted: list[str] = dataclasses.field(default_factory=list)  # Eventually move this to a debugging context
    existing: set[str] = dataclasses.field(default_factory=set)
    member_counts: dict[str, int] = dataclasses.field(
        default_factory=functools.partial(collections.defaultdict, int)
    )

    @classmethod
    @functools.cache
    def default_context(cls) -> typing.Self:
        return cls()

    def query(self, pattern: str) -> tuple[typing.ForwardRef('MagicTag'), ...]:
        pattern_parts = pattern.split(Constants.SEP)
        print(pattern_parts)
