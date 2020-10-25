from tkinter import Tk, Label
import asynctkinter as at

at.patch_unbind()

root = Tk()
label = Label(root, text='Hello', font=('', 80))
label.pack()

async def animate_label(label):
    from functools import partial
    sleep = partial(at.sleep, after=label.after)
    await sleep(2000)
    while True:
        label['text'] = 'Do'
        await sleep(500)
        label['text'] = 'You'
        await sleep(500)
        label['text'] = 'Like'
        await sleep(500)
        label['text'] = 'Tkinter?'
        await sleep(2000)
        label['text'] = 'Answer me!'
        await sleep(2000)


at.start(animate_label(label))
root.mainloop()
