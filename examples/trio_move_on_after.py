from functools import partial
import tkinter as tk
import asynctkinter as at


def move_on_after(after, timeout):
    '''
    https://trio.readthedocs.io/en/stable/reference-core.html#trio.move_on_after
    '''
    return at.wait_any_cm(at.sleep(after, timeout))


def main():
    at.install()
    root = tk.Tk()
    at.start(async_main(root))
    root.mainloop()


async def async_main(root):
    sleep = partial(at.sleep, root.after)

    label = tk.Label(root, font=('', 80))
    label.pack()
    await sleep(1400)
    async with move_on_after(root.after, 3000):
        while True:
            label['text'] = 'A'
            await sleep(300)
            label['text'] = 'B'
            await sleep(300)
            label['text'] = 'C'
            await sleep(300)
    label['text'] = 'DONE'


if __name__ == "__main__":
    main()
