import tkinter as tk  # python 3
from tkinter import font  as tkfont  # python 3
from os.path import basename
import tkinter.filedialog as fd
import subprocess
import webbrowser
from tkinter import ttk

"""
if you want the user to upload something from the same directory as the gui
then you can use initialdir=os.getcwd() as the first parameter of askopenfilename
"""
LARGE_FONT = ("Verdana", 16)

def callback(url):
    webbrowser.open_new(url)

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
        label = tk.Label(self, text="PRYSM Models", font=("Verdana", 40))
        label.pack(pady=(200, 10), padx=10)

        descrip = tk.Label(self, text="A graphical user interface for Climate Proxy System Modeling Tools in Python",
                           font=("Helvetica", 18))
        descrip.pack(pady=10, padx=10)

        authors = tk.Label(self, text="By: Sylvia Dee, Henry Qin, Xueyan Mu, and Vinay Tummarakota",
                           font=("Helvetica", 18))
        authors.pack(pady=10, padx=10)

        website = tk.Label(self, text="Getting Started Guide", fg="blue", cursor="hand2", font=("Helvetica", 18))
        website.pack(pady=10, padx=10)
        website.bind("<Button-1>", lambda e: callback("https://docs.google.com/document/d/1RHYEXm5AjXO3NppNxDLPmPnHPr8tQIaT_jH7F7pU2ic/edit?usp=sharing"))

        github = tk.Label(self, text="Github", fg="blue", cursor="hand2", font=("Helvetica", 18))
        github.pack(pady=10, padx=10)
        github.bind("<Button-1>", lambda e: callback("https://github.com/henryyqin/LakeModelGUI"))

        button = ttk.Button(self, text="PageOne", command=lambda: controller.show_frame("PageOne"))
        button.pack(ipadx=43, ipady=3, pady=(40, 5))

        button2 = ttk.Button(self, text="PageTwo", command=lambda: controller.show_frame("PageTwo"))
        button2.pack(ipadx=30, ipady=3, pady=(5, 5))


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

        #Entries for .inc file
        parameters = ["obliquity", "latitude (negative for South)", "longitude (negative for West)",
                           "local time relative to gmt in hours", "depth of lake at sill in meters",
                           "Elevation of Basin Bottom in Meters", "Area of Catchment+Lake in Hectares",
                           "neutral drag coefficient 1.8 HAD 1.7GISS 1.2CCSM", "shortwave extinction coefficient (1/m)",
                           "fraction of advected air over lake", "albedo of melting snow", "albedo of non-melting snow",
                           "prescribed depth in meters", "prescribed salinity in ppt", "d18O of air above lake",
                           "dD of air above lake", "number of years for spinup",
                           "true for explict boundry layer computations; presently only for sigma coord climate models",
                           "sigma level for boundary flag", "true for variable lake depth", "true for variable ice cover",
                           "true for variable salinity", "true for variable d18O", "true for variable dD",
                           "height of met inputs"]
        param_values = []
        for i in range(rowIdx,rowIdx+25):
            tk.Label(self, text=parameters[i-rowIdx]).grid(
                row=i, column=0, sticky="W")
            p = tk.Entry(self)
            p.grid(row=i, column=1, sticky="W")
            param_values.append(p)

        rowIdx+=25

        #Submit entries for .inc file
        submitButton = tk.Button(self, text="Submit Parameters",
                                 command=lambda: self.editInc([p.get() for p in param_values], parameters))
        submitButton.grid(row=rowIdx, column=1, pady=10, ipadx=30, ipady=3, sticky="W")

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

    """
    Edits the parameters in the .inc file
    """

    def editInc(self, parameters, comments):
        with open("Tanganyika.inc", "r+") as f:
            new = f.readlines()
            #names of the parameters that need to be modified
            names = ["oblq","xlat","xlon","gmt","max_dep","basedep","b_area","cdrn","eta","f","alb_slush",
                           "alb_snow", "depth_begin", "salty_begin", "o18air", "deutair", "nspin", "bndry_flag",
                           "sigma","wb_flag","iceflag","s_flag","o18flag","deutflag","z_screen"]
            #line numbers in the .inc file that need to be modified
            rows = [28,29,30,31,32,33,34,35,36,37,38,39,41,42,44,45,69,70,71,72,73,74,75,76,77]
            for i in range(0, len(parameters)):
                if len(parameters[i]) != 0:
                    new[rows[i]] = "    parameter ("+names[i]+" = "+parameters[i]+")   ! "+comments[i]+"\n"
            f.seek(0)
            f.truncate()
            f.writelines(new)
            f.close()


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
