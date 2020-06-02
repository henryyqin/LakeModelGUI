import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fd
import numpy as np
import os
from os.path import basename
from math import pi, sqrt, exp


import matplotlib
matplotlib.use("TkAgg")

import subprocess

LARGE_FONT = ("Verdana", 16)

class Page(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        frame = StartPage(container, self)

        self.frames[StartPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)

        rowIdx = 1
        filename = ''

        # Allows user to upload a .txt file.
        tk.Label(self,
                 text="Upload a .txt file."
                 ).grid(row=rowIdx, columnspan=3, rowspan=3)
        rowIdx += 3
        tk.Label(self, text="Click to upload your file:").grid(
            row=rowIdx, column=0, sticky="E")
        uploadButton = tk.Button(self, text="Upload .txt File",
                                 command=self.uploadTxt)
        uploadButton.grid(row=rowIdx, column=1, ipadx=30, ipady=3, sticky="W")
        rowIdx += 1

        # Shows the name of the current uploaded file, if any.
        tk.Label(self, text="Current .txt File Uploaded:").grid(
            row=rowIdx, column=0, sticky="E")
        self.currentTxtFileLabel = tk.Label(self, text="No file")
        self.currentTxtFileLabel.grid(
            row=rowIdx, column=1, columnspan=2, sticky="W")
        rowIdx += 1

        # Allows user to upload a .inc file.
        tk.Label(self,
                 text="Upload a .inc file."
                 ).grid(row=rowIdx, columnspan=3, rowspan=3)
        rowIdx += 3
        tk.Label(self, text="Click to upload your file:").grid(
            row=rowIdx, column=0, sticky="E")
        uploadButton = tk.Button(self, text="Upload .inc File",
                                 command=self.uploadInc)
        uploadButton.grid(row=rowIdx, column=1, ipadx=30, ipady=3, sticky="W")
        rowIdx += 1

        # Shows the name of the current uploaded file, if any.
        tk.Label(self, text="Current .inc File Uploaded:").grid(
            row=rowIdx, column=0, sticky="E")
        self.currentIncFileLabel = tk.Label(self, text="No file")
        self.currentIncFileLabel.grid(
            row=rowIdx, column=1, columnspan=2, sticky="W")
        rowIdx += 1

        # Allows user to edit .inc file (Mac only)
        editButton = tk.Button(
            self, text="Edit .inc File", command=self.editText)
        editButton.grid(row=rowIdx, column=1, ipadx=30, ipady=3, sticky="W")
        rowIdx += 1

        # Button to run the model (Mac only)
        runButton = tk.Button(
            self, text="Run Model", command=self.runModel)
        runButton.grid(row=rowIdx, column=1, ipadx=30, ipady=3, sticky="W")
        rowIdx += 1

    """
    The user will choose a .inc file from the same directory as the GUI.
    It is assumed that Tanganyka.inc and Malawi.inc will be downloaded with the GUI.
    """

    def uploadTxt(self):
        # Open the file choosen by the user
        self.txtfilename = fd.askopenfilename(
            initialdir=os.getcwd(), filetypes=(('include files', 'txt'),))
        self.currentTxtFileLabel.configure(text=basename(self.txtfilename))

    def uploadInc(self):
        # Open the file choosen by the user
        self.incfilename = fd.askopenfilename(
            initialdir=os.getcwd(), filetypes=(('include files', 'inc'),))
        self.currentIncFileLabel.configure(text=basename(self.incfilename))

    def editText(self):
        # Edit the .inc file that was chosen by the user
        if self.incfilename == '':
            return

        # For Windows
        # subprocess.Popen([notepad, self.filename])

        # For Mac
        subprocess.call(['open', '-a', 'TextEdit', self.incfilename])

    def runModel(self):
        # For Mac
        # Runs f2py terminal command then (hopefully) terminates (takes a bit)
        subprocess.call(
            ['f2py', '-c', '-m', 'lakepsm', 'lake_environment.f90'])

        # imports the wrapper
        import lakepsm

        # defines the input file (idk if necessary at this step)
        lake_data_file = self.txtfilename

        # Run Environment Model
        lakepsm.lakemodel()
        print('Success!')


app = Page()
app.mainloop()
