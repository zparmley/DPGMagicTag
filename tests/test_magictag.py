from dpgmagictag.magictag import MagicTag


def test_is_str():
    assert isinstance(MagicTag(), str)


def test_eq():
    assert MagicTag('abc') == MagicTag('abc')
    assert MagicTag('abc') != MagicTag('def')


def test_composable():
    assert (MagicTag('a') / 'b') == MagicTag('a/b')
    assert ('a' / MagicTag('b')) == MagicTag('a/b')


def test_query_relative():
    root_1 = MagicTag.random_factory()
    root_2 = MagicTag.random_factory()

    a_1_1 = root_1 / 'a/1'
    a_1_2 = root_2 / 'a/1'

    results = root_1.query('*/a/1')
    assert a_1_1 in results
    assert a_1_2 not in results

def test_query_nonrelative():
    root_1 = MagicTag.random_factory()
    root_2 = MagicTag.random_factory()

    a_1_1 = root_1 / 'a/1'
    a_1_2 = root_2 / 'a/1'

    results = root_1.query('*/a/1', relative=False)
    assert a_1_1 in results
    assert a_1_2 in results
