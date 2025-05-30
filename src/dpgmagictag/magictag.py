import dataclasses
import operator
import random
import string
import typing

from dpgmagictag.context import Context
from dpgmagictag.path import Path


@dataclasses.dataclass
class MagicTag(str):
    path_str: dataclasses.InitVar[str] = ''
    context: Context = dataclasses.field(
        default_factory=Context.default_context,
        kw_only=True,
    )
    path: Path = dataclasses.field(
        default_factory=Path,
        kw_only=True,
    )

    def __new__(cls, path_str: str = '', **kwargs):
        if 'path' in kwargs:
            path = kwargs['path'] / path_str
        else:
            default_factory = cls.__dataclass_fields__['path'].default_factory
            path = default_factory() / path_str  # type: ignore
        if 'context' in kwargs:
            root = kwargs['context'].root
        else:
            default_factory = cls.__dataclass_fields__['context'].default_factory
            root = default_factory().root  # type: ignore
        full_path_str = cls._str(root, path)

        return super(MagicTag, cls).__new__(cls, full_path_str)

    def __post_init__(self, path_str: str):
        self.path = self.path / path_str
        self._path_created()

    def _path_created(self, path: Path | None = None):
        if path is None:
            path = self.path
        self.context.existing.add(path)

    def __truediv__(self, part: str | typing.Self | Path):
        if isinstance(part, MagicTag):
            part = part.path
        elif isinstance(part, str):
            part = Path(part)
        return type(self)(
            context=self.context,
            path=self.path / part,
        )

    def __rtruediv__(self, part: str | typing.Self | Path):
        if isinstance(part, MagicTag):
            part = part.path
        elif isinstance(part, str):
            part = Path(part)
        return type(self)(
            context=self.context,
            path=part / self.path,
        )

    def __repr__(self):
        return f'{type(self).__name__}(path={repr(self.path)}, context={repr(self.context)})'

    @classmethod
    def _str(cls, root: str, path: Path) -> str:
        return str(root / path)

    def __str__(self):
        return self._str(self.context.root, self.path)

    def __hash__(self):
        return hash(str(self))

    def query(self, pattern: str, relative: bool=True):
        paths: set[Path] | filter[Path] = self.context.query(pattern)
        if relative:
            # paths = filter(operator.methodcaller('is_relative_to', self.path), paths)
            paths = filter(lambda path: path.is_relative_to(self.path), paths)
        return set(MagicTag(path=path, context=self.context) for path in paths)

    @classmethod
    def random_factory(cls):
        return cls(''.join(random.choices(string.ascii_letters, k=8)))
