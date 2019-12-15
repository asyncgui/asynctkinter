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

def heavy_task():
    import time
    for i in range(5):
        time.sleep(1)
        print('heavy task:', i)

root = Tk()
label = Label(root, text='Hello', font=('', 60))
label.pack()

async def some_task(label):
    label['text'] = 'start heavy task'

    # wait until the label is pressed
    event = await at.event(label, '<Button>')

    print(event.x, event.y)
    label['text'] = 'running...'

    # wait for the completion of another thread
    await at.thread(heavy_task, watcher=label)

    label['text'] = 'done'

    # wait for 2sec
    await at.sleep(label, 2000)

    label['text'] = 'close the window'


at.start(some_task(label))
root.mainloop()
```

```python
async def some_task(label):
    # wait until EITEHR the label is pressed OR 5sec passes
    tasks = await ak.or_(
        ak.event(label, '<Button>'),
        ak.sleep(5),
    )
    print("The label was pressed" if tasks[0].done else "5sec passed")

    # wait until BOTH the label is pressed AND 5sec passes"
    tasks = await ak.and_(
        ak.event(label, '<Button>'),
        ak.sleep(5),
    )
```

## Note

- Why is `patch_unbind()` necessary? Take a look at [this](https://stackoverflow.com/questions/6433369/deleting-and-changing-a-tkinter-event-binding).
