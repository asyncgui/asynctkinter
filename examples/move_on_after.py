import tkinter as tk
import asynctkinter as atk


async def main(*, clock: atk.Clock, root: tk.Tk):
    root.title("Appying a time limit to a code block")
    root.geometry('400x400')
    label = tk.Label(root, font=('', 80))
    label.pack(expand=True, fill='both')
    await clock.sleep(1.0)
    async with clock.move_on_after(3):
        while True:
            label['text'] = 'A'
            await clock.sleep(0.3)
            label['text'] = 'B'
            await clock.sleep(0.3)
            label['text'] = 'C'
            await clock.sleep(0.3)
    label['text'] = 'DONE'


if __name__ == "__main__":
    atk.run(main)
