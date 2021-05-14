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
        label['text'] = 'by clicking the label'
        await sleep(2500)


async def root_func(label):
    await at.or_(
        animate_label(label),
        at.event(label, '<Button>'),
    )
    label['text'] = 'Cancelled!!'


at.start(root_func(label))
root.mainloop()
