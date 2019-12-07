__version__ = '0.0.1'
__all__ = ('patch_unbind', 'start', 'sleep', 'event', 'thread', )

import types
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
