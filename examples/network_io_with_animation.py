import tkinter as tk
from tkinter import ttk
import requests

import asynctkinter as at
from progress_spinner import run_progress_spinner


async def main(*, clock: at.Clock, root: tk.Tk):
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

    await at.event(button, "<Button>")

    lw = 20
    async with at.run_as_daemon(
        run_progress_spinner(
            lw, lw, canvas.winfo_width() - lw, canvas.winfo_height() - lw,
            clock=clock, draw_target=canvas, line_width=lw,
        ),
    ):
        session = requests.Session()
        button['text'] = 'cancel'
        async with at.move_on_when(at.event(button, "<Button>")) as cancel_tracker:
            label['text'] = 'first request...'
            await clock.run_in_thread(
                lambda: session.get("https://httpbin.org/delay/2"),
                daemon=True,
                polling_interval=0.4,
            )
            label['text'] = 'second request...'
            await clock.run_in_thread(
                lambda: session.get("https://httpbin.org/delay/2"),
                daemon=True,
                polling_interval=0.4,
            )

    label['text'] = 'cancelled' if cancel_tracker.finished else 'all requests done'
    button['text'] = 'close'
    await at.event(button, "<Button>")
    await clock.sleep(0)
    root.destroy()


if __name__ == '__main__':
    at.run(main)
