from tkinter import Tk, Label
import asynctkinter as at

at.patch_unbind()

root = Tk()
label = Label(root, font=('', 40))
label.pack()

async def async_func(label):
    from functools import partial
    sleep = partial(at.sleep, after=label.after)
    while True:
        label['text'] = 'Press the left mouse button!!'
        await at.event(label, '<Button-1>')
        label['text'] = 'One more time'
        await at.event(label, '<Button>', filter=lambda event: event.num == 1)
        label['text'] = 'Nice!!'
        await sleep(1500)
        label['text'] = 'Press the right mouse button!!'
        await at.event(label, '<Button-3>')
        label['text'] = 'One more time'
        await at.event(label, '<Button>', filter=lambda event: event.num == 3)
        label['text'] = 'Great!!'
        await sleep(1500)

at.start(async_func(label))
root.mainloop()
