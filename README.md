# AsyncTkinter

[Youtube](https://youtu.be/8XP1KgRd3jI)

`asynctkinter` is an async library that saves you from ugly callback-based code,
just like most of async libraries do.
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
```

It's barely readable and not easy to understand.
If you use `asynctkinter`, the code above will become like this:

```python
import asynctkinter as at

async def what_you_want_to_do(label):
    print('A')
    await at.sleep(1000, after=label.after)
    print('B')
    await at.event(label, '<Button>')
    print('C')
```

## Installation

```
pip install asynctkinter
```

## Pin the minor version

If you use this module, it's recommended to pin the minor version, because if
it changed, it usually means some breaking changes occurred.

## Usage

```python
from tkinter import Tk, Label
import asynctkinter as at
at.patch_unbind()

root = Tk()
label = Label(root, text='Hello', font=('', 60))
label.pack()

async def some_task(label):
    label['text'] = 'start heavy task'

    # wait for a label to be pressed
    event = await at.event(label, '<Button>')
    print(f"pos: {event.x}, {event.y}")

    # wait for 2sec
    await at.sleep(2000, after=label.after)

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
at.start(task_A(e))
# A1
at.start(task_B(e))
# B1
e.set()
# A2
# B2
```

### threading

`asynctkinter` doesn't have any I/O primitives like Trio and asyncio do,
thus threads are the only way to perform them without blocking the main-thread:

```python
from concurrent.futures import ThreadPoolExecuter
import asynctkinter as at

executer = ThreadPoolExecuter()

async def some_task(widget):
    # create a new thread, run a function inside it, then
    # wait for the completion of that thread
    r = await at.run_in_thread(
        thread_blocking_operation, after=widget.after)
    print("return value:", r)

    # run a function inside a ThreadPoolExecuter, and wait for the completion
    r = await at.run_in_executer(
        thread_blocking_operation, executer, after=widget.after)
    print("return value:", r)
```

Exceptions(not BaseExceptions) are propagated to the caller,
so you can handle them like you do in synchronous code:

```python
import requests
from requests.exceptions import Timeout
import asynctkinter as at

async def some_task(widget):
    try:
        r = await at.run_in_thread(
            lambda: requests.get('htt...', timeout=10), after=widget.after)
    except Timeout:
        print("TIMEOUT!")
    else:
        print('GOT A RESPONSE')
```

## Structured Concurrency

Both `asynctkinter.and_()` and `asynctkinter.or_()` follow the concept of "structured concurrency".
What does that mean?
They promise two things:

* The tasks passed into them never outlive them.
* Exceptions occured in the tasks are propagated to the caller.

Read [this post][njs_sc] if you are curious to the concept.

## Misc

- Why is `patch_unbind()` necessary? Take a look at [this](https://stackoverflow.com/questions/6433369/deleting-and-changing-a-tkinter-event-binding).

[njs_sc]:https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/