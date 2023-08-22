'''
I'm not even a tkinter user so the code probably is impractical.
'''
import tkinter as tk
import asynctkinter as at


def main():
    at.install()
    root = tk.Tk()
    at.start(async_main(root))
    root.mainloop()


async def async_main(root: tk.Tk):
    from tkinter.font import Font

    font = Font(size=50)
    frame = tk.Frame(root)
    frame.pack()

    # title
    label = tk.Label(frame, text='BMI Calculator', font=font)
    label.pack(padx=10, pady=10)
    await at.sleep(label.after, 2000)

    # ask weight
    label['text'] = 'Input your weight'
    # label.pack(padx=10, pady=10)
    child_frame = tk.Frame()
    child_frame.pack()
    entry = tk.Entry(child_frame, bg='white', font=font)
    entry.pack(side='left', padx=10, pady=10)
    label2 = tk.Label(child_frame, text='kg', font=font)
    label2.pack(padx=10, pady=10)
    ok_button = tk.Button(frame, text='ok', font=font)
    ok_button.pack()
    weight = None
    while weight is None:
        await at.event(ok_button, '<Button>')
        text = entry.get()
        if not text:
            continue
        try:
            weight = float(text)
        except ValueError:
            pass
    print(f'weight: {weight}kg')

    # ask height
    label['text'] = 'Input your height'
    entry.delete(0, tk.END)
    label2['text'] = 'm'
    height = None
    while height is None:
        await at.event(ok_button, '<Button>')
        text = entry.get()
        if not text:
            continue
        try:
            height = float(text)
        except ValueError:
            pass
    print(f'height: {height}m')

    # show result
    bmi = weight / (height * height)
    print(f'BMI指数: {bmi}')
    if bmi < 18.5:
        bmi_class = 'too skinny'
    elif bmi < 25.0:
        bmi_class = 'healthy'
    else:
        bmi_class = 'too fat'
    label['text'] = f'You are {bmi_class}.'
    child_frame.destroy()
    ok_button.destroy()
    await at.sleep(label.after, 2000)


if __name__ == '__main__':
    main()
