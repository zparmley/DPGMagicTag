# DpgMagicTag

A composable tag system useable with DearPyGUI

## Motivation

[DearPyGUI](https://github.com/hoffstadt/DearPyGui) allows memorable tags for
items but they are required to be strings.  Often, especially when creating
reusable components which might appear more than once in an application, I
found myself using some variation of the following pattern:

```python
base_tag = some_unique_string_generator()
with dpg.window(tag = base_tag + 'window'):
    with dpg.button(tag = base_tag + 'left_button'):
        ...
```

And then later in code having to remember or use a reference to the tag exactly
as I composed it.  With **dpgmagictag** I can compose tags like paths:

```python
base_tag = MagicTag.random_factory()
with dpg.window(tag = base_tag / 'window'):
    with dpg.button(tag = base_tag / 'button'):
        ...
```

Later, to find all buttons, for instance, I can query with i.e.

```python
button_tags = MagicTag().query('*/button')
# or, because querying is relative by default
button_tag = base_tag.query('button')[0]
```

Querying matches with glob-style patterns, so it feels natural once you get
used to composing tags as paths.

All paths, by default, share a context.  Therefore all tags are query-able with
_MagicTag().query(_

## Magic

Why are MagicTags magic?  Because dearpygui treats them as strings, and they
works as strings.  Note, though, that there is a root (from the shared context)
prepended to the string value of each tag.  To see the actual string value as
dearpygui would, use _str()_:

```python
from dpgmagictag.magictag import MagicTag

str(MagicTag('a'))  ## DEFAULT_ROOT/a
```

## n.b.

Note that composing tags like so:

```python
tag = MagicTag() / 'window' / 'header' / 'button1'
```

Creates intermittent tags for _/window_ and _/window/header_
