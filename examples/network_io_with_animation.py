'''
asyncgui 0.11.1 or later is required to run this example.
'''

import tkinter as tk
from tkinter import ttk
import requests

import asynctkinter as atk
from progress_spinner import run_progress_spinner


async def main(*, clock: atk.Clock, root: tk.Tk):
    root.title("HTTP request + loading animation")
    root.geometry('720x480')
    bg = root.cget("bg")

    style = ttk.Style()
    style.configure('TButton', font=(None, 30))
    style.configure('TLabel', font=(None, 30), background=bg)

    label = ttk.Label(root, text='HTTP requests')
    label.pack(pady=20)
    button = ttk.Button(root, text='start')
    button.pack(pady=20, side='bottom')
    canvas = tk.Canvas(root, bg=bg, height=200, width=200)
    canvas.pack(expand=True)

    await atk.event(button, "<ButtonPress>")

    async with atk.open_nursery() as nursery:
        cancel_tracker = nursery.start(atk.event(button, "<ButtonPress>"), daemon=True, close_on_finish=True)
        lw = 20  # line width
        nursery.start(run_progress_spinner(
            lw, lw, canvas.winfo_width() - lw, canvas.winfo_height() - lw,
            clock=clock, draw_target=canvas, line_width=lw,
        ), daemon=True)
        button["text"] = "cancel"
        with requests.Session() as session:
            label["text"] = "first request..."
            await atk.run_in_thread(
                clock,
                lambda: session.get("https://httpbin.org/delay/2"),
                daemon=True,
                polling_interval=0.4,
            )
            label['text'] = 'second request...'
            await atk.run_in_thread(
                clock,
                lambda: session.get("https://httpbin.org/delay/2"),
                daemon=True,
                polling_interval=0.4,
            )

    label["text"] = "cancelled" if cancel_tracker.finished else "all requests done"
    button["text"] = "close"
    await atk.event(button, "<ButtonPress>")
    await clock.sleep(0)
    root.destroy()


if __name__ == '__main__':
    atk.run(main)
