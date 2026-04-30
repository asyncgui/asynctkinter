import tkinter as tk


def second_callback(e):
    print("2nd")
    return 'break'


def main():
    root = tk.Tk()
    label = tk.Label(root, text='Suikoden 6 when?', font=('', 40))
    label.pack()
    label.bind("<ButtonPress>", lambda e: print("1st"), "+")
    label.bind("<ButtonPress>", second_callback, "+")
    label.bind("<ButtonPress>", lambda e: print("3rd"), "+")
    root.mainloop()


if __name__ == "__main__":
    main()
