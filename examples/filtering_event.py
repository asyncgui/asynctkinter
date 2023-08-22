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
    label = tk.Label(root, font=('', 40))
    label.pack()
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


if __name__ == "__main__":
    main()
