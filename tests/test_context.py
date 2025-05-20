from dpgmagictag.context import Context
from dpgmagictag.magictag import MagicTag


def test_query():
    context = Context('TestContext1')

    root_1 = MagicTag('root_1', context=context)
    root_2 = MagicTag('root_2', context=context)

    a_1_1 = root_1 / 'a/1'
    a_1_2 = root_2 / 'a/1'

    results = context.query('*/a/1')
    assert a_1_1.path in results
    assert a_1_2.path in results
