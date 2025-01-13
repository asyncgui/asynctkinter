'''
* Press mouse button 1 to draw a rectangle.
* Press mouse button 3 to draw an oval.
'''

import tkinter as tk
import asynctkinter as at


async def main(*, clock: at.Clock, root: tk.Tk):
    root.title("Painter")
    root.geometry('800x800')
    canvas = tk.Canvas(root, bg='white')
    canvas.pack(expand=True, fill='both')

    button2command = {
        1: draw_rect,
        3: draw_oval,
    }
    while True:
        e_press = await at.event(canvas, '<Button>')
        command = button2command.get(e_press.num)
        if command is not None:
            await command(canvas, e_press)


async def draw_rect(canvas: tk.Canvas, e_press: tk.Event):
    ox, oy = e_press.x, e_press.y
    rect = canvas.create_rectangle(ox, oy, ox, oy, outline='orange', width=3)
    async with (
        at.move_on_when(at.event(canvas, '<ButtonRelease>', filter=lambda e: e.num == e_press.num)),
        at.event_freq(canvas, '<Motion>') as mouse_motion,
    ):
        while True:
            e = await mouse_motion()
            canvas.coords(rect, ox, oy, e.x, e.y)


async def draw_oval(canvas: tk.Canvas, e_press: tk.Event):
    ox, oy = e_press.x, e_press.y
    oval = canvas.create_oval(ox, oy, ox, oy, outline='blue', width=3)
    bbox = canvas.create_rectangle(ox, oy, ox, oy, outline='black', dash=(3, 3))
    async with (
        at.move_on_when(at.event(canvas, '<ButtonRelease>', filter=lambda e: e.num == e_press.num)),
        at.event_freq(canvas, '<Motion>') as mouse_motion,
    ):
        while True:
            e = await mouse_motion()
            canvas.coords(oval, ox, oy, e.x, e.y)
            canvas.coords(bbox, ox, oy, e.x, e.y)
    canvas.delete(bbox)


if __name__ == '__main__':
    at.run(main)
