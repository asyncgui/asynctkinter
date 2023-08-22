from functools import partial
import tkinter as tk
import asynctkinter as at


def main():
    at.install()
    root = tk.Tk()
    at.start(async_main(root))
    root.mainloop()


def heavy_task():
    import time
    for i in range(5):
        time.sleep(1)
        print('heavy task:', i)
    return 'done'


async def async_main(root):
    sleep = partial(at.sleep, root.after)
    label = tk.Label(root, text='Hello', font=('', 60))
    label.pack()
    label['text'] = 'start heavy task'
    await at.event(label, '<Button>')
    label['text'] = 'running...'
    result = await at.run_in_thread(heavy_task, after=root.after)
    label['text'] = result
    await sleep(2000)
    label['text'] = 'close the window'


if __name__ == '__main__':
    main()
