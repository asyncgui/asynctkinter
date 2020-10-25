from tkinter import Tk, Label
import asynctkinter as at

at.patch_unbind()

root = Tk()
label = Label(root, font=('', 40))
label.pack()

async def async_func(label):
    while True:
        label['text'] = 'Click anywhere!'
        event = await at.event(label, '<Button>')
        label['text'] = f'You clicked at ({event.x}, {event.y})'
        await at.sleep(1500, after=label.after)

at.start(async_func(label))
root.mainloop()
