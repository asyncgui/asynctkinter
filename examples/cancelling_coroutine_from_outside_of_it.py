from tkinter import Tk, Label
import asynctkinter as at

at.patch_unbind()

root = Tk()
label = Label(root, text='Hello', font=('', 40))
label.pack()

async def animate_label(label):
    from functools import partial
    sleep = partial(at.sleep, after=label.after)
    await sleep(1500)
    while True:
        label['text'] = 'This animation'
        await sleep(1500)
        label['text'] = 'can be cancelled anytime'
        await sleep(2000)
        label['text'] = 'by clicking the window'
        await sleep(2500)


coro = animate_label(label)


def on_click(event):
    coro.close()
    label['text'] = 'Cancelled!!'


label.bind('<Button>', on_click)
at.start(coro)
root.mainloop()
