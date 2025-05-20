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
    with dpg.button(tag = base_tag + 'left_button')
    ...
```
