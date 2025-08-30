from functools import cached_property

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import asynctkinter as atk


class App:
    async def main(self, *, clock, root):
        root.title('BMI Calculator')
        root.geometry('800x400')
        self.init_style()
        while True:
            await self.run_bmi_calculator(clock, root)

    async def run_bmi_calculator(self, clock: atk.Clock, root: tk.Tk):
        scene = self.title_scene
        scene.pack(in_=root, expand=True, fill='both')
        await atk.event(scene.children['start_button'], '<Button>')
        scene.pack_forget()

        scene = self.input_scene
        scene.pack(in_=root, expand=True, fill='both')
        weight = await scene.ask_input('Input your weight in kilograms')
        height = await scene.ask_input('Input your height in meters')
        scene.pack_forget()

        bmi = weight / (height * height)
        if bmi < 18.5:
            result = 'too skinny'
        elif bmi < 25.0:
            result = 'healthy'
        else:
            result = 'too fat'

        scene = self.result_scene
        scene.pack(in_=root, expand=True, fill='both')
        scene.children['top_label']['text'] = f'Your BMI is {bmi:.2f}\nYou are'
        scene.children['bottom_label']['text'] = result
        await atk.wait_any(clock.sleep(3), atk.event(root, '<Button>'))
        scene.children['top_label']['text'] = ''
        scene.children['bottom_label']['text'] = 'bye'
        await atk.wait_any(clock.sleep(3), atk.event(root, '<Button>'))
        scene.pack_forget()

    def init_style(self):
        style = ttk.Style()
        style.configure('TButton', font=(None, 30))
        style.configure('TLabel', font=(None, 30))
        style.configure('TEntry', font=(None, 30))
        style.configure('H1.TLabel', font=(None, 50, 'bold'))

    @cached_property
    def title_scene(self) -> ttk.Frame:
        scene = ttk.Frame()
        label = ttk.Label(scene, text='BMI Calculator', style='H1.TLabel')
        label.pack(expand=True)
        button = ttk.Button(scene, text='Start', name='start_button')
        button.pack(expand=True)
        return scene

    @cached_property
    def input_scene(self) -> ttk.Frame:
        scene = ttk.Frame()
        label = ttk.Label(scene)
        label.pack(expand=True)
        entry = ttk.Entry(scene)
        # FIXME: 'TEntry' style doesn't seem to work so set the font here.
        entry.configure(font=(None, 30))
        entry.pack(expand=True, fill='x', padx=20, pady=40)

        async def ask_input(msg):
            label['text'] = msg
            entry.delete(0, tk.END)
            entry.focus()
            while True:
                await atk.event(entry, '<Return>')
                text = entry.get()
                try:
                    value = float(text)
                    if value <= 0:
                        raise ValueError
                except ValueError:
                    messagebox.showerror('Error', 'The value must be a positive number.')
                    continue
                break
            return value

        scene.ask_input = ask_input
        return scene

    @cached_property
    def result_scene(self) -> ttk.Frame:
        scene = ttk.Frame()
        label = ttk.Label(scene, name='top_label', justify='center')
        label.pack(pady=20)
        label = ttk.Label(scene, name='bottom_label', style='H1.TLabel')
        label.pack(expand=True)
        return scene


if __name__ == '__main__':
    atk.run(App().main)
