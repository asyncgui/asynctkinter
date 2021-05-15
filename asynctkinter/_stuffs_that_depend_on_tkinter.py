__all__ = (
    'patch_unbind', 'sleep', 'event', 'run_in_thread', 'run_in_executer',
)
from functools import lru_cache
from typing import Callable
import types


@types.coroutine
def sleep(duration, *, after:Callable):
    yield lambda step_coro: after(duration, step_coro)


@types.coroutine
def event(widget, name, *, filter=None):
    bind_id = None
    step_coro = None

    def bind(step_coro_):
        nonlocal bind_id, step_coro
        bind_id = widget.bind(name, callback, '+')
        step_coro = step_coro_

    def callback(*args, **kwargs):
        nonlocal bind_id
        if (filter is not None) and (not filter(*args, **kwargs)):
            return
        widget.unbind(name, bind_id)
        bind_id = None
        step_coro(*args, **kwargs)

    try:
        return (yield bind)[0][0]
    finally:
        if bind_id is not None:
            widget.unbind(name, bind_id)


async def run_in_thread(func, *, daemon=False, polling_interval=3000, after:Callable):
    from threading import Thread

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
        await sleep(polling_interval, after=after)
    if exception is not None:
        raise exception
    return return_value


async def run_in_executer(func, executer, *, polling_interval=3000, after:Callable):
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
            await sleep(polling_interval, after=after)
    except GeneratorExit:
        future.cancel()
        raise
    assert future.done()
    if exception is not None:
        raise exception
    return return_value


@lru_cache(maxsize=1)
def patch_unbind():
    from tkinter import Misc
    def _new_unbind(self, sequence, funcid=None):
        if not funcid:
            self.tk.call('bind', self._w, sequence, '')
            return
        func_callbacks = self.tk.call('bind', self._w, sequence, None).split('\n')
        new_callbacks = [l for l in func_callbacks if l[6:6 + len(funcid)] != funcid]
        self.tk.call('bind', self._w, sequence, '\n'.join(new_callbacks))
        self.deletecommand(funcid)
    Misc.unbind = _new_unbind
