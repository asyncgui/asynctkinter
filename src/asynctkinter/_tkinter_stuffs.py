__all__ = (
    'event', 'event_freq', 'run', 'install',
    'run_in_thread', 'run_in_executor',
)
from functools import lru_cache, partial
from collections.abc import Awaitable

from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import tkinter

from asyncgui import Cancelled, ExclusiveEvent
from asyncgui_ext.clock import Clock


def _event_callback(callback, filter, e: tkinter.Event):
    if filter is None or filter(e):
        callback(e)


async def event(widget, event_name, *, filter=None) -> Awaitable[tkinter.Event]:
    '''
    .. code-block::

        e = await event(widget, "<ButtonPress>")
        print(f"{e.x = }, {e.y = }")
    '''
    ee = ExclusiveEvent()
    bind_id = widget.bind(event_name, partial(_event_callback, ee.fire, filter), "+")
    try:
        return await ee.wait_args_0()
    finally:
        widget.unbind(event_name, bind_id)


class event_freq:
    '''
    When handling a frequently occurring event, such as ``<Motion>``, the following kind of code
    may cause performance issues:

    .. code-block::

        while True:
            e = await event(widget, "<Motion>")
            ...

    If that happens, try the following code instead. It may resolve the issue:

    .. code-block::

        with event_freq(widget, "<Motion>") as mouse_motion:
            while True:
                e = await mouse_motion()
                ...

    When listening for a ``<Motion>`` event, you will often also want to listen for a ``<ButtonRelease>`` event,
    which leads to deeply nested code:

    .. code-block::

        async with move_on_when(event(widget, "<ButtonRelease>", filter=...)):
            with event_freq(widget, "<Motion>") as mouse_motion:
                while True:
                    e = await mouse_motion()
                    ...

    To mitigate this, ``event_freq`` can also be used as an async context manager, making the above code less nested:

    .. code-block::

        async with (
            move_on_when(event(widget, "<ButtonRelease>", filter=...)),
            event_freq(widget, "<Motion>") as mouse_motion,
        ):
            while True:
                e = await mouse_motion()
                ...

    .. versionadded:: 0.4.2
    '''
    def __init__(self, widget, event_name, *, filter=None):
        self.widget = widget
        self.event_name = event_name
        self.filter = filter

    def __enter__(self):
        ee = ExclusiveEvent()
        self.bind_id = self.widget.bind(self.event_name, partial(_event_callback, ee.fire, self.filter), "+")
        return ee.wait_args_0

    def __exit__(self, *args):
        self.widget.unbind(self.event_name, self.bind_id)

    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, *args):
        return self.__exit__(*args)


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

    STARTED = asyncgui.TaskState.STARTED
    last_time = get_time()
    while root_task._state is STARTED:
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
