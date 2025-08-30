import tkinter as tk
import requests

import asynctkinter as atk


async def main(*, clock: atk.Clock, root: tk.Tk):
    root.title("HTTP Request")
    root.geometry('1000x400')
    label = tk.Label(root, text='Press to start a HTTP request', font=('', 40))
    label.pack(expand=True)
    await atk.event(label, '<Button>')
    label['text'] = 'waiting for the server to respond...'
    res = await atk.run_in_thread(
        clock,
        lambda: requests.get("https://httpbin.org/delay/2"),
        daemon=True,
        polling_interval=0.2,
    )
    label['text'] = res.json()['headers']['User-Agent']


if __name__ == '__main__':
    atk.run(main)
