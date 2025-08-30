import itertools

import tkinter as tk
import asynctkinter as atk


async def run_progress_spinner(
        x1, y1, x2, y2, *, clock: atk.Clock, draw_target: tk.Canvas, line_color='black', line_width=10,
        min_arc_angle=15, speed=1.0):
    MA = min_arc_angle
    BS = 20  # base speed
    get_next_start = itertools.accumulate(itertools.cycle((BS, BS, BS + 360 - MA - MA,  BS, )), initial=90).__next__
    get_next_extent = itertools.cycle((MA, 360 - MA, 360 - MA, MA, )).__next__
    start = get_next_start()
    extent = get_next_extent()

    arc = draw_target.create_arc(
        x1, y1, x2, y2,
        outline=line_color, width=line_width, start=start, extent=extent, style='arc',
    )
    try:
        d = 0.5 / speed
        while True:
            next_start = get_next_start()
            next_extent = get_next_extent()
            async for s, e in clock.interpolate_seq((start, extent), (next_start, next_extent), duration=d):
                draw_target.itemconfig(arc, start=s, extent=e)
            start = next_start
            extent = next_extent
    finally:
        draw_target.delete(arc)


async def main(*, clock: atk.Clock, root: tk.Tk):
    root.title("Progress Spinner")
    root.geometry('800x800')
    canvas = tk.Canvas(root, bg='white')
    canvas.pack(expand=True, fill='both')

    lw = 30
    await run_progress_spinner(
        lw, lw, 800 - lw, 800 - lw,
        clock=clock, draw_target=canvas, line_width=lw)


if __name__ == '__main__':
    atk.run(main)
