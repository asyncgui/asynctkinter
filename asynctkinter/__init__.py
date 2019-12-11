__version__ = '0.0.1'
__all__ = (
    'patch_unbind', 'start', 'sleep', 'event', 'thread',
    'gather', 'and_', 'or_',
)

import types
import typing
from inspect import getcoroutinestate, CORO_CLOSED


def start(coro):
    def step_coro(*args, **kwargs):
        try:
            if getcoroutinestate(coro) != CORO_CLOSED:
                coro.send((args, kwargs, ))(step_coro)
        except StopIteration:
            pass

    try:
        coro.send(None)(step_coro)
    except StopIteration:
        pass


@types.coroutine
def sleep(widget, duration):
    yield lambda step_coro: widget.after(duration, step_coro)


@types.coroutine
def event(widget, name, *, filter=None):
    bind_id = None
    step_coro = None

    def bind(step_coro_):
        nonlocal bind_id, step_coro
        bind_id = widget.bind(name, callback, '+')
        step_coro = step_coro_

    def callback(*args, **kwargs):
        if (filter is not None) and (not filter(*args, **kwargs)):
            return
        widget.unbind(name, bind_id)
        step_coro(*args, **kwargs)

    return (yield bind)[0][0]


async def thread(func, *, sleep_by):
    from threading import Thread
    return_value = None
    is_finished = False
    def wrapper(*args, **kwargs):
        nonlocal return_value, is_finished
        return_value = func(*args, **kwargs)
        is_finished = True
    Thread(target=wrapper).start()
    while not is_finished:
        await sleep(sleep_by, 3000)
    return return_value


class Task:
    __slots__ = ('coro', 'done', 'result', 'done_callback')
    def __init__(self, coro, *, done_callback=None):
        self.coro = coro
        self.done = False
        self.result = None
        self.done_callback = done_callback
    async def _run(self):
        self.result = await self.coro
        self.done = True
        if self.done_callback is not None:
            self.done_callback()


@types.coroutine
def gather(coros:typing.Iterable[typing.Coroutine], *, n:int=None) -> typing.Sequence[Task]:
    coros = tuple(coros)
    n_coros_left = n if n is not None else len(coros)
    step_coro = None

    def done_callback():
        nonlocal n_coros_left
        n_coros_left -= 1
        if n_coros_left == 0:
            step_coro()
    tasks = tuple(Task(coro, done_callback=done_callback) for coro in coros)
    for task in tasks:
        start(task._run())

    def callback(step_coro_):
        nonlocal step_coro
        step_coro = step_coro_
    yield callback

    return tasks


async def or_(*coros):
    return await gather(coros, n=1)


async def and_(*coros):
    return await gather(coros)


def _new_unbind(self, sequence, funcid=None):
    if not funcid:
        self.tk.call('bind', self._w, sequence, '')
        return
    func_callbacks = self.tk.call('bind', self._w, sequence, None).split('\n')
    new_callbacks = [l for l in func_callbacks if l[6:6 + len(funcid)] != funcid]
    self.tk.call('bind', self._w, sequence, '\n'.join(new_callbacks))
    self.deletecommand(funcid)


def patch_unbind():
    from tkinter import Misc
    Misc.unbind = _new_unbind
