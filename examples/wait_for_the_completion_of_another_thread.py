from tkinter import Tk, Label
import asynctkinter as at
at.patch_unbind()

def heavy_task():
    import time
    for i in range(5):
        time.sleep(1)
        print('heavy task:', i)
    return 'done'

root = Tk()
label = Label(root, text='Hello', font=('', 60))
label.pack()

async def some_task(label):
    label['text'] = 'start heavy task'
    event = await at.event(label, '<Button>')
    label['text'] = 'running...'
    result = await at.run_in_thread(heavy_task, after=label.after)
    label['text'] = result
    await at.sleep(2000, after=label.after)
    label['text'] = 'close the window'


at.start(some_task(label))
root.mainloop()
