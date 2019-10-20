# AsyncTkinter

Allows you to use async/await syntax inside a Tkinter application. ([Youtube](https://youtu.be/8XP1KgRd3jI))

## Installation

```
pip install git+https://github.com/gottadiveintopython/asynctkinter#egg=asynctkinter
```

## Usage

```python
from tkinter import Tk, Label
import asynctkinter as at

at.patch_unbind()

root = Tk()
label = Label(root, font=('', 40))
label.pack()

async def async_func(label):
    while True:
        label['text'] = 'Click anywhere!'
        event = await at.event(label, '<Button>')
        label['text'] = f'You clicked at ({event.x}, {event.y})'
        await at.sleep(label, 1500)

at.start(async_func(label))
root.mainloop()

```

## Note

- Why `patch_unbind()` is needed? See [this](https://stackoverflow.com/questions/6433369/deleting-and-changing-a-tkinter-event-binding).
