from tkinter import Tk, Label
import asynctkinter as at

at.patch_unbind()

root = Tk()
label = Label(root, font=('', 40))
label.pack()

async def async_func(label):
    while True:
        label['text'] = 'Press the left mouse button!!'
        event = await at.event(label, '<Button>', filter=lambda event: event.num == 1)
        label['text'] = 'Nice!!'
        await at.sleep(label, 1500)
        label['text'] = 'Press the right mouse button!!'
        event = await at.event(label, '<Button>', filter=lambda event: event.num == 3)
        label['text'] = 'Great!!'
        await at.sleep(label, 1500)

at.start(async_func(label))
root.mainloop()
