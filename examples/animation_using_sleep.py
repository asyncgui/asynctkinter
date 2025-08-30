import tkinter as tk
import asynctkinter as atk


async def main(*, clock: atk.Clock, root: tk.Tk):
    root.title("Looping Animation")
    root.geometry('800x200')
    label = tk.Label(root, text='Hello', font=('', 80))
    label.pack(expand=True, fill='both')
    await clock.sleep(2)
    while True:
        label['text'] = 'Do'
        await clock.sleep(0.5)
        label['text'] = 'You'
        await clock.sleep(0.5)
        label['text'] = 'Like'
        await clock.sleep(0.5)
        label['text'] = 'Tkinter?'
        await clock.sleep(2)
        label['text'] = 'Answer me!'
        await clock.sleep(2)


if __name__ == "__main__":
    atk.run(main)
