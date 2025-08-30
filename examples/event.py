import tkinter as tk
import asynctkinter as atk


async def main(*, clock: atk.Clock, root: tk.Tk):
    root.title("Event")
    root.geometry('800x400')
    label = tk.Label(root, font=('', 40))
    label.pack(expand=True, fill='both')
    while True:
        label['text'] = 'Click anywhere!'
        e = await atk.event(label, '<Button>')
        label['text'] = f'You clicked at pos ({e.x}, {e.y})'
        await clock.sleep(1.5)


if __name__ == "__main__":
    atk.run(main)
