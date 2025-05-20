import re

from dpgmagictag.magictag import MagicTag


def test_match():
    tag = MagicTag('a/b/c')
    path = tag.path
    assert path.match('a/b/c')
    assert path.match('a/*')
    assert path.match('*/b/c')
    assert path.match('a/*/c')
    assert path.match('a/*/*')

def test_nomatch():
    tag = MagicTag('a/b/c')
    path = tag.path
    assert not path.match('a/b/c/d')
    assert not path.match('a/b/c/*')
    assert not path.match('*/a/b/c')
    assert not path.match('*/b/d')

def test_match_regex():
    tag = MagicTag('a/b/c')
    path = tag.path
    pattern = re.compile(r'a.b.c')
    assert path.match(pattern)
