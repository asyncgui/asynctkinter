import tkinter as tk
import asynctkinter as atk


async def main(*, clock: atk.Clock, root: tk.Tk):
    root.title("Filtering Event")
    root.geometry('900x400')
    label = tk.Label(root, font=('', 40))
    label.pack(expand=True, fill='both')
    while True:
        label['text'] = 'Press the left mouse button!!'
        await atk.event(label, '<Button-1>')
        label['text'] = 'One more time'
        await atk.event(label, '<Button>', filter=lambda e: e.num == 1)
        label['text'] = 'Nice!!'

        await clock.sleep(1.5)

        label['text'] = 'Press the right mouse button!!'
        await atk.event(label, '<Button-3>')
        label['text'] = 'One more time'
        await atk.event(label, '<Button>', filter=lambda e: e.num == 3)
        label['text'] = 'Great!!'

        await clock.sleep(1.5)


if __name__ == "__main__":
    atk.run(main)
