__all__ = (
    'event', 'event_freq', 'run', 'install',
    'run_in_thread', 'run_in_executor',
)
import types
from functools import lru_cache, partial
import typing as T

from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import tkinter

from asyncgui import _current_task, _sleep_forever, Cancelled
from asyncgui_ext.clock import Clock


def _event_callback(task_step, filter, e: tkinter.Event):
    if filter is None or filter(e):
        task_step(e)


@types.coroutine
def event(widget, sequence, *, filter=None) -> T.Awaitable[tkinter.Event]:
    task = (yield _current_task)[0][0]
    bind_id = widget.bind(
        sequence,
        partial(_event_callback, task._step, filter),
        '+',
    )
    try:
        return (yield _sleep_forever)[0][0]
    finally:
        widget.unbind(sequence, bind_id)


class event_freq:
    '''
    When handling a frequently occurring event, such as ``<Motion>``, the following code might cause performance
    issues:

    .. code-block::

        e = await event(widget, '<ButtonPress>')
        while True:
            e = await event(widget, '<Motion>')
            ...

    If that happens, try the following code instead. It might resolve the issue:

    .. code-block::

        e = await event(widget, '<ButtonPress>')
        async with event_freq(widget, '<Motion>') as mouse_motion:
            while True:
                e = await mouse_motion()
                ...

    The trade-off is that within the context manager, you can't perform any async operations except the
    ``await mouse_motion()``.

    .. code-block::

        async with event_freq(...) as xxx:
            e = await xxx()  # OK
            await something_else()  # Don't

    .. versionadded:: 0.4.2
    '''
    __slots__ = ('_widget', '_seq', '_filter', '_bind_id', )

    def __init__(self, widget, sequence, *, filter=None):
        self._widget = widget
        self._seq = sequence
        self._filter = filter

    @types.coroutine
    def __aenter__(self):
        task = (yield _current_task)[0][0]
        self._bind_id = self._widget.bind(
            self._seq,
            partial(_event_callback, task._step, self._filter),
            "+",
        )
        return self._wait_one

    async def __aexit__(self, *args):
        self._widget.unbind(self._seq, self._bind_id)

    @staticmethod
    @types.coroutine
    def _wait_one():
        return (yield _sleep_forever)[0][0]


@lru_cache(maxsize=1)
def install():
    def immediate_call(f):
        f()

    @immediate_call
    def patch_unbind():
        '''
        The reason we need to patch 'Misc.unbind()'.
        https://stackoverflow.com/questions/6433369/deleting-and-changing-a-tkinter-event-binding
        '''
        def _new_unbind(self, sequence, funcid=None):
            if not funcid:
                self.tk.call('bind', self._w, sequence, '')
                return
            func_callbacks = self.tk.call('bind', self._w, sequence, None).split('\n')
            new_callbacks = [l for l in func_callbacks if l[6:6 + len(funcid)] != funcid]
            self.tk.call('bind', self._w, sequence, '\n'.join(new_callbacks))
            self.deletecommand(funcid)

        tkinter.Misc.unbind = _new_unbind


def run(async_fn, *, fps=20, root: tkinter.Tk=None):
    from time import sleep, perf_counter as get_time
    from tkinter import TclError
    import asyncgui
    from asyncgui_ext.clock import Clock

    install()
    max_ = max
    root = tkinter.Tk() if root is None else root
    clock = Clock()

    # `run_in_thread` and `run_in_executer` used to be methods of Clock class until `asyncgui-ext-clock``
    # version 0.5 but they no longer are. In order not to break existing code, we need to recreate them.
    clock.run_in_thread = partial(run_in_thread, clock)
    clock.run_in_executer = partial(run_in_executor, clock)

    root_task = asyncgui.start(async_fn(clock=clock, root=root))
    root.protocol("WM_DELETE_WINDOW", lambda: (root_task.cancel(), root.destroy()))

    clock_tick = clock.tick
    root_update = root.update
    update_interval = 1.0 / fps
    min_sleep_time = 1.0 / 60.0

    last_time = get_time()
    while True:
        try:
            root_update()
        except TclError:
            break

        cur_time = get_time()
        delta_time = cur_time - last_time
        last_time = cur_time
        sleep_time = max_(min_sleep_time, update_interval - delta_time)
        clock_tick(delta_time)
        sleep(sleep_time)
        # print(f"{last_time = }, {cur_time = }, {delta_time = }, {sleep_time = }")

    root_task.cancel()


async def run_in_thread(clock: Clock, func, *, daemon=None, polling_interval=1.0):
    '''
    Creates a new thread, runs a function within it, then waits for the completion of that function.

    .. code-block::

        return_value = await run_in_thread(clock, func)

    .. warning::
        When the caller Task is cancelled, the ``func`` will be left running, which violates "structured concurrency".
    '''
    return_value = None
    exception = None
    done = False

    def wrapper():
        nonlocal return_value, done, exception
        try:
            return_value = func()
        except Exception as e:
            exception = e
        finally:
            done = True

    Thread(target=wrapper, daemon=daemon, name="asynctkinter.run_in_thread").start()
    async with clock.sleep_freq(polling_interval) as sleep:
        while not done:
            await sleep()
    if exception is not None:
        raise exception
    return return_value


async def run_in_executor(clock: Clock, executer: ThreadPoolExecutor, func, *, polling_interval=1.0):
    '''
    Runs a function within a :class:`concurrent.futures.ThreadPoolExecutor`, and waits for the completion of the
    function.

    .. code-block::

        executor = ThreadPoolExecutor()
        ...
        return_value = await run_in_executor(clock, executor, func)


    .. warning::
        When the caller Task is cancelled, the ``func`` will be left running if it has already started,
        which violates "structured concurrency".
    '''
    return_value = None
    exception = None
    done = False

    def wrapper():
        nonlocal return_value, done, exception
        try:
            return_value = func()
        except Exception as e:
            exception = e
        finally:
            done = True

    future = executer.submit(wrapper)
    try:
        async with clock.sleep_freq(polling_interval) as sleep:
            while not done:
                await sleep()
    except Cancelled:
        future.cancel()
        raise
    if exception is not None:
        raise exception
    return return_value
