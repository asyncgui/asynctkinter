# AsyncTkinter

Async library that works on top of tkinter's event loop.
([Youtube](https://youtu.be/8XP1KgRd3jI))

### Installation

```
pip install asynctkinter
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

    # wait until a label is pressed
    event = await at.event(label, '<Button>')

    print(event.x, event.y)
    label['text'] = 'running...'

    # create a new thread, run a function on it, then
    # wait for the completion of that thread
    result = await at.run_in_thread(heavy_task, after=label.after)
    print('result of heavytask():', result)

    label['text'] = 'done'

    # wait for 2sec
    await at.sleep(2000, after=label.after)

    label['text'] = 'close the window'


at.start(some_task(label))
root.mainloop()
```

#### wait for the completion/cancellation of multiple tasks simultaneously

```python
async def some_task(label):
    from functools import partial
    import asynctkinter as at
    sleep = partial(at.sleep, after=label.after)
    # wait until EITEHR a label is pressed OR 5sec passes
    tasks = await at.or_(
        at.event(label, '<Button>'),
        sleep(5000),
    )
    print("The label was pressed" if tasks[0].done else "5sec passed")

    # wait until BOTH a label is pressed AND 5sec passes"
    tasks = await at.and_(
        at.event(label, '<Button>'),
        sleep(5000),
    )
```

#### synchronization primitive

There is a Trio's [Event](https://trio.readthedocs.io/en/stable/reference-core.html#trio.Event) equivalent.

```python
import asynctkinter as at

async def task_A(e):
    print('A1')
    await e.wait()
    print('A2')
async def task_B(e):
    print('B1')
    await e.wait()
    print('B2')

e = at.Event()
ak.start(task_A(e))
# A1
ak.start(task_B(e))
# B1
e.set()
# A2
# B2
```

## Note

- Why is `patch_unbind()` necessary? Take a look at [this](https://stackoverflow.com/questions/6433369/deleting-and-changing-a-tkinter-event-binding).
