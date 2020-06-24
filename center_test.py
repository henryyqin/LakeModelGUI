import tkinter as Tkinter

def __init__(self, parent=None):
        if parent is None:
            # create a new window
            parent = Tkinter.Tk()
        self.parent = parent

        # selectable: only one item
        self.listbox = Tkinter.Listbox(parent, selectmode=Tkinter.SINGLE)
        # put list into main frame, using all available space
        self.listbox.pack(anchor=Tkinter.CENTER, fill=Tkinter.BOTH)

        # lower subframe which will contain one button
        self.bottom_frame = Tkinter.Frame(parent)
        self.bottom_frame.pack(side=Tkinter.BOTTOM)

        buttonOK = Tkinter.Button(self.bottom_frame, text='OK', command=self.pressedOK)
        buttonOK.pack(side=Tkinter.LEFT, fill=Tkinter.X)
        # idea: set title to cur_disambiguation 