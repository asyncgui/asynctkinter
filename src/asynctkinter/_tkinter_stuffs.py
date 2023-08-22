__all__ = (
    'install', 'sleep', 'event', 'run_in_thread', 'run_in_executer',
)
from functools import lru_cache
import typing as T
import types
from threading import Thread

import tkinter
from asyncgui import Cancelled, IBox


@types.coroutine
def sleep(after: T.Callable, duration) -> T.Awaitable:
    bind_id = None

    def _sleep(task):
        nonlocal bind_id
        bind_id = after(duration, task._step)

    try:
        yield _sleep
    except Cancelled:
        after.__self__.after_cancel(bind_id)
        raise


async def event(widget, sequence, *, filter=None) -> T.Awaitable[tkinter.Event]:
    box = IBox()
    bind_id = widget.bind(
        sequence,
        lambda e, box=box, filter=filter: box.put(e) if (filter is None or filter(e)) else None,
        '+',
    )
    try:
        return (await box.get())[0][0]
    finally:
        widget.unbind(sequence, bind_id)


async def run_in_thread(func, *, daemon=None, polling_interval=3000, after: T.Callable) -> T.Awaitable:
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

    Thread(target=wrapper, daemon=daemon).start()
    while not done:
        await sleep(after, polling_interval)
    if exception is not None:
        raise exception
    return return_value


async def run_in_executer(executer, func, *, polling_interval=3000, after: T.Callable) -> T.Awaitable:
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
        while not done:
            await sleep(after, polling_interval)
    except Cancelled:
        future.cancel()
        raise
    if exception is not None:
        raise exception
    return return_value


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
