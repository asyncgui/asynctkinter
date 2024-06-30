'''
* Same as painter1.py except this one can handle multiple mouse buttons simultaneously.
'''

import tkinter as tk
import asynctkinter as at

from painter1 import draw_oval, draw_rect


async def main(*, clock: at.Clock, root: tk.Tk):
    root.title("Painter")
    root.geometry('800x800')
    canvas = tk.Canvas(root, bg='white')
    canvas.pack(expand=True, fill='both')

    button2command = {
        1: draw_rect,
        3: draw_oval,
    }
    async with at.open_nursery() as nursery:
        while True:
            e_press = await at.event(canvas, '<Button>')
            command = button2command.get(e_press.num)
            if command is not None:
                nursery.start(command(canvas, e_press))


if __name__ == '__main__':
    at.run(main)
