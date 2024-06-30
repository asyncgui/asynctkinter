import tkinter as tk
import asynctkinter as at


async def run_progress_spinner(x1, y1, x2, y2, *, clock: at.Clock, draw_target: tk.Canvas, line_color='black', line_width=10):
    start = 70
    extent = 20
    arc = draw_target.create_arc(
        x1, y1, x2, y2,
        outline=line_color, width=line_width, start=start, extent=extent, style='arc',
    )

    try:
        while True:
            prev_v = 0
            async for dt, __, p in clock.anim_with_dt_et_ratio(duration=0.7):
                p = min(p, 1.0)
                v = p * p * 320
                diff = v - prev_v
                extent += diff
                start -= diff
                start -= dt * 30
                draw_target.itemconfig(arc, start=start, extent=extent)
                prev_v = v
            async for dt, et in clock.anim_with_dt_et():
                start -= dt * 30
                draw_target.itemconfig(arc, start=start)
                if et >= 0.2:
                    break
            prev_v = 0
            async for dt, __, p in clock.anim_with_dt_et_ratio(duration=0.7):
                p = min(p, 1.0)
                v = p * p * 320
                diff = v - prev_v
                extent -= diff
                start -= dt * 30
                draw_target.itemconfig(arc, start=start, extent=extent)
                prev_v = v
            async for dt, et in clock.anim_with_dt_et():
                start -= dt * 30
                draw_target.itemconfig(arc, start=start)
                if et >= 0.2:
                    break
    finally:
        draw_target.delete(arc)


async def main(*, clock: at.Clock, root: tk.Tk):
    root.title("Progress Spinner")
    root.geometry('800x800')
    canvas = tk.Canvas(root, bg='white')
    canvas.pack(expand=True, fill='both')

    lw = 30
    await run_progress_spinner(
        lw, lw, 800 - lw, 800 - lw,
        clock=clock, draw_target=canvas, line_width=lw)


if __name__ == '__main__':
    at.run(main)
