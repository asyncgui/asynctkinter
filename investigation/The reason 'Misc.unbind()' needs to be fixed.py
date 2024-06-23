'''
https://stackoverflow.com/questions/6433369/deleting-and-changing-a-tkinter-event-binding

The code will work if you 'asynctkinter.install()'. 
'''

import tkinter as tk
# import asynctkinter
# asynctkinter.install()


def main():
    root = tk.Tk()
    label = tk.Label(root, text='Suikoden 6 when?', font=('', 40))
    label.pack()
    label.bind('<Button>', lambda e: print('1st'), '+')
    bind_id = label.bind('<Button>', lambda e: print('2nd'), '+')
    label.bind('<Button>', lambda e: print('3rd'), '+')
    label.unbind('<Button>', bind_id)
    root.mainloop()


if __name__ == "__main__":
    main()
