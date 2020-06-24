import tkinter as tk


win = tk.Tk()
var = tk.StringVar()

var_entry = tk.Entry(win, textvariable=var)
var_entry.grid(row=1, column=2)

tk.Button(win, text='1', command=lambda: var.set(4)).grid(row=2, column=0)

win.mainloop()