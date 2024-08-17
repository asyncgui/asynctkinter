# AsyncTkinter

[Youtube](https://youtu.be/8XP1KgRd3jI)

`asynctkinter` is an async library that saves you from ugly callback-style code,
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

It's not easy to understand.
If you use `asynctkinter`, the code above will become:

```python
import asynctkinter as at

async def what_you_want_to_do(clock, label):
    print('A')
    await clock.sleep(1)
    print('B')
    await at.event(label, '<Button>')
    print('C')

nursery.start(what_you_want_to_do(...))
```

## Installation

Pin the minor version.

```text
poetry add asynctkinter@~0.4
pip install "asynctkinter>=0.4,<0.5"
```

## Usage

```python
import tkinter as tk
import asynctkinter as at


async def main(*, clock: at.Clock, root: tk.Tk):
    label = tk.Label(root, text='Hello', font=('', 80))
    label.pack()

    # waits for 2 seconds to elapse
    await clock.sleep(2)

    # waits for a label to be pressed
    event = await at.event(label, '<Button>')
    print(f"pos: {event.x}, {event.y}")

    # waits for either 5 seconds to elapse or a label to be pressed.
    # i.e. waits at most 5 seconds for a label to be pressed
    tasks = await at.wait_any(
        clock.sleep(5),
        at.event(label, '<Button>'),
    )
    if tasks[0].finished:
        print("Timeout")
    else:
        event = tasks[1].result
        print(f"The label got pressed. (pos: {event.x}, {event.y})")

    # same as the above
    async with clock.move_on_after(5) as timeout_tracker:
        event = await at.event(label, '<Button>')
        print(f"The label got pressed. (pos: {event.x}, {event.y})")
    if timeout_tracker.finished:
        print("Timeout")

    # waits for both 5 seconds to elapse and a label to be pressed.
    tasks = await at.wait_all(
        clock.sleep(5),
        at.event(label, '<Button>'),
    )

    # nests as you want.
    tasks = await ak.wait_all(
        at.event(label, '<Button>'),
        at.wait_any(
            clock.sleep(5),
            ...,
        ),
    )
    child_tasks = tasks[1].result


if __name__ == "__main__":
    at.run(main)
```

### threading

Unlike `Trio` and `asyncio`, `asynctkinter` doesn't provide any I/O functionalities,
thus threads may be the best way to perform them without blocking the main thread:

```python
from concurrent.futures import ThreadPoolExecuter
import asynctkinter as at

executer = ThreadPoolExecuter()

async def async_fn(clock: at.Clock):
    # create a new thread, run a function inside it, then
    # wait for the completion of that thread
    r = await clock.run_in_thread(thread_blocking_operation, polling_interval=1.0)
    print("return value:", r)

    # run a function inside a ThreadPoolExecuter, and wait for its completion.
    # (ProcessPoolExecuter is not supported)
    r = await clock.run_in_executer(executer, thread_blocking_operation, polling_interval=0.1)
    print("return value:", r)
```

Exceptions(not BaseExceptions) are propagated to the caller,
so you can catch them like you do in synchronous code:

```python
import requests
import asynctkinter as at

async def async_fn(clock: at.Clock):
    try:
        r = await clock.run_in_thread(lambda: requests.get('htt...', timeout=10), ...)
    except requests.Timeout:
        print("TIMEOUT!")
    else:
        print('RECEIVED:', r)
```


## Notes

- You may want to read the [asyncgui's documentation](https://asyncgui.github.io/asyncgui/) as it is the foundation of this library.
- You may want to read the [asyncgui_ext.clock's documentation](https://asyncgui.github.io/asyncgui-ext-clock/) as well.
- I, the author of this library, am not even a tkinter user so there may be plenty of weird code in the repository.
