import tkinter as tk
import requests

import asynctkinter as at


async def main(*, clock: at.Clock, root: tk.Tk):
    root.title("HTTP Request")
    root.geometry('1000x400')
    label = tk.Label(root, text='Press to start a HTTP request', font=('', 40))
    label.pack(expand=True)
    await at.event(label, '<Button>')
    label['text'] = 'waiting for the server to respond...'
    res = await clock.run_in_thread(
        lambda: requests.get("https://httpbin.org/delay/2"),
        daemon=True,
        polling_interval=0.2,
    )
    label['text'] = res.json()['headers']['User-Agent']


if __name__ == '__main__':
    at.run(main)
