__all__ = (
    'event', 'run', 'install',
)
from functools import lru_cache
import typing as T

import tkinter
from asyncgui import AsyncEvent


async def event(widget, sequence, *, filter=None) -> T.Awaitable[tkinter.Event]:
    ae = AsyncEvent()
    bind_id = widget.bind(
        sequence,
        lambda e, ae=ae, filter=filter: ae.fire(e) if (filter is None or filter(e)) else None,
        '+',
    )
    try:
        return (await ae.wait())[0][0]
    finally:
        widget.unbind(sequence, bind_id)


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


def run(async_fn, *, fps=20, root=None):
    from time import sleep, perf_counter as get_time
    from tkinter import TclError
    import asyncgui
    from asyncgui_ext.clock import Clock

    install()
    max_ = max
    root = tkinter.Tk() if root is None else root
    clock = Clock()

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
