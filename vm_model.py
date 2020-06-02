import tkinter as tk  # python 3
from tkinter import font  as tkfont  # python 3
from os.path import basename
import tkinter.filedialog as fd
import subprocess

"""
if you want the user to upload something from the same directory as the gui
then you can use initialdir=os.getcwd() as the first parameter of askopenfilename
"""
LARGE_FONT = ("Verdana", 16)


class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Verdana', size=18, weight="bold")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is the start page", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Run Lake Model",
                            command=lambda: controller.show_frame("PageOne"))
        button2 = tk.Button(self, text="Go to Page Two",
                            command=lambda: controller.show_frame("PageTwo"))
        button1.pack()
        button2.pack()


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        rowIdx = 1
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="(This is page 1) Upload or modify .txt and .inc files", font=controller.title_font)
        label.grid(row=rowIdx, columnspan=3, rowspan=3, pady=15)

        rowIdx += 3

        # Label for uploading .txt and .inc files
        tk.Label(self,
                 text="(SUBTITLE- can include instructions on using sample files) Upload a .txt and .inc file."
                 ).grid(row=rowIdx, columnspan=3, rowspan=3, pady=15)
        rowIdx += 3

        # Allows user to upload .txt data.
        tk.Label(self, text="Click to upload your .txt file:").grid(
            row=rowIdx, column=0, pady=10, sticky="W")
        graphButton = tk.Button(self, text="Upload .txt File",
                                command=self.uploadTxt)
        graphButton.grid(row=rowIdx, column=1, pady=10, ipadx=30, ipady=3, sticky="W")
        rowIdx += 1

        # Shows the name of the current uploaded file, if any.
        tk.Label(self, text="Current File Uploaded:").grid(
            row=rowIdx, column=0, sticky="W")
        self.currentTxtFileLabel = tk.Label(self, text="No file")
        self.currentTxtFileLabel.grid(
            row=rowIdx, column=1, columnspan=2, pady=10, sticky="W")
        rowIdx += 3

        # Allows user to upload .inc data.

        tk.Label(self, text="Click to upload your .inc file:").grid(
            row=rowIdx, column=0, sticky="W")
        graphButton = tk.Button(self, text="Upload .inc File",
                                command=self.uploadInc)
        graphButton.grid(row=rowIdx, column=1, pady=10, ipadx=30, ipady=3, sticky="W")
        rowIdx += 1

        # Shows the name of the current uploaded file, if any.
        tk.Label(self, text="Current File Uploaded:").grid(
            row=rowIdx, column=0, sticky="W")
        self.currentIncFileLabel = tk.Label(self, text="No file")
        self.currentIncFileLabel.grid(
            row=rowIdx, column=1, columnspan=2, pady=10, sticky="W")
        rowIdx += 1

        # Return to Start Page
        homeButton = tk.Button(self, text="Back to start page",
                               command=lambda: controller.show_frame("StartPage"))
        # previousPageB.pack(anchor = "w", side = "bottom")
        homeButton.grid(row=rowIdx, column=3, ipadx=25, ipady=3, pady=30, sticky="W")
        rowIdx += 1

    """
    Takes a .txt file
    """

    def uploadTxt(self):
        # Open the file choosen by the user
        txtfilename = fd.askopenfilename(filetypes=(('text files', 'txt'),))
        self.currentTxtFileLabel.configure(text=basename(txtfilename))
        print(txtfilename)

    """
    Takes a .inc file
    """

    def uploadInc(self):
        # Open the file choosen by the user
        incfilename = fd.askopenfilename(filetypes=(('include files', 'inc'),))
        self.currentIncFileLabel.configure(text=basename(incfilename))
        print(incfilename)


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is page 2", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()
        button_lakemodel = tk.Button(self, text="Run lake model",
                                command=self.run_lakemodel)
        button_lakemodel.pack()
    def run_lakemodel(self):
        subprocess.run(["f2py","-c","-m","lakepsm","lake_environment.f90"])
        import lakepsm
        lakepsm.lakemodel()

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
