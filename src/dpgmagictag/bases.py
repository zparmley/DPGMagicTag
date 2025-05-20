import fnmatch
import functools
import re


@functools.cache
def _is_case_sensitive(parser):
    """Courtesy of https://github.com/python/cpython/blob/3.13/Lib/pathlib/_abc.py#L44
    """
    return parser.normcase('Aa') == 'Aa'


class UnsupportedOperation(NotImplementedError):
    """Courtesy of https://github.com/python/cpython/blob/3.13/Lib/pathlib/_abc.py#L48

    An exception that is raised when an unsupported operation is called on
    a path object.
    """
    pass


class ParserBase:
    """Based on ParserBase from cpython3.13
    Source: https://github.com/python/cpython/blob/3.13/Lib/pathlib/_abc.py#L55

    Base class for path parsers, which do low-level path manipulation.

    Path parsers provide a subset of the os.path API, specifically those
    functions needed to provide PurePathBase functionality. Each PurePathBase
    subclass references its path parser via a 'parser' class attribute.

    Every method in this base class raises an UnsupportedOperation exception.
    """

    @classmethod
    def _unsupported_msg(cls, attribute):
        return f"{cls.__name__}.{attribute} is unsupported"

    @property
    def sep(self):
        """The character used to separate path components."""
        raise UnsupportedOperation(self._unsupported_msg('sep'))

    def join(self, path, *paths):
        """Join path segments."""
        raise UnsupportedOperation(self._unsupported_msg('join()'))

    def split(self, path):
        """Split the path into a pair (head, tail), where *head* is everything
        before the final path separator, and *tail* is everything after.
        Either part may be empty.
        """
        raise UnsupportedOperation(self._unsupported_msg('split()'))

    def splitdrive(self, path):
        """Split the path into a 2-item tuple (drive, tail), where *drive* is
        a device name or mount point, and *tail* is everything after the
        drive. Either part may be empty."""
        raise UnsupportedOperation(self._unsupported_msg('splitdrive()'))

    def normcase(self, path):
        """Normalize the case of the path."""
        raise UnsupportedOperation(self._unsupported_msg('normcase()'))

    def isabs(self, path):
        """Returns whether the path is absolute, i.e. unaffected by the
        current directory or drive."""
        raise UnsupportedOperation(self._unsupported_msg('isabs()'))


class PathBase:
    """Based on PurePathBase from cpython3.13 but heavily modified
    original: https://github.com/python/cpython/blob/3.13/Lib/pathlib/_abc.py#L101

    Base class for MagicTagPath objects.
    """

    __slots__ = (
        # The `_raw_path` slot store a joined string path. This is set in the
        # `__init__()` method.
        '_raw_path',

        # The '_resolving' slot stores a boolean indicating whether the path
        # is being processed by `PathBase.resolve()`. This prevents duplicate
        # work from occurring when `resolve()` calls `stat()` or `readlink()`.
        '_resolving',
    )
    parser = ParserBase()

    def __init__(self, *paths: str):
        self._raw_path = self.parser.join(*paths)
        self._resolving = False

    def with_segments(self, *pathsegments: str):
        """Construct a new path object from any number of path segment strs.
        """
        return type(self)(*pathsegments)

    def __str__(self):
        """Return the string representation of the path."""
        return self._raw_path

    @property
    def name(self):
        """The final path component, if any."""
        return self.parser.split(self._raw_path)[1]

    @property
    def member_index(self) -> int | None:
        '''The member # of this path, if any.'''
        if not self._raw_path.endswith(']'):
            return None
        _, index = self._raw_path.rsplit('[', maxsplit=1)
        return int(index[:-1])

    @property
    def stem(self):
        """The final path component"""
        name = self.name
        if name.endswith(']'):
            name, _ = name.rsplit('[', maxsplit=1)
        return name

    def with_name(self, name: str):
        """Return a new path with the name changed."""
        split = self.parser.split
        if split(name)[0]:
            raise ValueError(f"Invalid name {name!r}")
        return self.with_segments(split(self._raw_path)[0], name)

    def with_member_index(self, index: int):
        """Return a new path with the file suffix changed.  If the path
        has no suffix, add given suffix.  If the given suffix is an empty
        string, remove the suffix from the path.
        """
        stem = self.stem
        if not stem:
            # If the stem is empty, we can't make the member index non-empty.
            raise ValueError(f"{self!r} has an empty name")
        else:
            return self.with_name(stem + f'[{index}]')

    def relative_to(self, other, *, walk_up=False):
        """Return the relative path to another path identified by the passed
        arguments.  If the operation is not possible (because this is not
        related to the other path), raise ValueError.

        The *walk_up* parameter controls whether `..` may be used to resolve
        the path.
        """
        if not isinstance(other, PathBase):
            other = self.with_segments(other)
        anchor0, parts0 = self._stack
        anchor1, parts1 = other._stack
        if anchor0 != anchor1:
            raise ValueError(f"{self._raw_path!r} and {other._raw_path!r} have different anchors")
        while parts0 and parts1 and parts0[-1] == parts1[-1]:
            parts0.pop()
            parts1.pop()
        for part in parts1:
            if not part or part == '.':
                pass
            elif not walk_up:
                raise ValueError(f"{self._raw_path!r} is not in the subpath of {other._raw_path!r}")
            elif part == '..':
                raise ValueError(f"'..' segment in {other._raw_path!r} cannot be walked")
            else:
                parts0.append('..')
        return self.with_segments('', *reversed(parts0))

    def is_relative_to(self, other):
        """Return True if the path is relative to another path or False.
        """
        if not isinstance(other, PathBase):
            other = self.with_segments(other)
        anchor0, parts0 = self._stack
        anchor1, parts1 = other._stack
        if anchor0 != anchor1:
            return False
        while parts0 and parts1 and parts0[-1] == parts1[-1]:
            parts0.pop()
            parts1.pop()
        for part in parts1:
            if part and part != '.':
                return False
        return True

    @property
    def parts(self):
        """An object providing sequence-like access to the
        components in the filesystem path."""
        anchor, parts = self._stack
        if anchor:
            parts.append(anchor)
        return tuple(reversed(parts))

    def joinpath(self, *pathsegments):
        """Combine this path with one or several arguments, and return a
        new path representing either a subpath (if all arguments are relative
        paths) or a totally different path (if one of the arguments is
        anchored).
        """
        return self.with_segments(self._raw_path, *pathsegments)

    def __truediv__(self, key):
        try:
            return self.with_segments(self._raw_path, key)
        except TypeError:
            return NotImplemented

    def __rtruediv__(self, key):
        try:
            return self.with_segments(key, self._raw_path)
        except TypeError:
            return NotImplemented

    @property
    def _stack(self):
        """
        Split the path into a 2-tuple (anchor, parts), where *anchor* is the
        uppermost parent of the path (equivalent to path.parents[-1]), and
        *parts* is a reversed list of parts following the anchor.
        """
        split = self.parser.split
        path = self._raw_path
        parent, name = split(path)
        names = []
        while path != parent:
            names.append(name)
            path = parent
            parent, name = split(path)
        return path, names

    @property
    def parent(self):
        """The logical parent of the path."""
        path = self._raw_path
        parent = self.parser.split(path)[0]
        if path != parent:
            parent = self.with_segments(parent)
            parent._resolving = self._resolving
            return parent
        return self

    @property
    def parents(self):
        """A sequence of this path's logical parents."""
        split = self.parser.split
        path = self._raw_path
        parent = split(path)[0]
        parents = []
        while path != parent:
            parents.append(self.with_segments(parent))
            path = parent
            parent = split(path)[0]
        return tuple(parents)

    def match(self, path_pattern: str | re.Pattern) -> bool:
        """
        Return True if this path matches the given pattern. if path_pattern is
        a str, it is matching is done via the fnmatch.fnmatchcase.  See the
        fnmatch module for matching rules.  If path_pattern is a compiled regex
        (via re.compile) the path is simply tested with .match(path)
        """
        if isinstance(path_pattern, re.Pattern):
            return path_pattern.match(self._raw_path) is not None
        return fnmatch.fnmatchcase(self._raw_path, path_pattern)
