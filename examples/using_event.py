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
        label['text'] = 'Click anywhere!'
        event = await at.event(label, '<Button>')
        label['text'] = f'You clicked at pos({event.x}, {event.y})'
        await sleep(1500)


if __name__ == "__main__":
    main()
