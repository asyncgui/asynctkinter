from functools import partial
import tkinter as tk
import asynctkinter as at


def main():
    at.install()
    root = tk.Tk()
    at.start(async_main(root))
    root.mainloop()


async def async_main(root):
    sleep = partial(at.sleep, root.after)

    label = tk.Label(root, text='Hello', font=('', 80))
    label.pack()
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


if __name__ == "__main__":
    main()
