from dpgmagictag.magictag import MagicTag


def test_is_str():
    assert isinstance(MagicTag(), str)


def test_eq():
    assert MagicTag('abc') == MagicTag('abc')
    assert MagicTag('abc') != MagicTag('def')


def test_composable():
    assert (MagicTag('a') / 'b') == MagicTag('a/b')
    assert ('a' / MagicTag('b')) == MagicTag('a/b')
