import typing

from dpgmagictag.bases import ParserBase
from dpgmagictag.bases import PathBase

class Constants:
    SEP: typing.ClassVar[str] = '/'


type PathType = typing.Union[str, 'Path']

def strip_magic_tag_path(path: PathType) -> str:
    if isinstance(path, Path):
        path = str(path)
    while (
            path.startswith(Constants.SEP)
            or path.endswith(Constants.SEP)
    ):
        path = path.strip(Constants.SEP)
    return path


def normalize_magic_tag_path(path: PathType) -> str:
    if isinstance(path, Path):
        path = str(path)

    DOUBLE_SEP = Constants.SEP * 2

    while (DOUBLE_SEP in path):
        path = path.replace(DOUBLE_SEP, Constants.SEP)
    path = strip_magic_tag_path(path)
    return path


def join_magic_tag_paths(*paths: PathType) -> str:
    """Join path segments."""
    to_join = map(strip_magic_tag_path, paths)
    joined = Constants.SEP.join(to_join)
    return normalize_magic_tag_path(joined)


class PathParser(ParserBase):
    @property
    def sep(self) -> str:
        """The character used to separate path components."""
        return Constants.SEP

    def join(self, path: str, *paths: str) -> str:
        """Join path segments."""
        return join_magic_tag_paths(path, *paths)

    def split(self, path: str) -> tuple[str, str]:
        """Split the path into a pair (head, tail), where *head* is everything
        before the final path separator, and *tail* is everything after.
        Either part may be empty.
        """
        if self.sep not in path:
            return ('', path)
        if (path.count(self.sep) == 1) and path.startswith(self.sep):
            return (self.sep, path[1:])
        left, right = path.rsplit(self.sep, 1)
        return (left, right)

    def splitdrive(self, path: str) -> tuple[str, str]:
        """Split the path into a 2-item tuple (drive, tail), where *drive* is
        a device name or mount point, and *tail* is everything after the
        drive. Either part may be empty."""
        return ('', path)

    def normcase(self, path) -> str:
        """Normalize the case of the path."""
        return path

    def isabs(self, path) -> bool:
        """Returns whether the path is absolute, i.e. unaffected by the
        current directory or drive."""
        return path.startswith(self.sep)


class Path(PathBase):
    parser = PathParser()

    def __init__(self, *paths, **kwargs):
        path = join_magic_tag_paths(*paths)
        super().__init__(path, **kwargs)

    def __repr__(self):
        return f"{type(self).__name__}('{str(self)}')"

    def __hash__(self):
        return hash((hash(self.__class__), str(self)))

    def __eq__(self, other):
        if isinstance(other, Path):
            return hash(self) == hash(other)
        return False
