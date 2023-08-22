# AsyncTkinter

[Youtube](https://youtu.be/8XP1KgRd3jI)

`asynctkinter` is an async library that saves you from ugly callback-based code,
like most of async libraries do.
Let's say you want to do:

1. `print('A')`
1. wait for 1sec
1. `print('B')`
1. wait for a label to be pressed
1. `print('C')`

in that order.
Your code would look like this:

```python
def what_you_want_to_do(label):
    bind_id = None
    print('A')

    def one_sec_later(__):
        nonlocal bind_id
        print('B')
        bind_id = label.bind('<Button>', on_press, '+')
    label.after(1000, one_sec_later)

    def on_press(event):
        label.unbind('<Button>', bind_id)
        print('C')

what_you_want_to_do(...)
```

It's barely readable and not easy to understand.
If you use `asynctkinter`, the above code will be:

```python
import asynctkinter as at

async def what_you_want_to_do(label):
    print('A')
    await at.sleep(label.after, 1000)
    print('B')
    await at.event(label, '<Button>')
    print('C')

at.start(what_you_want_to_do(...))
```

## Installation

It's recommended to pin the minor version, because if
it changed, it means some *important* breaking changes occurred.

```text
poetry add asynctkinter@~0.3
pip install "asynctkinter>=0.3,<0.4"
```

## Usage

```python
from functools import partial
from tkinter import Tk, Label
import asynctkinter as at
at.install()

root = Tk()
label = Label(root, text='Hello', font=('', 60))
label.pack()

async def async_fn(label):
    sleep = partial(at.sleep, label.after)

    # wait for 2sec
    await sleep(2000)

    # wait for a label to be pressed
    event = await at.event(label, '<Button>')
    print(f"pos: {event.x}, {event.y}")

    # wait until EITHER a label is pressed OR 5sec passes.
    # i.e. wait at most 5 seconds for a label to be pressed.
    tasks = await at.wait_any(
        at.event(label, '<Button>'),
        sleep(5000),
    )
    if tasks[0].finished:
        event = tasks[0].result
        print(f"The label was pressed. (pos: {event.x}, {event.y})")
    else:
        print("5sec passed")

    # wait until a label is pressed AND 5sec passes.
    tasks = await at.wait_all(
        at.event(label, '<Button>'),
        sleep(5000),
    )


at.start(async_fn(label))
root.mainloop()
```

### threading

`asynctkinter` doesn't have any I/O primitives like Trio and asyncio do,
thus threads are the only way to perform them without blocking the main-thread:

```python
from concurrent.futures import ThreadPoolExecuter
import asynctkinter as at

executer = ThreadPoolExecuter()

async def async_fn(widget):
    # create a new thread, run a function inside it, then
    # wait for the completion of that thread
    r = await at.run_in_thread(thread_blocking_operation, after=widget.after)
    print("return value:", r)

    # run a function inside a ThreadPoolExecuter, and wait for its completion.
    # (ProcessPoolExecuter is not supported)
    r = await at.run_in_executer(executer, thread_blocking_operation, after=widget.after)
    print("return value:", r)
```

Exceptions(not BaseExceptions) are propagated to the caller,
so you can catch them like you do in synchronous code:

```python
import requests
import asynctkinter as at

async def async_fn(widget):
    try:
        r = await at.run_in_thread(lambda: requests.get('htt...', timeout=10), after=widget.after)
    except requests.Timeout:
        print("TIMEOUT!")
    else:
        print('RECEIVED:', r)
```


## Note

- You may want to read the [asyncgui's documentation](https://gottadiveintopython.github.io/asyncgui/) as it is the foundation of this library.
